from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AnnouncementForm,
    AssignmentForm,
    CourseEditForm,
    CourseForm,
    CourseGroupForm,
    GradeSubmissionForm,
    JoinCourseForm,
    QuickAnnouncementForm,
    QuickAssignmentForm,
    StudyMaterialForm,
    SubmissionForm,
)
from .models import Announcement, Assignment, Course, CourseGroup, Enrollment, StudyMaterial, Submission


def add_student_submission_status(assignments, student):
    """Attach the current student's submission to each assignment for display."""
    assignments = list(assignments)
    submissions = Submission.objects.filter(
        assignment__in=assignments, student=student
    )
    submissions_by_assignment = {
        submission.assignment_id: submission for submission in submissions
    }
    for assignment in assignments:
        assignment.student_submission = submissions_by_assignment.get(assignment.id)
    return assignments


@login_required
def create_course(request):
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can create courses.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CourseForm(request.POST, teacher=request.user)

        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            new_group_name = form.cleaned_data["new_group_name"].strip()
            if new_group_name:
                group = CourseGroup.objects.filter(
                    teacher=request.user, name__iexact=new_group_name
                ).first()
                if group is None:
                    group = CourseGroup.objects.create(
                        teacher=request.user, name=new_group_name
                    )
                course.group = group
            course.save()

            messages.success(
                request,
                f"Course created successfully. Course code: {course.course_code}",
            )
            return redirect("my_courses")
    else:
        form = CourseForm(teacher=request.user)

    return render(request, "courses/create_course.html", {"form": form})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can edit it.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CourseEditForm(request.POST, instance=course, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Course details were updated successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = CourseEditForm(instance=course, teacher=request.user)

    return render(request, "courses/edit_course.html", {"form": form, "course": course})


@login_required
def manage_course_groups(request):
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can manage course groups.")
        return redirect("my_courses")

    if request.method == "POST":
        form = CourseGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.teacher = request.user
            try:
                group.save()
            except Exception:
                form.add_error("name", "You already have a group with this name.")
            else:
                messages.success(request, f"{group.name} was created successfully.")
                return redirect("manage_course_groups")
    else:
        form = CourseGroupForm()

    groups = request.user.course_groups.prefetch_related("courses").all()
    return render(request, "courses/manage_course_groups.html", {"form": form, "groups": groups, "active_nav": "courses"})


@login_required
def edit_course_group(request, group_id):
    group = get_object_or_404(CourseGroup, id=group_id, teacher=request.user)
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can edit course groups.")
        return redirect("my_courses")
    if request.method == "POST":
        form = CourseGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Course group was updated successfully.")
            return redirect("manage_course_groups")
    else:
        form = CourseGroupForm(instance=group)
    return render(request, "courses/edit_course_group.html", {"form": form, "group": group, "active_nav": "courses"})


@login_required
def delete_course_group(request, group_id):
    group = get_object_or_404(CourseGroup, id=group_id, teacher=request.user)
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can delete course groups.")
        return redirect("my_courses")
    if request.method == "POST":
        group_name = group.name
        group.delete()
        messages.success(request, f"{group_name} was deleted. Its courses are now in No Group.")
    return redirect("manage_course_groups")


@login_required
def join_course(request):
    if request.user.role != "student":
        messages.error(request, "Only students can join courses.")
        return redirect("dashboard")

    if request.method == "POST":
        form = JoinCourseForm(request.POST)

        if form.is_valid():
            course = Course.objects.filter(
                course_code=form.cleaned_data["course_code"],
                is_archived=False,
            ).first()

            if course is None:
                form.add_error("course_code", "No course was found with this code.")
            else:
                enrollment, created = Enrollment.objects.get_or_create(
                    course=course,
                    student=request.user,
                )

                if created:
                    messages.success(request, f"You joined {course.title} successfully.")
                else:
                    messages.info(request, f"You already joined {course.title}.")

                return redirect("my_courses")
    else:
        form = JoinCourseForm()

    return render(request, "courses/join_course.html", {"form": form})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role == "teacher":
        has_access = course.teacher_id == request.user.id
    else:
        has_access = Enrollment.objects.filter(
            course=course,
            student=request.user,
        ).exists()

    if not has_access:
        messages.error(request, "You do not have access to this course.")
        return redirect("dashboard")

    announcements = course.announcements.select_related("author")
    assignments = course.assignments.all()
    if request.user.role == "student":
        assignments = add_student_submission_status(assignments, request.user)
    materials = course.study_materials.select_related("uploaded_by")
    enrollments = course.enrollments.select_related("student")
    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "announcements": announcements,
            "assignments": assignments,
            "materials": materials,
            "enrollments": enrollments,
            "active_course_id": course.id,
        },
    )


