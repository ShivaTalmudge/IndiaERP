from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

PUBLIC_PREFIXES = ('/', '/login/', '/logout/', '/terms/', '/privacy/', '/static/', '/media/')


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            is_public = any(path == p or path.startswith(p) for p in PUBLIC_PREFIXES)
            is_superadmin_path = path.startswith('/superadmin/')

            if not is_public and not is_superadmin_path:
                try:
                    profile = request.user.profile
                    if profile.role == 'superadmin':
                        pass  # never blocked
                    elif profile.company is None:
                        logout(request)
                        messages.error(request, "Your account has no company assigned.")
                        return redirect('login')
                    elif not profile.company.is_active:
                        logout(request)
                        messages.error(request, "Your company account is disabled. Contact support.")
                        return redirect('login')
                    elif not profile.company.is_license_valid():
                        logout(request)
                        messages.error(request, f"License expired on {profile.company.license_end_date}. Contact support.")
                        return redirect('login')
                except Exception:
                    pass
        return self.get_response(request)


class CompanyContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        request.user_role = None
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                request.company = profile.company
                request.user_role = profile.role
            except Exception:
                pass
        return self.get_response(request)
