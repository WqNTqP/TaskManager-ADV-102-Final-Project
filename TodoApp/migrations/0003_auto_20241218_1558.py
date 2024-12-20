# Generated by Django 3.2.19 on 2024-12-18 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TodoApp', '0002_taskmate_taskdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskmate_userdetails',
            name='role',
            field=models.CharField(choices=[('user', 'User '), ('admin', 'Admin')], default='user', max_length=10),
        ),
        migrations.AlterField(
            model_name='taskmate_userdetails',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
