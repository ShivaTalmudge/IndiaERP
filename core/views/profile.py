"""core/views/profile.py — User profile view/edit + password change."""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.contrib.auth.models import User

from ..decorators import permission_required

fc = {'class': 'form-control'}


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs=fc))
    last_name  = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs=fc))
    email      = forms.EmailField(required=False, widget=forms.EmailInput(attrs=fc))
    phone      = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs=fc))


@permission_required(None)  # any logged-in user
def profile_view(request):
    user    = request.user
    profile = user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name  = form.cleaned_data["last_name"]
            user.email      = form.cleaned_data["email"]
            user.save(update_fields=["first_name", "last_name", "email"])
            profile.phone = form.cleaned_data["phone"]
            profile.save(update_fields=["phone"])
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(initial={
            "first_name": user.first_name,
            "last_name":  user.last_name,
            "email":      user.email,
            "phone":      profile.phone,
        })

    return render(request, "core/profile.html", {"form": form, "profile": profile})


@permission_required(None)  # any logged-in user
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    # Apply Bootstrap styling
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    return render(request, "core/change_password.html", {"form": form})
