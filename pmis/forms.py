from django import forms
from .models import Client, Project, Task

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'Budget','image','image_2', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'status', 'project', 'task_start_date', 'task_end_date', 'assigned_to']
        widgets = {
            'task_start_date': forms.DateInput(attrs={'type': 'date'}),
            'task_end_date': forms.DateInput(attrs={'type': 'date'})
        }

class CSVUploadForm(forms.Form):
    class Meta:
        csv_files = forms.FileField()
