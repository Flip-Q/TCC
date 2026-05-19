from django.core.management.base import BaseCommand
from django.utils import timezone
from academic_services.models import AgendamentoPostagem
from academic_services.services.classroom_services import postar_material_aula

class Command(BaseCommand):
    help = 'Procura no banco de dados e dispara as postagens agendadas para o Google Classroom'
    
    def handle(self, *args, **kwargs):
        agora = timezone.now()
        
        self.stdout.write(f"[{agora.strftime('%d/%m/%Y %H:%M:%S')}] Procurando postagens agendadas...")
        
        agendamentos_pendentes = AgendamentoPostagem.objects.filter(
            data_da_postagem__lte = agora,
            id_post_classroom__isnull = True,   # n mandar 2 vezes a msm postagem
            aprovacao_automatica = True
        )
        
        if not agendamentos_pendentes.exists():
            self.stdout.write(self.style.SUCCESS("Nenhuma postagem pendente no momento."))
            return

        for agendamento in agendamentos_pendentes:
            self.stdout.write(f"Processando agendammento ID: {agendamento.id}...")
            
            cronograma_item = agendamento.cronograma_item
            turma = cronograma_item.cronograma.turma
            
            if not turma.id_classroom:
                self.stdout.write(self.style.ERROR(f"\t Turma {turma.codigo} não vinculada ao Google Classroom."))
                continue
            
            disciplina_nome = cronograma_item.cronograma.template.disciplina.nome
            titulo_aula = cronograma_item.template_item.titulo_aula
            
            titulo_post = titulo_aula
            descricao_post = f"Materiais e conteúdos programados para esta aula"
            
            conteudos = cronograma_item.conteudos.all()
            lista_links = [conteudo.link_no_drive for conteudo in conteudos if conteudo.link_no_drive]
            
            resposta = postar_material_aula(
                course_id=turma.id_classroom,
                titulo=titulo_post,
                descricao=descricao_post,
                links_materiais=lista_links
            )
            
            if resposta.get("Sucesso"):
                agendamento.id_post_classroom = resposta.get("post_id")
                agendamento.save()
                self.stdout.write(self.style.SUCCESS(f"\t Postagem criada com sucesso (Post ID: {agendamento.id_post_classroom})."))
            else:
                self.stdout.write(self.style.ERROR(f"\t Erro ao criar postagem: {resposta.get('erro')}"))
                
        self.stdout.write(self.style.SUCCESS("Processamento de postagens agendadas concluído."))