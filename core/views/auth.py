"""core/views/auth.py — Public pages and authentication."""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from ..forms import LoginForm
from ..decorators import login_required_custom


def _profile(user):
    try:
        return user.profile
    except Exception:
        return None


def landing_page(request):
    features_list = [
        "Sales Invoicing",
        "Purchase Orders",
        "Inventory Management",
        "GST Reports",
        "HSN Master",
        "Multi-User & Roles",
    ]
    return render(request, "core/landing.html", {"feature_items": features_list})


def terms_page(request):
    return render(request, "core/terms.html")


def privacy_page(request):
    return render(request, "core/privacy.html")


def login_view(request):
    if request.user.is_authenticated:
        p = _profile(request.user)
        if p and p.role == "superadmin":
            return redirect("superadmin_dashboard")
        return redirect("dashboard")

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                p = _profile(user)
                if p is None:
                    messages.error(request, "Account not configured. Contact administrator.")
                    return render(request, "core/login.html", {"form": form})
                if not p.is_active:
                    messages.error(request, "Your account is disabled.")
                    return render(request, "core/login.html", {"form": form})
                login(request, user)
                if p.role == "superadmin":
                    return redirect("superadmin_dashboard")
                return redirect("dashboard")
            messages.error(request, "Invalid username or password.")
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
