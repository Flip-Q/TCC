import os
import json
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_exempt

from .models import AgendamentoPostagem, CronogramaItem, ConteudoDisciplina, Turma, ConteudoCategoria
from .services.classroom_services import postar_material_aula

from social_django.models import UserSocialAuth
from google.oauth2.credentials import Credentials



@login_required
def get_google_token(request):
    try:
        social_user = request.user.social_auth.get(provider='google-oauth2')
        return JsonResponse({
            'access_token': social_user.extra_data.get('access_token'),
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'api_key': settings.GOOGLE_PICKER_API_KEY
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    
@csrf_exempt
@require_POST
@login_required
def criar_agendamento(request):
    try:
        data = json.loads(request.body)
        
        turma_codigo = data.get('turma_codigo')
        turma = Turma.objects.get(codigo=turma_codigo)
        
        cronograma_item = CronogramaItem.objects.filter(cronograma__turma=turma).first()
        
        if not cronograma_item:
            return JsonResponse({'error': 'Nenhum item de cronograma ativo encontrado para esta turma.'}, status=400)
        
        data_postagem = data.get('data_prevista')
        agendamento = AgendamentoPostagem.objects.create(
            cronograma_item=cronograma_item,
            data_da_postagem=data_postagem
        )
        
        categoria_padrao, created = ConteudoCategoria.objects.get_or_create(nome='Material de Aula')
        
        arquivos = data.get('arquivos', [])
        for arquivo in arquivos:
            novo_conteudo = ConteudoDisciplina.objects.create(
                categoria=categoria_padrao,
                disciplina=cronograma_item.cronograma.template.disciplina,
                nome_no_drive=arquivo.get('nome'),
                link_no_drive=arquivo.get('url'),
            )
            cronograma_item.conteudos.add(novo_conteudo)
        
        return JsonResponse({'status': 'Sucesso', 'agendamento_id': agendamento.id})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def logout_view(request):
    django_logout(request)
    return redirect(settings.LOGIN_ERROR_URL)


@login_required
def get_perfil(request):
    return JsonResponse({
        'nome': request.user.first_name or request.user.username
    })


@login_required
def get_agendamentos(request):  
    tarefas = AgendamentoPostagem.objects.all().order_by('data_da_postagem')
    
    lista_tarefas = []
    for tarefa in tarefas:
        lista_tarefas.append({
            'id': tarefa.id,
            'materia': tarefa.cronograma_item.cronograma.template.disciplina.nome,
            'assunto': tarefa.cronograma_item.template_item.titulo_aula,
            'data_prevista': tarefa.data_da_postagem,
            'status': 'Postado' if tarefa.id_post_classroom else 'Pendente'
        })
    
    return JsonResponse(lista_tarefas, safe=False)

@csrf_exempt
@require_POST
@login_required
def enviar_agora(request, tarefa_id):
    try:
        agendamento = AgendamentoPostagem.objects.get(id=tarefa_id)
        cronograma_item = agendamento.cronograma_item
        turma = cronograma_item.cronograma.turma
        
        if not turma.id_classroom:
            return JsonResponse({'erro': 'Turma não vinculada ao Google Classroom.'}, status=400)
        
        social_user = request.user.social_auth.get(provider='google-oauth2')
        token_data = social_user.extra_data
        
        creds = Credentials(
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE
        )
        
        disciplina_nome = cronograma_item.cronograma.template.disciplina.nome
        titulo_aula = cronograma_item.template_item.titulo_aula
        titulo_post = titulo_aula
        
        conteudos = cronograma_item.conteudos.all()
        lista_links = [conteudo.link_no_drive for conteudo in conteudos if conteudo.link_no_drive]
        
        print(f"LINKS QUE SERÃO ENVIADOS: {lista_links}")
        
        resposta = postar_material_aula(
            creds=creds,
            course_id=turma.id_classroom,
            titulo=titulo_post,
            descricao=f"Materiais e conteúdos programados para esta aula",
            links_materiais=lista_links
        )
        
        
        if resposta.get("Sucesso"):
            agendamento.id_post_classroom = resposta.get("post_id")
            agendamento.save()
            return JsonResponse({'status': 'Sucesso', 'post_id': agendamento.id_post_classroom})
        else:
            return JsonResponse({'erro': resposta.get('erro')}, status=500)       
    
    except AgendamentoPostagem.DoesNotExist:
        return JsonResponse({'erro': 'Agendamento não encontrado.'}, status=404)  
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)































