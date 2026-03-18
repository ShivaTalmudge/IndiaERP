from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect

def login_required_custom(view_func):
    """Basic login requirement across the project."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def permission_required(perm_name):
    """
    Checks if the user's profile has the specified permission bit set.
    - SUPER_ADMIN: Bypass
    - PLATFORM_OWNER: Blocked from company-aware data views
    - COMPANY_OWNER: Bypass (implicit full access to their own company)
    - STAFF: Checked against boolean fields on UserProfile
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            profile = getattr(request, 'profile', None)
            if not profile:
                return HttpResponseForbidden("Access Denied: User Profile missing.")
            
            # 1. Super Admin bypass (must be impersonating to access company-aware views)
            if profile.role == 'SUPER_ADMIN':
                if not getattr(request, 'company', None):
                    return HttpResponseForbidden("Access Denied: Super Admin must impersonate a company to access this view.")
                return view_func(request, *args, **kwargs)
            
            # 2. Platform Owner block (Critical Requirement)
            if profile.role == 'PLATFORM_OWNER':
                return HttpResponseForbidden("Access Denied: Platform Owners cannot access internal company data.")
            
            # 3. Company Owner bypass (Full access within company)
            if profile.role == 'COMPANY_OWNER':
                if not getattr(request, 'company', None):
                    return HttpResponseForbidden("Access Denied: You are not associated with any company.")
                return view_func(request, *args, **kwargs)
                
            # 4. Staff check
            if getattr(profile, perm_name, False):
                if not getattr(request, 'company', None):
                    return HttpResponseForbidden("Access Denied: You are not associated with any company.")
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(f"Access Denied: Insufficient permissions ({perm_name}).")
        return _wrapped_view
    return decorator

def super_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request, 'profile') and request.profile.role == 'SUPER_ADMIN':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: Super Admin role required.")
    return _wrapped_view

def platform_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request, 'profile') and request.profile.role in ['SUPER_ADMIN', 'PLATFORM_OWNER']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: Platform Owner or Super Admin role required.")
    return _wrapped_view

def company_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request, 'profile') and request.profile.role in ['SUPER_ADMIN', 'COMPANY_OWNER']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access Denied: Company Owner or Super Admin role required.")
    return _wrapped_view