@login_required
def create_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can upload lectures.")
        return redirect("course_detail", course_id=course.id)

    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploaded_by = request.user
            material.save()
            messages.success(request, "Lecture added successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = StudyMaterialForm()

    return render(request, "courses/create_material.html", {"course": course, "form": form})


@login_required
def edit_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id)
    course = material.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can edit lectures.")
        return redirect("dashboard")

    if request.method == "POST":
        form = StudyMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecture updated successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = StudyMaterialForm(instance=material)

    return render(request, "courses/edit_material.html", {"course": course, "material": material, "form": form})


@login_required
def delete_material(request, material_id):
    material = get_object_or_404(StudyMaterial, id=material_id)
    course = material.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can delete lectures.")
        return redirect("dashboard")

    if request.method == "POST":
        material.delete()
        messages.success(request, "Lecture deleted successfully.")

    return redirect("course_detail", course_id=course.id)


@login_required
def create_announcement(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can post announcements.")
        return redirect("course_detail", course_id=course.id)

    if request.method == "POST":
        form = AnnouncementForm(request.POST)

        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course = course
            announcement.author = request.user
            announcement.save()

            messages.success(request, "Announcement posted successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = AnnouncementForm()

    return render(
        request,
        "courses/create_announcement.html",
        {"course": course, "form": form},
    )


@login_required
def quick_announcement(request):
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can post announcements.")
        return redirect("dashboard")

    courses = request.user.created_courses.filter(is_archived=False).order_by("-created_at")
    if not courses.exists():
        messages.info(request, "Create a course before posting an announcement.")
        return redirect("create_course")

    if request.method == "POST":
        form = QuickAnnouncementForm(request.POST, teacher=request.user)
        if form.is_valid():
            announcement = Announcement.objects.create(
                course=form.cleaned_data["course"],
                author=request.user,
                title=form.cleaned_data["title"],
                message=form.cleaned_data["message"],
            )
            messages.success(request, "Announcement posted successfully.")
            return redirect("course_detail", course_id=announcement.course_id)
    else:
        form = QuickAnnouncementForm(
            teacher=request.user,
            initial={"course": courses.first()},
        )

    return render(request, "courses/quick_announcement.html", {"form": form})


@login_required
def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    course = announcement.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can edit announcements.")
        return redirect("dashboard")

    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)

        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = AnnouncementForm(instance=announcement)

    return render(
        request,
        "courses/edit_announcement.html",
        {"course": course, "announcement": announcement, "form": form},
    )


@login_required
def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    course = announcement.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can delete announcements.")
        return redirect("dashboard")

    if request.method == "POST":
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")

    return redirect("course_detail", course_id=course.id)


@login_required
def my_courses(request):
    if request.user.role == "teacher":
        courses = request.user.created_courses.filter(is_archived=False).select_related("group").order_by("-created_at")
        course_groups = request.user.course_groups.prefetch_related("courses").all()
        grouped_courses = [
            {
                "group": group,
                "courses": [course for course in courses if course.group_id == group.id],
            }
            for group in course_groups
        ]
        grouped_courses = [item for item in grouped_courses if item["courses"]]
        ungrouped_courses = [course for course in courses if course.group_id is None]
    else:
        courses = Course.objects.filter(enrollments__student=request.user, is_archived=False).select_related(
            "teacher"
        ).order_by("-created_at")
        grouped_courses = []
        ungrouped_courses = []

    return render(
        request,
        "courses/my_courses.html",
        {
            "courses": courses,
            "grouped_courses": grouped_courses,
            "ungrouped_courses": ungrouped_courses,
            "active_nav": "courses",
        },
    )


@login_required
def create_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can create assignments.")
        return redirect("course_detail", course_id=course.id)

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, "Assignment created successfully.")
            return redirect("course_detail", course_id=course.id)
    else:
        form = AssignmentForm()

    return render(
        request,
        "courses/create_assignment.html",
        {"course": course, "form": form},
    )


