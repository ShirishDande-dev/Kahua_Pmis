from django.shortcuts import render, redirect, get_object_or_404
from . models import Client, Project, Task
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required, permission_required
from .forms import ClientForm, ProjectForm, TaskForm, CSVUploadForm
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Q
import csv
from datetime import datetime
import logging
from collections import OrderedDict
logger = logging.getLogger(__name__)


TASK_LIST_CACHE_TIMEOUT = 60 * 15


def _invalidate_task_list_cache(*project_ids):
    cache.delete("task_list_all_projects")
    for project_id in project_ids:
        if project_id:
            cache.delete(f"task_list_project_{project_id}")


def index(request):
      
    return render(request, 'index.html')


#client view

@login_required
def client_list(request):
    clients = Client.objects.all()
    context = {'clients': clients}
    return render(request, 'client_list.html', context)

@login_required
def client_detail(request, pk):
    client = Client.objects.get(pk=pk)
    projects = Project.objects.filter(client=client)
    context = {'client': client, 'projects': projects}
    return render(request, 'client_detail.html', context)
#project view
@login_required(login_url='kahua_users:login')
def project_list(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'project_list.html', context)

@login_required
@cache_page(60 * 15)  # Cache for 15 minutes
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    tasks = Task.objects.filter(project=project)
    context = {'project': project, 'tasks': tasks, 'client': project.client}
    return render(request, 'project_detail.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user.client
            project.save()
            print("Files recieved: ", request.FILES)
            return redirect('project_list')
    else:
        form = ProjectForm()
    context = {'form': form}
    return render(request, 'project_create.html', context) 

#project update

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST,request.FILES, instance=project)
        if form.is_valid():
            client = getattr(project, 'client', None)
            form.save()
            return JsonResponse({'success': True, 'message': 'Project updated successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
            
    else:
        form = ProjectForm(instance=project)
    context = {'form': form , 'project': project}
    return render(request, 'project_update.html', context)

@login_required
def project_delete(request, pk):
    project = Project.objects.get(pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    context = {'project': project}
    return render(request, 'project_delete.html', context)


#task view

@login_required
def task_list(request, project_id=None):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    filters_active = bool(query or status)

    if filters_active:
        tasks = Task.objects.select_related('project', 'assigned_to__user')
        if project_id:
            tasks = tasks.filter(project_id=project_id)
    else:
        cache_key = f"task_list_{project_id}" if project_id else "task_list_all"
        tasks = cache.get(cache_key)
        if not tasks:
            if project_id:
                tasks = Task.objects.filter(project_id=project_id).select_related('project', 'assigned_to__user')
            else:
                tasks = Task.objects.all().select_related('project', 'assigned_to__user')
            cache.set(cache_key, tasks, timeout=60*15)

    if query:
        tasks = tasks.filter(
            Q(name__icontains=query) |
            Q(project__name__icontains=query) |
            Q(assigned_to__user__username__icontains=query)
        )

    if status in {str(choice[0]) for choice in Task.STATUS}:
        tasks = tasks.filter(status=int(status))

    tasks = tasks.order_by('project__name', 'task_end_date', 'name')

    filter_context = {
        'q': query,
        'status': status,
        'status_choices': Task.STATUS,
    }

    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        context = {'tasks': tasks, 'project': project, **filter_context}
    else:
        project_task_groups = OrderedDict()
        for task in tasks:
            project_task_groups.setdefault(task.project, []).append(task)

        context = {'project_task_groups': project_task_groups.items(), **filter_context}
    return render(request, 'task_list.html', context)

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    context = {'task': task}
    url = reverse('task_detail', args=[task.pk])
    
    return render(request, 'task_detail.html', context)

@login_required
@permission_required('pmis.can_assign_task', raise_exception=True)
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if request.user.has_perm('pmis.can_assign_task_to_client', task.assigned_to):
                task.save()
                cache.delete(f"task_list_project_{task.project.id}")
                cache.delete("task_list_all_projects")
                return redirect('task_list', project_id=task.project.id)
            else:
                messages.error(request, "You do not have permissions to assign tasks.")
                return redirect('task_list')
    else:
        form = TaskForm()
    context = {'form': form}
    return render(request, 'task_create.html', context)

@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    project = task.project
    if request.method == 'POST':
        previous_project_id = task.project.pk
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            cache_key = f"task_list_project_{task.project.pk}"
            cache.delete(cache_key)
            cache.delete("task_list_all_projects")
            return JsonResponse({
                "success": True,
                "message": "Task updated successfully.",
                "project_id": task.project.pk
            })
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)
    else:
        form = TaskForm(instance=task)
    context = {'form': form, 'task': task, 'project': project}
    return render(request, 'task_update.html', context)

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        project_id = task.project.pk
        task.delete()
        cache.delete(f"task_list_project_{project_id}")
        cache.delete("task_list_all_projects")
        return redirect('task_list', project_id=project_id)
    context = {'task': task}
    return render(request, 'task_delete.html', context)

@login_required
def upload_tasks_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # ✅ Move this OUTSIDE the 'if not ...' block
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'This is not a CSV file.')
                return redirect('task_list')

            try:
                file_data = csv_file.read().decode('utf-8').splitlines()
            except UnicodeDecodeError:
                file_data = csv_file.read().decode('iso-8859-1').splitlines()

            reader = csv.reader(file_data)
            next(reader)  # Skip header

            touched_project_ids = set()

            for row in reader:
                try:
                    # Columns: id, project_id, name, date_created, task_start_date, task_end_date, status, assigned_to_id
                    _, project_id, task_name, date_created, task_start_date, task_end_date, status, assigned_to_id = row

                    project = Project.objects.get(id=int(project_id))

                    touched_project_ids.add(int(project_id))

                    task = Task.objects.create(
                        name=task_name,
                        status=int(status),
                        project=project,
                        assigned_to_id=int(assigned_to_id),
                        task_start_date=datetime.strptime(task_start_date, "%d-%m-%Y").date(),
                        task_end_date=datetime.strptime(task_end_date, "%d-%m-%Y").date(),
                    )

                    # Manually set date_created if needed
                    task.date_created = datetime.strptime(date_created, "%d-%m-%Y").date()
                    task.save()

                except Exception as e:
                    messages.error(request, f"Error processing row {row}: {e}")
                    logger.exception(f"Error processing row {row}: {e}")

                    continue

            cache.delete("task_list_all_projects")
            if touched_project_ids:
                first_project_id = sorted(touched_project_ids)[0]
                cache.delete(f"task_list_project_{first_project_id}")

            messages.success(request, "Tasks have been uploaded successfully.")
            logger.info("Tasks have been uploaded successfully.")
            if touched_project_ids:
                first_project_id = sorted(touched_project_ids)[0]
                return redirect(f'/project/{first_project_id}/tasks/')
            return redirect('task_list')
    else:
        form = CSVUploadForm()
    
    # Corrected: redirect does not take context, and GET requests should usually return a template
    return render(request, 'task_list.html', {'form': form})
