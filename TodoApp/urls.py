from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from TodoApp import views
from .views import userDashboard, acceptTask  
from .views import userDashboard, finishTask  


urlpatterns = [
    path('',views.login , name='login'),
    path('homepage/',views.homepage , name='homepage'),
    path('signUp/',views.signUp , name='signUp'),
    path('resetPassword/',views.resetPassword , name='resetPassword'),
    path('profilePage/',views.profilePage , name='profilePage'),
    path('delete/<int:idd>',views.delete,name='delete'),
    path('edit/<int:idd>',views.editTodo,name='editTodo'),
    path('logOut/',views.logOut , name='logOut'),
    path('myday/', views.myDayView, name='myday'),
    path('userDashboard/', views.userDashboard, name='userDashboard'),
    path('acceptTask/<int:task_id>/', acceptTask, name='acceptTask'),
    path('cancelTask/<int:task_id>/', views.cancelTask, name='cancelTask'),
    path('finishTask/<int:task_id>/', finishTask, name='finishTask'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()