@login_required
def quick_assignment(request):
    if request.user.role != "teacher":
        messages.error(request, "Only teachers can create assignments.")
        return redirect("dashboard")

    courses = request.user.created_courses.filter(is_archived=False).order_by("-created_at")
    if not courses.exists():
        messages.info(request, "Create a course before adding an assignment.")
        return redirect("create_course")

    if request.method == "POST":
        form = QuickAssignmentForm(request.POST, teacher=request.user)
        if form.is_valid():
            assignment = Assignment.objects.create(
                course=form.cleaned_data["course"],
                created_by=request.user,
                title=form.cleaned_data["title"],
                instructions=form.cleaned_data["instructions"],
                due_date=form.cleaned_data["due_date"],
            )
            messages.success(request, "Assignment created successfully.")
            return redirect("assignment_detail", assignment_id=assignment.id)
    else:
        form = QuickAssignmentForm(
            teacher=request.user,
            initial={"course": courses.first()},
        )

    return render(request, "courses/quick_assignment.html", {"form": form})


@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can edit assignments.")
        return redirect("dashboard")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)

        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully.")
            return redirect("assignment_detail", assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)

    return render(
        request,
        "courses/edit_assignment.html",
        {"course": course, "assignment": assignment, "form": form},
    )


@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can delete assignments.")
        return redirect("dashboard")

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        return redirect("course_detail", course_id=course.id)

    return redirect("assignment_detail", assignment_id=assignment.id)


@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user.role == "teacher":
        has_access = course.teacher_id == request.user.id
    else:
        has_access = Enrollment.objects.filter(
            course=course,
            student=request.user,
        ).exists()

    if not has_access:
        messages.error(request, "You do not have access to this assignment.")
        return redirect("dashboard")

    submission = None
    if request.user.role == "student":
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user,
        ).first()

    return render(
        request,
        "courses/assignment_detail.html",
        {
            "assignment": assignment,
            "course": course,
            "submission": submission,
            "active_course_id": course.id,
        },
    )


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user.role != "student" or not Enrollment.objects.filter(
        course=course,
        student=request.user,
    ).exists():
        messages.error(request, "Only enrolled students can submit this assignment.")
        return redirect("assignment_detail", assignment_id=assignment.id)

    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user,
    ).first()

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            saved_submission = form.save(commit=False)
            saved_submission.assignment = assignment
            saved_submission.student = request.user
            saved_submission.save()
            messages.success(request, "Your assignment submission has been saved.")
            return redirect("assignment_detail", assignment_id=assignment.id)
    else:
        form = SubmissionForm(instance=submission)

    return render(
        request,
        "courses/submit_assignment.html",
        {"assignment": assignment, "course": course, "form": form, "submission": submission},
    )


@login_required
def delete_submission(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user.role != "student":
        messages.error(request, "Only students can delete their own submissions.")
        return redirect("assignment_detail", assignment_id=assignment.id)

    submission = get_object_or_404(
        Submission, assignment=assignment, student=request.user
    )

    if request.method == "POST":
        if submission.file:
            submission.file.delete(save=False)
        submission.delete()
        messages.success(request, "Your submission was deleted successfully.")

    return redirect("assignment_detail", assignment_id=assignment.id)


@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can view submissions.")
        return redirect("assignment_detail", assignment_id=assignment.id)

    submissions = assignment.submissions.select_related("student")
    return render(
        request,
        "courses/submissions_list.html",
        {"assignment": assignment, "course": course, "submissions": submissions},
    )


@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("assignment", "assignment__course", "student"),
        id=submission_id,
    )
    assignment = submission.assignment
    course = assignment.course

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can grade submissions.")
        return redirect("dashboard")

    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.graded_at = timezone.now()
            graded_submission.save()
            messages.success(request, "Marks and feedback have been saved.")
            return redirect("view_submissions", assignment_id=assignment.id)
    else:
        form = GradeSubmissionForm(instance=submission)

    return render(
        request,
        "courses/grade_submission.html",
        {
            "course": course,
            "assignment": assignment,
            "submission": submission,
            "form": form,
            "active_course_id": course.id,
        },
    )


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can delete it.")
        return redirect("dashboard")

    if request.method == "POST":
        course_title = course.title
        course.delete()
        messages.success(request, f"{course_title} was deleted successfully.")
        return redirect("my_courses")

    return redirect("course_detail", course_id=course.id)


