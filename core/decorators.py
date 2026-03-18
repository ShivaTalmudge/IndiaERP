from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def get_profile(request):
    """Retrieve the profile attached by middleware or fetch if missing."""
    return getattr(request, 'profile', None) or (request.user.is_authenticated and request.user.profile)


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Use the role set by middleware if available
        role = getattr(request, 'user_role', None)
        if not role:
            # Fallback if middleware hasn't run
            try: role = request.user.profile.role
            except Exception: pass

        if role == 'superadmin':
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Super Admin access required.")
        return redirect('dashboard' if request.user.is_authenticated else 'login')
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        role = getattr(request, 'user_role', None) or (request.user.profile.role)

        if role in ('superadmin', 'admin'):
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Insufficient privileges. Admin access required.")
        return redirect('dashboard')
    return wrapper


def permission_required(perm):
    """
    Cleaner RBAC decorator that utilizes middleware-provided context.
    - superadmin and admin bypass all permission checks.
    - staff user permissions are verified against the specific profile flag.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Role check from middleware
            role = getattr(request, 'user_role', None) or (request.user.profile.role)

            # Bypass check for admin roles
            if role in ('superadmin', 'admin'):
                return view_func(request, *args, **kwargs)

            # Fail-closed if permission not specified
            if perm is None:
                messages.error(request, "Insufficient privileges.")
                return redirect('dashboard')

            # For staff users, check the specific flag
            profile = get_profile(request)
            if profile and getattr(profile, perm, False):
                return view_func(request, *args, **kwargs)

            messages.error(request, "You don't have permission to perform this action.")
            return redirect('dashboard')

        return wrapper
    return decorator
