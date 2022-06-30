from dataclasses import field
from django import forms
from .models import CSV, Teacher

class CSVForm(forms.ModelForm):
    class Meta:
        model = CSV
        fields = ['upload_file']

        widgets = {
            'upload_file':forms.FileInput(attrs={'class':'form-control','accept':'.csv'}),
        }