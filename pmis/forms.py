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

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'status', 'project', 'task_start_date', 'task_end_date', 'assigned_to']

class CSVUploadForm(forms.Form):
    class Meta:
        csv_files = forms.FileField()
