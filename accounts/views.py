from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from courses.models import Assignment, Course, Submission

from .forms import UserLoginForm, UserProfileForm, UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your MetroClass account has been created.")
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Welcome back to MetroClass.")
            return redirect("dashboard")
    else:
        form = UserLoginForm(request)

    return render(request, "accounts/login.html", {"form": form})


def user_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been signed out.")

    return redirect("home")


@login_required
def dashboard(request):
    if request.user.role == "teacher":
        courses = request.user.created_courses.filter(is_archived=False).order_by("-created_at")
        upcoming_assignments = Assignment.objects.filter(
            course__teacher=request.user,
            due_date__gte=timezone.now(),
        ).order_by("due_date")
        submissions = Submission.objects.filter(
            assignment__course__teacher=request.user
        )
        return render(
            request,
            "accounts/teacher_dashboard.html",
            {
                "courses": courses,
                "upcoming_assignments": upcoming_assignments[:3],
                "course_count": courses.count(),
                "assignment_count": upcoming_assignments.count(),
                "submission_count": submissions.count(),
                "recent_submissions": submissions.select_related(
                    "student", "assignment", "assignment__course"
                ).order_by("-updated_at")[:2],
            },
        )

    courses = Course.objects.filter(enrollments__student=request.user, is_archived=False).select_related(
        "teacher"
    ).order_by("-created_at")
    upcoming_assignments = Assignment.objects.filter(
        course__enrollments__student=request.user,
        due_date__gte=timezone.now(),
    ).select_related("course").order_by("due_date")
    return render(
        request,
        "accounts/student_dashboard.html",
        {
            "courses": courses,
            "upcoming_assignments": upcoming_assignments[:3],
            "course_count": courses.count(),
            "assignment_count": upcoming_assignments.count(),
        },
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST, instance=request.user, is_student=request.user.role == "student"
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Your account details have been updated.")
            return redirect("dashboard")
    else:
        form = UserProfileForm(
            instance=request.user, is_student=request.user.role == "student"
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form, "active_nav": "settings"},
    )


@login_required
def delete_account_confirm(request):
    """First confirmation before an account can be deleted."""
    if request.method == "POST":
        request.session["account_delete_step_one"] = True
        return redirect("delete_account_final")

    return render(
        request,
        "accounts/delete_account_confirm.html",
        {"active_nav": "settings"},
    )


@login_required
def delete_account_final(request):
    """Final typed confirmation and permanent account deletion."""
    if not request.session.get("account_delete_step_one"):
        return redirect("delete_account_confirm")

    if request.method == "POST":
        if request.POST.get("confirmation_text", "").strip().upper() != "DELETE":
            messages.error(request, 'Please type DELETE exactly to remove your account.')
        else:
            account = request.user
            display_name = account.display_name
            request.session.pop("account_delete_step_one", None)
            logout(request)
            account.delete()
            messages.success(request, f"{display_name}, your account has been deleted.")
            return redirect("home")

    return render(
        request,
        "accounts/delete_account_final.html",
        {"active_nav": "settings"},
    )
