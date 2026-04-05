from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, Group
from django.urls import reverse


# Create your models here.

class Client(models.Model):
    class Meta:
        permissions = (
            ('can_assign_task_to_client', 'Can Assign Task to Client'),
        )
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# class CustomUser(AbstractUser):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
#     related_groups = models.ManyToManyField(Group)


class Project(models.Model):
    STATUS = (
        (0, 'Not Started'),
        (1, 'In Progress'),
        (2, 'Completed')
    )
    name = models.CharField(max_length=255)
    Budget = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    description = models.TextField(editable=True)
    image = models.ImageField(blank=True, null=True)
    image_2 = models.ImageField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS = (
        (0, 'Not Started'),
        (1, 'In Progress'),
        (2, 'Completed')
    )
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    date_created = models.DateField(auto_now_add=True)
    task_start_date = models.DateField(null=True, blank=True)
    task_end_date = models.DateField(null=True, blank=True)
    
    status = models.IntegerField(choices=STATUS, default=0)
    assigned_to = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    def get_status_display(self):
        return dict(self.STATUS)[self.status]
    
    def get_absolute_url(self):
        return reverse('task_detail', args=[str(self.pk)])



