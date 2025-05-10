from django import forms
from companies.models import Vacancy

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'description', 'requirements', 'location', 'city',
            'salary_from', 'salary_to', 'currency', 'employment_type', 'experience'
        ]
