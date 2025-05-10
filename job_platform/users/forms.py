from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UniversalRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")
    role = forms.ChoiceField(
        choices=[('job_seeker', 'Соискатель'), ('employer', 'Работодатель')],
        widget=forms.RadioSelect,
        label="Выберите роль"
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'role']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают")
        return cleaned_data
