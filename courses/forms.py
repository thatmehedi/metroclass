from django import forms

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
        fields = ["title", "description", "group"]
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
        }

    field_order = ["title", "description", "group", "new_group_name"]

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].required = False
        self.fields["group"].empty_label = "No Group"
        self.fields["group"].queryset = CourseGroup.objects.filter(teacher=teacher) if teacher else CourseGroup.objects.none()
        self.fields["group"].widget.attrs["class"] = "form-select"


class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "group"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Course title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Brief course description", "rows": 4}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].required = False
        self.fields["group"].empty_label = "No Group"
        self.fields["group"].queryset = CourseGroup.objects.filter(teacher=teacher) if teacher else CourseGroup.objects.none()
        self.fields["group"].widget.attrs["class"] = "form-select"

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


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "instructions", "due_date"]
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
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_date"].input_formats = ["%Y-%m-%dT%H:%M"]


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
