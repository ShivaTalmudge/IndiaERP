from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile

class CompanyContextMiddleware(MiddlewareMixin):
    """
    Middleware to attach 'profile', 'company', and 'user_role' to the request object.
    This ensures data isolation and easy access to user context throughout the application.
    """
    def process_request(self, request):
        request.company = None
        request.user_role = None
        request.profile = None
        
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                request.profile = profile
                request.user_role = profile.role

                # Superadmin and Platform Owner context logic
                if profile.role == 'SUPER_ADMIN':
                    company_id = request.session.get('impersonate_company_id')
                    if company_id:
                        from .models import Company
                        request.company = Company.objects.filter(pk=company_id).first()
                    else:
                        request.company = None # Global view
                elif profile.role == 'PLATFORM_OWNER':
                    request.company = None # Platform operators see global company list, but no internal data (enforced in models)
                else:
                    request.company = profile.company
            except UserProfile.DoesNotExist:
                pass
        return None

class LicenseMiddleware(MiddlewareMixin):
    """
    Middleware to check company license validity and active status.
    Superadmins are exempt from these checks.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            path = request.path
            # Define public paths that don't require license check
            PUBLIC_PREFIXES = ('/logout/', '/terms/', '/privacy/', '/static/', '/media/', '/admin/')
            is_public = any(path == p or path.startswith(p) for p in PUBLIC_PREFIXES)
            is_superadmin_path = path.startswith('/superadmin/')

            # Profile should be attached by CompanyContextMiddleware
            profile = getattr(request, 'profile', None)
            
            if not is_public and not is_superadmin_path:
                if profile:
                    if profile.role in ['SUPER_ADMIN', 'PLATFORM_OWNER']:
                        return None # Infrastructure roles bypass license checks
                    
                    if profile.company is None:
                        from django.contrib.auth import logout
                        from django.contrib import messages
                        from django.shortcuts import redirect
                        logout(request)
                        messages.error(request, "Your account has no company assigned.")
                        return redirect('login')
                    
                    if not profile.company.is_active:
                        from django.contrib.auth import logout
                        from django.contrib import messages
                        from django.shortcuts import redirect
                        logout(request)
                        messages.error(request, "Your company account is disabled. Contact support.")
                        return redirect('login')
                    
                    if not profile.company.is_license_valid():
                        from django.contrib.auth import logout
                        from django.contrib import messages
                        from django.shortcuts import redirect
                        logout(request)
                        messages.error(request, f"License expired on {profile.company.license_end_date}. Contact support.")
                        return redirect('login')
        return None
