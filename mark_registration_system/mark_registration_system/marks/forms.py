from django import forms
from .models import Mark

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'module', 'marks_obtained', 'total_marks']
