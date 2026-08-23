from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Announcement, Assignment, Course, CourseGroup, StudyMaterial, Submission


class CourseForm(forms.ModelForm):
    new_group_name = forms.CharField(
        required=False,
        label="Or create a new group (optional)",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Example: Batch 62"}
        ),
    )

    class Meta:
        model = Course
        fields = ["title", "description", "group", "accent_color"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Course title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Brief course description",
                    "rows": 4,
                }
            ),
            "accent_color": forms.TextInput(
                attrs={"class": "form-control form-control-color", "type": "color"}
            ),
        }

    field_order = ["title", "description", "group", "accent_color", "new_group_name"]

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].required = False
        self.fields["group"].empty_label = "No Group"
        self.fields["group"].queryset = CourseGroup.objects.filter(teacher=teacher) if teacher else CourseGroup.objects.none()
        self.fields["group"].widget.attrs["class"] = "form-select"
        self.fields["accent_color"].label = "Course accent color"
        self.fields["accent_color"].help_text = "Used as a water-glass tint for the course header and course card banner."


class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "group", "accent_color"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Course title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Brief course description", "rows": 4}),
            "accent_color": forms.TextInput(attrs={"class": "form-control form-control-color", "type": "color"}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].required = False
        self.fields["group"].empty_label = "No Group"
        self.fields["group"].queryset = CourseGroup.objects.filter(teacher=teacher) if teacher else CourseGroup.objects.none()
        self.fields["group"].widget.attrs["class"] = "form-select"
        self.fields["accent_color"].label = "Course accent color"
        self.fields["accent_color"].help_text = "Used as a water-glass tint for the course header and course card banner."

class CourseGroupForm(forms.ModelForm):
    class Meta:
        model = CourseGroup
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Example: Batch 62"}
            )
        }


class JoinCourseForm(forms.Form):
    course_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-character course code",
            }
        ),
    )

    def clean_course_code(self):
        return self.cleaned_data["course_code"].strip().upper()


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "message"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Announcement title",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your announcement",
                    "rows": 5,
                }
            ),
        }


class QuickAnnouncementForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    title = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Announcement title"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Write your course update",
                "rows": 5,
            }
        ),
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(
            teacher=teacher, is_archived=False
        ).order_by("-created_at") if teacher else Course.objects.none()


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "instructions", "resource_file", "resource_link", "due_date"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Assignment title"}
            ),
            "instructions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Explain what students need to do",
                    "rows": 6,
                }
            ),
            "resource_file": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "resource_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Google Drive, Docs, YouTube, or website link (optional)",
                }
            ),
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resource_file"].label = "Attachment (optional)"
        self.fields["resource_file"].help_text = "Add any supporting file for students to download."
        self.fields["resource_link"].label = "Resource link (optional)"
        self.fields["resource_link"].help_text = "Add a website, Google Drive, Docs, or YouTube link."
        self.fields["due_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        minimum_due_date = timezone.localtime(timezone.now() + timedelta(minutes=1))
        self.fields["due_date"].widget.attrs["min"] = minimum_due_date.strftime(
            "%Y-%m-%dT%H:%M"
        )

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        if due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")

        return due_date


class QuickAssignmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    title = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Assignment title"}
        ),
    )
    instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Optional short instructions",
                "rows": 3,
            }
        ),
    )
    due_date = forms.DateTimeField(
        label="Due date",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(
            teacher=teacher, is_archived=False
        ).order_by("-created_at") if teacher else Course.objects.none()
        minimum_due_date = timezone.localtime(timezone.now() + timedelta(minutes=1))
        self.fields["due_date"].widget.attrs["min"] = minimum_due_date.strftime(
            "%Y-%m-%dT%H:%M"
        )

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]
        if due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file", "comment"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional note for your teacher",
                    "rows": 4,
                }
            ),
        }


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["score", "feedback"]
        widgets = {
            "score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: 85",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "feedback": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write helpful feedback for this student",
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["score"].required = True
        self.fields["score"].label = "Marks"
        self.fields["feedback"].required = True
        self.fields["feedback"].label = "Written feedback"


class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ["title", "file", "external_link"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Lecture title"}
            ),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "external_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Google Drive, Google Docs, YouTube, or website link",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        external_link = cleaned_data.get("external_link")

        if not file and not external_link:
            raise forms.ValidationError("Upload one file or add one link.")

        return cleaned_data
