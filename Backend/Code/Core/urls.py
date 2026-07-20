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
from django.views.decorators.csrf import csrf_exempt
from social_django.views import auth as social_auth_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/<str:backend>/', csrf_exempt(social_auth_view), name='begin'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('auth/logout/', views.logout_view, name='logout'),
    path('api/perfil/', views.get_perfil, name='perfil'),
    path('api/agendamentos/', views.get_agendamentos, name='agendamentos'),
    path('api/disparar/<int:tarefa_id>/', views.enviar_agora, name='enviar_agora'),
    path('api/google-token/', views.get_google_token, name='google_token'),
    path('api/agendamentos/criar/', views.criar_agendamento, name='criar_agendamento'),
    path('api/gatilho-rotina/', views.gatilho_rotina_diaria, name='gatilho_rotina'),    
    path('api/turmas/', views.get_turmas, name='get_turmas'),
    path('api/disciplinas/', views.get_disciplinas, name='get_disciplinas'),
    path('api/agendamentos/<int:tarefa_id>/excluir/', views.excluir_agendamento, name='excluir_agendamento'),
    path('api/agendamentos/<int:tarefa_id>/editar/', views.editar_agendamento, name='editar_agendamento'),
    path('api/templates/', views.listar_templates, name='listar_templates'),
    path('api/templates/criar/', views.criar_template, name='criar_template'),
    path('api/templates/<int:template_id>/', views.get_template_detalhes, name='get_template_detalhes'),
    path('api/templates/<int:template_id>/excluir/', views.excluir_template, name='excluir_template'),
    path('api/templates/<int:template_id>/itens/', views.get_template_itens, name='get_template_itens'),
    path('api/templates/<int:template_id>/itens/criar/', views.criar_template_item, name='criar_template_item'),
    path('api/templates/itens/<int:item_id>/excluir/', views.excluir_template_item, name='excluir_template_item'),
    path('api/cronogramas/<str:turma_codigo>/<str:disciplina_codigo>/', views.get_cronograma_turma, name='get_cronograma_turma'),
    path('api/cronogramas/gerar/', views.criar_cronograma_turma, name='criar_cronograma_turma'),
    path('api/cronogramas/sincronizar/', views.sincronizar_calendario_turma, name='sincronizar_calendario_turma'),
    path('api/professores/lista/', views.get_professores_lista, name='get_professores_lista'),
    path('api/substituicoes/solicitar/', views.solicitar_substituicao, name='solicitar_substituicao'),
    path('api/substituicoes/recebidas/', views.get_convites_recebidos, name='get_convites_recebidos'),
    path('api/substituicoes/enviadas/', views.get_minhas_solicitacoes, name='get_minhas_solicitacoes'),
    path('api/substituicoes/<int:id_substituicao>/responder/', views.responder_substituicao, name='responder_substituicao'),
]