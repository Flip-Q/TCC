"""
URL configuration for Core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from academic_services import views 
from django.urls import path, include
from django.contrib.auth import views as auth_views
from academic_services import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('social_django.urls', namespace='social')),
    path('auth/logout/', views.logout_view, name='logout'),
    path('api/perfil/', views.get_perfil, name='perfil'),
    path('api/agendamentos/', views.get_agendamentos, name='agendamentos'),
    path('api/disparar/<int:tarefa_id>/', views.enviar_agora, name='enviar_agora'),
    path('api/google-token/', views.get_google_token, name='google_token'),
    path('api/agendamentos/criar/', views.criar_agendamento, name='criar_agendamento'),
]