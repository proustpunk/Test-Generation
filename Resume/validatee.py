from django import forms

def validate_password(password):
    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters long.")
    if not any(char.isupper() for char in password):
        raise forms.ValidationError("Password must include at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise forms.ValidationError("Password must include at least one lowercase letter.")
    if not any(char.isdigit() for char in password):
        raise forms.ValidationError("Password must include at least one number.")
    if not any(char in "!@#$%^&*" for char in password):
        raise forms.ValidationError("Password must include at least one special character (!@#$%^&*).")

