from django.urls import path

from . import views


urlpatterns = [
    path("create/", views.create_course, name="create_course"),
    path("groups/", views.manage_course_groups, name="manage_course_groups"),
    path("groups/<int:group_id>/edit/", views.edit_course_group, name="edit_course_group"),
    path("groups/<int:group_id>/delete/", views.delete_course_group, name="delete_course_group"),
    path("<int:course_id>/edit/", views.edit_course, name="edit_course"),
    path("join/", views.join_course, name="join_course"),
    path("my/", views.my_courses, name="my_courses"),
    path("announcements/", views.all_announcements, name="all_announcements"),
    path("to-review/", views.to_review, name="to_review"),
    path("materials/", views.course_materials, name="course_materials"),
    path("deadlines/", views.deadlines, name="deadlines"),
    path("archived/", views.archived_courses, name="archived_courses"),
    path("announcements/quick-create/", views.quick_announcement, name="quick_announcement"),
    path("assignments/quick-create/", views.quick_assignment, name="quick_assignment"),
    path("<int:course_id>/lectures/create/", views.create_material, name="create_material"),
    path("lectures/<int:material_id>/edit/", views.edit_material, name="edit_material"),
    path("lectures/<int:material_id>/delete/", views.delete_material, name="delete_material"),
    path(
        "<int:course_id>/announcements/create/",
        views.create_announcement,
        name="create_announcement",
    ),
    path(
        "announcements/<int:announcement_id>/edit/",
        views.edit_announcement,
        name="edit_announcement",
    ),
    path(
        "announcements/<int:announcement_id>/delete/",
        views.delete_announcement,
        name="delete_announcement",
    ),
    path(
        "<int:course_id>/assignments/create/",
        views.create_assignment,
        name="create_assignment",
    ),
    path(
        "<int:course_id>/delete/",
        views.delete_course,
        name="delete_course",
    ),
    path("<int:course_id>/archive/", views.archive_course, name="archive_course"),
    path("<int:course_id>/restore/", views.restore_course, name="restore_course"),
    path(
        "<int:course_id>/leave/",
        views.leave_course,
        name="leave_course",
    ),
    path(
        "assignments/<int:assignment_id>/",
        views.assignment_detail,
        name="assignment_detail",
    ),
    path(
        "assignments/<int:assignment_id>/submit/",
        views.submit_assignment,
        name="submit_assignment",
    ),
    path(
        "assignments/<int:assignment_id>/delete-submission/",
        views.delete_submission,
        name="delete_submission",
    ),
    path(
        "assignments/<int:assignment_id>/edit/",
        views.edit_assignment,
        name="edit_assignment",
    ),
    path(
        "assignments/<int:assignment_id>/delete/",
        views.delete_assignment,
        name="delete_assignment",
    ),
    path(
        "assignments/<int:assignment_id>/submissions/",
        views.view_submissions,
        name="view_submissions",
    ),
    path(
        "submissions/<int:submission_id>/grade/",
        views.grade_submission,
        name="grade_submission",
    ),
    path("<int:course_id>/", views.course_detail, name="course_detail"),
]
