import pytest
from pmis.models import Client, Project, Task
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.
@pytest.fixture
def data_user():
    return {
    'username': 'testuser',
    'password': 'password123',
    'email': 'johndoe@example.com'
}

@pytest.fixture
def user(db, data_user)-> User:
    return User.objects.create_user(**data_user)

@pytest.fixture
def client(db, user):
    return Client.objects.create(user=user,
                                 first_name = 'John',
                                 last_name = 'Doe',
                                 email = 'johndoe@example.com')

@pytest.fixture
def project(db, client):
    return Project.objects.create(name='Test Project', Budget=1000.00, description='Test Description',
                                   start_date='2023-01-01', end_date='2023-12-31', client=client)


@pytest.mark.django_db
def test_client_model(db, client, user):

    assert client.user.username == 'testuser'
    assert client.first_name == 'John'
    assert client.last_name == 'Doe'
    assert client.email == 'johndoe@example.com'
    assert str(client) == 'testuser'

@pytest.mark.djnago_db
def test_project_model(project, client):

    assert project.name == 'Test Project'
    assert project.Budget == 1000.00
    assert project.description == 'Test Description'
    assert project.start_date == '2023-01-01'

    assert project.end_date == '2023-12-31'
    assert project.client == client
    assert str(project) == 'Test Project'


@pytest.mark.django_db
def test_task_model(db, project, client):

    task = Task.objects.create(project=project, name='Test Task', task_start_date='2023-01-01',
                                task_end_date='2023-01-31', assigned_to=client)

    assert task.project == project
    assert task.name == 'Test Task'
    assert task.task_start_date == '2023-01-01'
    assert task.task_end_date == '2023-01-31'
    assert task.assigned_to == client
