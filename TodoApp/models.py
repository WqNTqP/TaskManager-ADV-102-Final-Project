from django.db import models

class TaskMate_userDetails(models.Model):
    USER_ROLE_CHOICES = [
        ('user', 'User '),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=30, primary_key=True)
    fullName = models.CharField(max_length=60)
    email = models.EmailField(max_length=254, unique=True)  # Ensure email is unique
    mobileNumber = models.CharField(max_length=15)
    password = models.CharField(max_length=30)
    profilePic = models.ImageField(upload_to='media/', default='/images/user.png')
    bio = models.CharField(max_length=500, default='Hey there! I am using TaskMate.')
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='user')  # New role field

class TaskMate_taskDetails(models.Model):
    taskId = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50)
    deadlineDate = models.CharField(max_length=50)
    deadlineTime = models.CharField(max_length=50)
    priority = models.IntegerField()
    description = models.CharField(max_length=500)
    filename = models.CharField(max_length=300)
    status = models.CharField(max_length=20, default='Pending')  # Status field
    acceptedBy = models.CharField(max_length=50, blank=True, null=True)