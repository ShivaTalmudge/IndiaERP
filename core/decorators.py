from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def _get_role(request):
    try:
        return request.user.profile.role
    except Exception:
        return None


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
        if _get_role(request) == 'superadmin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Super Admin access required.")
        return redirect('login')
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if _get_role(request) in ('superadmin', 'admin'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Admin access required.")
        return redirect('dashboard')
    return wrapper


def permission_required(perm):
    """
    Decorator that checks whether the user has the required permission.
    - If perm is None, any authenticated user is allowed (used for profile etc.)
    - If the user is admin/superadmin, they get access to everything.
    - Otherwise, checks the specific permission flag on the profile.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Must be logged in
            if not request.user.is_authenticated:
                return redirect('login')

            # perm=None means fallback to role-based check (Fail-Closed)
            if perm is None:
                role = _get_role(request)
                if role in ('superadmin', 'admin'):
                    return view_func(request, *args, **kwargs)
                messages.error(request, "Insufficient privileges for this action.")
                return redirect('dashboard')

            # Get role — admin/superadmin bypass all permission checks
            role = _get_role(request)
            if role in ('superadmin', 'admin'):
                return view_func(request, *args, **kwargs)

            # For staff users, check the specific flag
            permission_granted = False
            try:
                profile = request.user.profile
                permission_granted = bool(getattr(profile, perm, False))
            except Exception:
                permission_granted = False

            if permission_granted:
                return view_func(request, *args, **kwargs)

            # User does not have permission — show an error and send to dashboard
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard')

        return wrapper
    return decorator
