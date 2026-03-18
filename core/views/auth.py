"""core/views/auth.py — Authentication & public pages."""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..forms import LoginForm
from ..decorators import login_required_custom
from ..utils import log_action


def landing_page(request):
    return render(request, "public/landing.html")


def terms_page(request):
    return render(request, "public/terms.html")


def privacy_page(request):
    return render(request, "public/privacy.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                if not user.is_active:
                    messages.error(request, "Your account is disabled.")
                    return render(request, "auth/login.html", {"form": form})
                
                login(request, user)
                
                # We need to get the profile to check role
                try:
                    p = user.profile
                    log_action(request, "login", "User", user.username)
                    if p.role == "superadmin":
                        return redirect("superadmin_dashboard")
                except Exception:
                    pass
                
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
    
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("login")


@login_required_custom
def profile_view(request):
    return render(request, "auth/profile.html")


@login_required_custom
def change_password(request):
    # This would usually handle password change form
    return render(request, "auth/change_password.html")