@login_required
def archive_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can archive it.")
        return redirect("dashboard")
    if request.method == "POST":
        course.is_archived = True
        course.save(update_fields=["is_archived"])
        messages.success(request, f"{course.title} was archived successfully.")
    return redirect("my_courses")


@login_required
def restore_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_archived=True)
    if request.user.role != "teacher" or course.teacher_id != request.user.id:
        messages.error(request, "Only this course's teacher can restore it.")
        return redirect("dashboard")
    if request.method == "POST":
        course.is_archived = False
        course.save(update_fields=["is_archived"])
        messages.success(request, f"{course.title} was restored successfully.")
    return redirect("archived_courses")


@login_required
def leave_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != "student":
        messages.error(request, "Only students can leave courses.")
        return redirect("dashboard")

    enrollment = Enrollment.objects.filter(
        course=course,
        student=request.user,
    ).first()

    if enrollment is None:
        messages.error(request, "You are not enrolled in this course.")
        return redirect("dashboard")

    if request.method == "POST":
        enrollment.delete()
        messages.success(request, f"You left {course.title} successfully.")
        return redirect("my_courses")

    return redirect("course_detail", course_id=course.id)


@login_required
def all_announcements(request):
    if request.user.role == "teacher":
        announcements = Announcement.objects.filter(
            course__teacher=request.user,
            course__is_archived=False,
        ).select_related("course", "author")
    else:
        announcements = Announcement.objects.filter(
            course__enrollments__student=request.user,
            course__is_archived=False,
        ).select_related("course", "author")

    return render(
        request,
        "courses/all_announcements.html",
        {"announcements": announcements, "active_nav": "announcements"},
    )


@login_required
def to_review(request):
    if request.user.role != "teacher":
        messages.error(request, "This page is for teachers only.")
        return redirect("dashboard")

    submissions = Submission.objects.filter(
        assignment__course__teacher=request.user,
        assignment__course__is_archived=False,
        graded_at__isnull=True,
    ).select_related("student", "assignment", "assignment__course")
    return render(
        request,
        "courses/to_review.html",
        {"submissions": submissions, "active_nav": "review"},
    )


@login_required
def course_materials(request):
    if request.user.role != "teacher":
        messages.error(request, "This page is for teachers only.")
        return redirect("dashboard")

    materials = StudyMaterial.objects.filter(
        course__teacher=request.user,
        course__is_archived=False,
    ).select_related("course", "uploaded_by")
    return render(
        request,
        "courses/course_materials.html",
        {"materials": materials, "active_nav": "materials"},
    )


@login_required
def deadlines(request):
    if request.user.role == "teacher":
        assignments = Assignment.objects.filter(
            course__teacher=request.user,
            course__is_archived=False,
            due_date__gte=timezone.now(),
        ).select_related("course").order_by("due_date")
    else:
        assignments = Assignment.objects.filter(
            course__enrollments__student=request.user,
            course__is_archived=False,
            due_date__gte=timezone.now(),
        ).select_related("course").order_by("due_date")

        assignments = add_student_submission_status(assignments, request.user)

    today = timezone.localdate()
    for assignment in assignments:
        assignment.days_left = max((assignment.due_date.date() - today).days, 0)

    return render(
        request,
        "courses/deadlines.html",
        {"assignments": assignments, "active_nav": "deadlines"},
    )


@login_required
def archived_courses(request):
    if request.user.role == "teacher":
        courses = request.user.created_courses.filter(is_archived=True).order_by("-created_at")
    else:
        courses = Course.objects.filter(enrollments__student=request.user, is_archived=True).select_related("teacher").order_by("-created_at")
    return render(
        request,
        "courses/archived_courses.html",
        {"active_nav": "settings", "courses": courses},
    )
