import os
import json
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.core.management import call_command
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

from .models import (
    AgendamentoPostagem, CronogramaItem, ConteudoDisciplina, Turma, Aula, Professor,
    ConteudoCategoria, Disciplina, Cronograma, TemplateCronogramaItem, TemplateCronograma,
    Substituicao
)
from .services.classroom_services import postar_material_aula

from social_django.models import UserSocialAuth
from google.oauth2.credentials import Credentials



def gatilho_rotina_diaria(request):
    token_enviado = request.GET.get('token')
    token_esperado = os.getenv('CRON_SECRET_KEY')
    
    if not token_esperado or token_enviado != token_esperado:
        return JsonResponse({'erro': 'Acesso negado. Token invalido.'}, status=403)
    
    try:
        call_command('rotina_diaria')
        return JsonResponse({'sucesso': True, 'mensagem': 'Rotina diaria concluida com sucesso.' })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


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
        disciplina_codigo = data.get('disciplina_codigo')
        
        turma = Turma.objects.get(codigo=turma_codigo)
        disciplina = Disciplina.objects.get(codigo=disciplina_codigo)
        
        cronograma_base = turma.cronogramas.filter(
            turma=turma,
            template__disciplina=disciplina
        ).first()
        
        if not cronograma_base:
            return JsonResponse({'error': f'Cronograma de {disciplina.nome} não encontrado para a turma {turma.codigo}.'}, status=400)
        
        novo_template_item = TemplateCronogramaItem.objects.create(
            template = cronograma_base.template,
            titulo_aula = data.get('assunto')
        )
        
        data_prevista_completa = data.get('data_prevista')
        data_prevista_dia = data_prevista_completa.split('T')[0]
        
        novo_cronograma_item = CronogramaItem.objects.create(
            cronograma = cronograma_base,
            template_item = novo_template_item,
            data_prevista_evento = data_prevista_dia
        )
        
        agendamento = AgendamentoPostagem.objects.create(
            cronograma_item=novo_cronograma_item,
            data_da_postagem=data_prevista_completa,
            aprovacao_automatica=True
        )
        
        categoria_padrao, _ = ConteudoCategoria.objects.get_or_create(nome='Material de Aula')
        arquivos = data.get('arquivos', [])
        
        for arquivo in arquivos:
            novo_conteudo = ConteudoDisciplina.objects.create(
                categoria=categoria_padrao,
                disciplina=disciplina,
                nome_no_drive=arquivo.get('nome'),
                link_no_drive=arquivo.get('url'),
            )
            novo_cronograma_item.conteudos.add(novo_conteudo)   
        return JsonResponse({'status': 'Sucesso', 'agendamento_id': agendamento.id})

    except Turma.DoesNotExist:
        return JsonResponse({'error': 'Turma não encontrada.'}, status=404)
    except Disciplina.DoesNotExist:
        return JsonResponse({'error': 'Disciplina não encontrada.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    """
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
        
    """

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
        cronograma_item = tarefa.cronograma_item
        turma = cronograma_item.cronograma.turma
        disciplina = cronograma_item.cronograma.template.disciplina
        
        arquivos = []
        for conteudo in cronograma_item.conteudos.all():
            arquivos.append({
                'nome': conteudo.nome_no_drive,
                'url': conteudo.link_no_drive
        })
        
        lista_tarefas.append({
            'id': tarefa.id,
            'materia': disciplina.nome,      # tarefa.cronograma_item.cronograma.template.disciplina.nome,
            'disciplina_codigo': disciplina.codigo,
            'turma_codigo': turma.codigo,
            'assunto': tarefa.cronograma_item.template_item.titulo_aula,
            'data_prevista': tarefa.data_da_postagem,
            'status': 'Postado' if tarefa.id_post_classroom else 'Pendente',
            'arquivos': arquivos
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


@login_required
def get_turmas(request):
    try:
        turmas = Turma.objects.all().values('codigo')
        return JsonResponse(list(turmas), safe=False)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)
    
@login_required
def get_disciplinas(request):
    try:
        disciplinas = Disciplina.objects.all().values('codigo', 'nome')
        return JsonResponse(list(disciplinas), safe=False)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def excluir_agendamento(request, tarefa_id):
    try: 
        agendamento = AgendamentoPostagem.objects.get(id=tarefa_id)
        # agendamento.cronograma_item.delete()  # se quiser deletar o item do cronograma junto
        agendamento.delete()
        return JsonResponse({'sucesso': True, 'mensagem': 'Agendamento excluído com sucesso.'})
    
    except AgendamentoPostagem.DoesNotExist:
        return JsonResponse({'erro': 'Agendamento não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)

@csrf_exempt
@require_POST
@login_required
def editar_agendamento(request, tarefa_id):
    try:
        data = json.loads(request.body)
        agendamento = AgendamentoPostagem.objects.get(id=tarefa_id)
        cronograma_item = agendamento.cronograma_item
        
        if 'data_prevista' in data and data['data_prevista']:
            agendamento.data_da_postagem = data.get('data_prevista')
            agendamento.save()
            
        if 'assunto' in data and data['assunto']:
            template_item = cronograma_item.template_item
            template_item.titulo_aula = data.get('assunto')
            template_item.save()
            
        turma_codigo = data.get('turma_codigo')
        disciplina_codigo = data.get('disciplina_codigo')
        
        if turma_codigo and disciplina_codigo:
            turma = Turma.objects.get(codigo=turma_codigo)
            disciplina = Disciplina.objects.get(codigo=disciplina_codigo)
            
            novo_cronograma_base = turma.cronogramas.filter(
                turma=turma,
                template__disciplina=disciplina
            ).first()
            
            if not novo_cronograma_base:
                return JsonResponse({'erro': f'Cronograma não encontrado para a turma {turma.codigo} e disciplina {disciplina.codigo}.'}, status=400)
            
            if cronograma_item.cronograma != novo_cronograma_base:
                cronograma_item.cronograma = novo_cronograma_base
                cronograma_item.save()
        
        if 'arquivos' in data:
            cronograma_item.conteudos.clear()
            
            arquivos = data.get('arquivos', [])
            if arquivos:
                categoria_padrao, _ = ConteudoCategoria.objects.get_or_create(nome='Material de Aula')
                disciplina_atual = cronograma_item.cronograma.template.disciplina
                
                for arquivo in arquivos:
                    conteudo = ConteudoDisciplina.objects.filter(link_no_drive=arquivo.get('url')).first()
                        
                    # Se não existir nenhum, aí sim ele cria um novinho
                    if not conteudo:
                        conteudo = ConteudoDisciplina.objects.create(
                            nome_no_drive=arquivo.get('nome'),
                            link_no_drive=arquivo.get('url'),
                            categoria=categoria_padrao,
                            disciplina=disciplina_atual
                        )
                
                #    conteudo, _ = ConteudoDisciplina.objects.get_or_create(
                #        link_no_drive=arquivo.get('url'),
                #        defaults={
                #            'nome_no_drive': arquivo.get('nome'),
                #            'categoria': categoria_padrao,
                #            'disciplina': disciplina_atual
                #        }
                #    )
                    cronograma_item.conteudos.add(conteudo)
        
        return JsonResponse({'sucesso': True, 'mensagem': 'Agendamento atualizado com sucesso.'})
    
    except Turma.DoesNotExist:
        return JsonResponse({'erro': 'Turma não encontrada.'}, status=404)
    except Disciplina.DoesNotExist:
        return JsonResponse({'erro': 'Disciplina não encontrada.'}, status=404)
    except AgendamentoPostagem.DoesNotExist:
        return JsonResponse({'erro': 'Agendamento não encontrado.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)



def listar_templates(request):
    if request.method == 'GET': 
        templates = list(TemplateCronograma.objects.select_related('disciplina').values(
            'id', 'titulo', 'disciplina__nome'
        ))
        
        dados_formatados = [
            {'id': t['id'], 'nome': f"{t['disciplina__nome']} - {t['titulo']}"} 
            for t in templates
        ]
    
        return JsonResponse(dados_formatados, safe=False)

@csrf_exempt
def criar_template(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            titulo_template = data.get('titulo')
            disciplina_codigo = data.get('disciplina_codigo')
            
            if not titulo_template or not disciplina_codigo:
                return JsonResponse({'erro': 'Título e disciplina são obrigatórios.'}, status=400)
            
            disciplina_instancia = Disciplina.objects.get(codigo=disciplina_codigo)
            
            novo_template = TemplateCronograma.objects.create(
                titulo=titulo_template,
                disciplina=disciplina_instancia
            )
            
            nome_completo = f"{disciplina_instancia.nome} - {novo_template.titulo}"
            return JsonResponse({'id': novo_template.id, 'nome': nome_completo}, status=201)

        except Disciplina.DoesNotExist:
            return JsonResponse({'erro': 'Disciplina não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def excluir_template(request, template_id):
    try: 
        template = TemplateCronograma.objects.get(id=template_id)
        template.delete()
        return JsonResponse({'sucesso': True, 'mensagem': 'Template excluído com sucesso.'})
    
    except TemplateCronograma.DoesNotExist:
        return JsonResponse({'erro': 'Template não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)
    

@login_required
def get_template_detalhes(request, template_id):
    try:
        template = TemplateCronograma.objects.get(id=template_id)
        return JsonResponse({'id': template.id, 'titulo': template.titulo})
    except TemplateCronograma.DoesNotExist:
        return JsonResponse({'erro': 'Template não encontrado.'}, status=404)
    
@login_required
def get_template_itens(request, template_id):
    try:
        itens = TemplateCronogramaItem.objects.filter(template_id=template_id).order_by('id').values('id', 'titulo_aula')
        return JsonResponse(list(itens), safe=False)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)
    
@csrf_exempt
@require_POST
@login_required
def criar_template_item(request, template_id):
    try:
        data = json.loads(request.body)
        titulo_aula = data.get('titulo_aula')
        
        if not titulo_aula:
            return JsonResponse({'erro': 'O título da aula é obrigatório.'}, status=400)
        
        template = TemplateCronograma.objects.get(id=template_id)
        
        novo_item = TemplateCronogramaItem.objects.create(
            template=template,
            titulo_aula=titulo_aula
        )
        
        return JsonResponse({'id': novo_item.id, 'titulo_aula': novo_item.titulo_aula}, status=201)
    
    except TemplateCronograma.DoesNotExist:
        return JsonResponse({'erro': 'Template não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)
    

@csrf_exempt
@require_POST
@login_required
def excluir_template_item(request, item_id):
    try:
        item = TemplateCronogramaItem.objects.get(id=item_id)
        item.delete()
        return JsonResponse({'sucesso': True, 'mensagem': 'Aula excluida com sucesso.'})
    except TemplateCronogramaItem.DoesNotExist:
        return JsonResponse({'erro': 'Aula não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)



@csrf_exempt
@require_POST
@login_required
def criar_cronograma_turma(request):
    try:
        data = json.loads(request.body)
        turma_codigo = data.get('turma_codigo')
        disciplina_codigo = data.get('disciplina_codigo')
        data_inicio_str = data.get('data_inicio')
        data_fim_str = data.get('data_fim')
        
        if not all([turma_codigo, disciplina_codigo, data_inicio_str, data_fim_str]):
            return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)
        
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        turma = Turma.objects.get(codigo=turma_codigo)
        disciplina = Disciplina.objects.get(codigo=disciplina_codigo)
        
        template = TemplateCronograma.objects.filter(disciplina=disciplina).first()
        if not template:
            return JsonResponse({'erro': 'Não há template cadastrado para esta disciplina.'}, status=400)
        
        Cronograma.objects.filter(turma=turma, template__disciplina=disciplina).delete()
        
        cronograma = Cronograma.objects.create(
            template=template,
            turma=turma,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        itens_template = TemplateCronogramaItem.objects.filter(template=template).order_by('id')
        
        feriados_datas = set()
        caminho_feriados = os.path.join(settings.BASE_DIR, 'academic_services', 'data', 'feriados.json')
        
        if os.path.exists(caminho_feriados):
            with open(caminho_feriados, 'r', encoding='utf-8') as arq_feriados:
                feriados = json.load(arq_feriados)
                for item in feriados:
                    data_obj = datetime.strptime(item['data'], '%Y-%m-%d').date()
                    feriados_datas.add(data_obj)
        else:
            print("Aviso: Arquivo 'feriados.json' não encontrado. Feriados não serão pulados.")
            
        data_atual = data_inicio
        index_aula = 0
        total_aulas = len(itens_template)
        
        while index_aula < total_aulas and data_atual <= data_fim:
            if data_atual.weekday() < 5 and data_atual not in feriados_datas:
                CronogramaItem.objects.create(
                    cronograma=cronograma,
                    template_item=itens_template[index_aula], 
                    data_prevista_evento=data_atual
                )
                index_aula += 1
            data_atual += timedelta(days=7)
        
        if index_aula < total_aulas:
            aviso = f"Cronograma criado, mas o periodo selecionado terminou antes de todas as aulas serem alocadas. {total_aulas - index_aula} aulas restantes sem data prevista."
            return JsonResponse({'erro': aviso}, status=400)
        
        return JsonResponse({'sucesso': True, 'mensagem': 'Cronograma criado com sucesso.'}, status=201)
    
    except Turma.DoesNotExist:
        return JsonResponse({'erro': 'Turma não encontrada.'}, status=404)
    except Disciplina.DoesNotExist:
        return JsonResponse({'erro': 'Disciplina não encontrada.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)
    

@login_required
def get_cronograma_turma(request, turma_codigo, disciplina_codigo):
    try:
        cronograma = Cronograma.objects.filter(
            turma__codigo=turma_codigo,
            template__disciplina__codigo=disciplina_codigo
        ).first()
        
        if not cronograma:
            return JsonResponse([], safe=False)
        
        itens = CronogramaItem.objects.filter(cronograma=cronograma).order_by('data_prevista_evento')
        
        lista_aulas = []
        for item in itens:
            aula_oficial = Aula.objects.filter(cronograma_item=item).first()
            
            if aula_oficial:
                id_para_front = aula_oficial.id
                nome_prof = aula_oficial.prof_real.user.get_full_name() or aula_oficial.prof_real.user.username
                sincronizado = True
            else:
                id_para_front = item.id
                nome_prof = 'Aguardando sincronização do Calendar'
                sincronizado = False
            
            lista_aulas.append({
                'id': id_para_front,
                'data': item.data_prevista_evento,
                'titulo': item.template_item.titulo_aula,
                'professor': nome_prof,
                'sincronizado': sincronizado
            })

        return JsonResponse(lista_aulas, safe=False)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)



@csrf_exempt
@require_POST
@login_required
def sincronizar_calendario_turma(request):
    try:
        data = json.loads(request.body)
        turma_codigo = data.get('turma_codigo')
        disciplina_codigo = data.get('disciplina_codigo')
        hora_inicio_str = data.get('hora_inicio')           # formato esperado: "HH:MM"
        hora_fim_str = data.get('hora_fim')                 # formato esperado: "HH:MM"
        
        if not all([turma_codigo, disciplina_codigo, hora_inicio_str, hora_fim_str]):
            return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)
        
        turma = Turma.objects.get(codigo=turma_codigo)
        disciplina = Disciplina.objects.get(codigo=disciplina_codigo)
        
        try:
            professor = request.user.professor
        except Exception:
            return JsonResponse({'erro': 'Usuário não é um professor.'}, status=403)
        
        cronograma = Cronograma.objects.filter(turma=turma, template__disciplina=disciplina).first()
        
        if not cronograma:
            return JsonResponse({'erro': 'Cronograma não encontrado.'}, status=404)
        
        itens = CronogramaItem.objects.filter(cronograma=cronograma).order_by('data_prevista_evento')
        
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
        
        matriculas = turma.matricula_set.select_related('aluno__user').all()
        lista_email_alunos = []
        for matricula in matriculas:
            email_aluno = matricula.aluno.user.email
            if email_aluno:
                lista_email_alunos.append({'email': email_aluno})
        
        service = build('calendar', 'v3', credentials=creds)
        fuso_horario_str = 'America/Sao_Paulo'
        import pytz
        fuso = pytz.timezone(fuso_horario_str)
        eventos_criados = 0
        
        for item in itens:
            data_str = item.data_prevista_evento.strftime('%Y-%m-%d')
            start_datetime = f"{data_str}T{hora_inicio_str}:00"
            end_datetime = f"{data_str}T{hora_fim_str}:00"
            
            evento = {
                'summary': f"[{turma.codigo}] {disciplina.nome} - {item.template_item.titulo_aula}",
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': fuso_horario_str,
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': fuso_horario_str,
                },
                'attendees': lista_email_alunos
            }
            
            evento_criado_calendar = service.events().insert(
                calendarId='primary',
                sendUpdates='none', 
                body=evento
            ).execute()
            
            id_evento_calendar = evento_criado_calendar.get('id')
            
            data_hora_obj = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M:%S')
            data_hora_aware = timezone.make_aware(data_hora_obj, timezone=fuso)
            
            Aula.objects.create(
                turma=turma,
                disciplina=disciplina,
                cronograma_item=item,
                prof_titular=professor,
                prof_real=professor,
                data_hora=data_hora_aware,
                google_event_id=id_evento_calendar
            )
            
            eventos_criados += 1
        
        return JsonResponse({'sucesso': True, 'mensagem': f'{eventos_criados} aulas adicionadas ao Calendar com sucesso.'})
        
    except Turma.DoesNotExist:
        return JsonResponse({'erro': 'Turma não encontrada.'}, status=404)
    except Disciplina.DoesNotExist:
        return JsonResponse({'erro': 'Disciplina não encontrada.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)

@login_required
def get_professores_lista(request):
    try:
        professores = Professor.objects.exclude(user=request.user).select_related('user')
        
        lista = []
        for prof in professores:
            nome = prof.user.get_full_name() or prof.user.username
            lista.append({'matricula': prof.matricula, 'nome': nome})

        return JsonResponse(lista, safe=False)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)
    
@csrf_exempt
@require_POST
@login_required
def solicitar_substituicao(request): 
    try: 
        data = json.loads(request.body)
        aulas_ids = data.get('aulas_ids', [])
        prof_substituto_matricula = data.get('prof_substituto_matricula')
        motivo = data.get('motivo')
        
        if not aulas_ids or not prof_substituto_matricula or not motivo:
            return JsonResponse({'erro': 'Dados incompletos.'}, status=400)
        
        prof_solicitante = request.user.professor
        prof_substituto = Professor.objects.get(matricula=prof_substituto_matricula)
        
        for aula_id in aulas_ids:
            aula = Aula.objects.get(id=aula_id)
            Substituicao.objects.create(
                aula=aula,
                prof_titular=prof_solicitante,
                prof_subst=prof_substituto,
                motivo=motivo,
                status_troca='Pendente'
            )
        
        return JsonResponse({'sucesso': True, 'mensagem': f'Solicitação enviada para {prof_substituto.user.first_name}.'}, status=201)

    except Professor.DoesNotExist:
        return JsonResponse({'erro': 'Professor substituto não encontrado.'}, status=404)
    except Aula.DoesNotExist:
        return JsonResponse({'erro': 'Uma ou mais aulas não foram encontradas.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)

@login_required
def get_convites_recebidos(request):
    try:
        professor = request.user.professor
        
        convites = Substituicao.objects.filter(
            prof_subst=professor,
            status_troca='Pendente'
        ).select_related('aula', 'prof_titular__user', 'aula__disciplina', 'aula__turma', 'aula__cronograma_item__template_item')
        
        lista = []
        for convite in convites:
            nome_solicitante = convite.prof_titular.user.get_full_name() or convite.prof_titular.user.username
            lista.append({
                'id': convite.id,
                'turma': convite.aula.turma.codigo,
                'disciplina': convite.aula.disciplina.nome,
                'titulo_aula': convite.aula.cronograma_item.template_item.titulo_aula,
                'data_aula': convite.aula.data_hora.strftime('%d/%m/%Y às %H:%M'),
                'prof_solicitante': nome_solicitante,
                'motivo': convite.motivo
            })
        
        return JsonResponse(lista, safe=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)
    

@login_required
def get_minhas_solicitacoes(request):
    try:
        professor = request.user.professor
        
        solicitacoes = Substituicao.objects.filter(
            prof_titular=professor
        ).select_related('aula', 'prof_subst__user', 'aula__disciplina', 'aula__turma', 'aula__cronograma_item__template_item')
        
        lista = []
        for sol in solicitacoes:
            nome_substituto = sol.prof_subst.user.get_full_name() or sol.prof_subst.user.username
            lista.append({
                'id': sol.id,
                'turma': sol.aula.turma.codigo,
                'disciplina': sol.aula.disciplina.nome,
                'titulo_aula': sol.aula.cronograma_item.template_item.titulo_aula,
                'data_aula': sol.aula.data_hora.strftime('%d/%m/%Y às %H:%M'),
                'prof_substituto': nome_substituto,
                'motivo': sol.motivo,
                'status': sol.status_troca
            })
        
        return JsonResponse(lista, safe=False)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)
    
    
@csrf_exempt
@require_POST
@login_required
def responder_substituicao(request, id_substituicao):
    try:
        data = json.loads(request.body)
        novo_status = data.get('status')
        
        if novo_status not in ['Aceito', 'Recusado']:
            return JsonResponse({'erro': 'Status inválido.'}, status=400)
        
        substituicao = Substituicao.objects.get(
            id=id_substituicao,
            prof_subst=request.user.professor,
            status_troca='Pendente'
        )

        substituicao.status_troca = novo_status
        substituicao.save()
        
        if novo_status == 'Aceito':
            aula = substituicao.aula
            aula.prof_real = substituicao.prof_subst
            aula.save()
            
            if aula.google_event_id:
                try:
                    titular_social = substituicao.prof_titular.user.social_auth.get(provider='google-oauth2')
                    token_data = titular_social.extra_data
                    
                    creds = Credentials(
                        token=token_data.get('access_token'),
                        refresh_token=token_data.get('refresh_token'),
                        token_uri='https://oauth2.googleapis.com/token',
                        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                        client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                        scopes=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE
                    )
                    
                    service = build('calendar', 'v3', credentials=creds)
                    
                    evento = service.events().get(calendarId='primary', eventId=aula.google_event_id).execute()
                    
                    email_substituto = request.user.email
                    attendees = evento.get('attendees', [])
                    
                    if not any(a.get('email') == email_substituto for a in attendees):  # se o subst n tiver na lista, adiciona
                        attendees.append({'email': email_substituto, 'responseStatus': 'accepted'})
                        evento['attendees'] = attendees
                        
                    service.events().update(
                        calendarId='primary',
                        eventId=aula.google_event_id,
                        body=evento,
                        sendUpdates='none'
                    ).execute()
                except Exception as e:
                    print(f"Erro ao atualizar o Google Calendar: {e}")
                    
            mensagem = 'Convite aceito com sucesso! A aula foi transferida para você.'
        else:
            mensagem = 'Convite recusado com sucesso.'
            
        return JsonResponse({'sucesso': True, 'mensagem': mensagem})
    
    except Substituicao.DoesNotExist:
        return JsonResponse({'erro': 'Convite não encontrado ou já processado.'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'erro': str(e)}, status=500)




