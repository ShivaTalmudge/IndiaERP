"""core/views/staff.py — Admin-level staff management."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction

from ..models import UserProfile
from ..forms import StaffForm
from ..decorators import company_owner_required


@company_owner_required
def staff_list(request):
    company = request.company
    staff = UserProfile.objects.filter(
        company=company, role="STAFF"
    ).select_related("user")
    return render(request, "core/staff_list.html", {"staff": staff})


@company_owner_required
def staff_add(request):
    company = request.company
    form = StaffForm()
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            if User.objects.filter(username=uname).exists():
                form.add_error("username", "Username already taken.")
            else:
                with transaction.atomic():
                    u = User.objects.create_user(
                        username=uname,
                        password=form.cleaned_data.get("password") or User.objects.make_random_password(),
                        email=form.cleaned_data.get("email", ""),
                        first_name=form.cleaned_data.get("first_name", ""),
                        last_name=form.cleaned_data.get("last_name", ""),
                    )
                    p = form.save(commit=False)
                    p.user = u
                    p.company = company
                    p.role = "STAFF"
                    p.save()
                messages.success(request, f"Staff '{uname}' created.")
                return redirect("staff_list")
    return render(request, "core/staff_form.html", {"form": form, "title": "Add Staff"})


@company_owner_required
def staff_edit(request, pk):
    company = request.company
    profile = get_object_or_404(
        UserProfile, pk=pk, company=company, role="STAFF"
    )
    form = StaffForm(
        instance=profile,
        initial={
            "username":   profile.user.username,
            "email":      profile.user.email,
            "first_name": profile.user.first_name,
            "last_name":  profile.user.last_name,
        },
    )
    if request.method == "POST":
        form = StaffForm(request.POST, instance=profile)
        if form.is_valid():
            u = profile.user
            u.email = form.cleaned_data.get("email", "")
            u.first_name = form.cleaned_data.get("first_name", "")
            u.last_name = form.cleaned_data.get("last_name", "")
            pw = form.cleaned_data.get("password")
            if pw:
                u.set_password(pw)
            u.save()
            p = form.save(commit=False)
            p.user = u
            p.company = company
            p.role = "STAFF"
            p.save()
            messages.success(request, "Staff updated.")
            return redirect("staff_list")
    return render(
        request,
        "core/staff_form.html",
        {"form": form, "title": "Edit Staff", "profile": profile},
    )


@company_owner_required
def staff_delete(request, pk):
    company = request.company
    profile = get_object_or_404(
        UserProfile, pk=pk, company=company, role="STAFF"
    )
    if request.method == "POST":
        name = profile.user.username
        profile.user.delete()
        messages.success(request, f"Staff '{name}' deleted.")
    return redirect("staff_list")
