from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="First Name", max_length=150, required=True)
    last_name = forms.CharField(label="Last Name", max_length=150, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[("", "Select your role"), *User.ROLE_CHOICES],
    )
    student_id = forms.CharField(
        label="Student ID / Roll Number",
        max_length=20,
        required=False,
        help_text="Required for students only. Example: 232-115-006",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "role", "student_id", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-select" if field_name == "role" else "form-control"

        self.fields["first_name"].widget.attrs["placeholder"] = "Enter your first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter your last name"
        self.fields["username"].widget.attrs["placeholder"] = "Choose a username for sign in"
        self.fields["email"].widget.attrs["placeholder"] = "name@example.com"
        self.fields["student_id"].widget.attrs["placeholder"] = "Example: 232-115-006"
        self.fields["password1"].widget.attrs["placeholder"] = "Create a password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm your password"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        student_id = cleaned_data.get("student_id", "").strip()

        if role == User.STUDENT and not student_id:
            self.add_error("student_id", "Student ID / Roll Number is required for students.")

        cleaned_data["student_id"] = student_id or None
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your password"}
        )
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "student_id"]
        labels = {"first_name": "First Name", "last_name": "Last Name", "student_id": "Student ID / Roll Number"}
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your last name"}
            ),
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "name@example.com"}
            ),
            "student_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Example: 232-115-006"}
            ),
        }

    def __init__(self, *args, is_student=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_student:
            self.fields.pop("student_id")
