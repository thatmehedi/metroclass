from .models import Course


def navigation_courses(request):
    """Provide the logged-in user's courses for the left navigation menu."""
    user = request.user

    if not user.is_authenticated:
        return {"navigation_courses": []}

    if user.role == "teacher":
        courses = user.created_courses.filter(is_archived=False).order_by("-created_at")
    else:
        courses = (
            Course.objects.filter(enrollments__student=user, is_archived=False)
            .select_related("teacher")
            .order_by("-created_at")
        )

    return {"navigation_courses": courses}
