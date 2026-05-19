from django.db import models
from django.contrib.auth.models import AbstractUser


#Tirar dps esse comentario (modelo antigo) --> adaptar o codigo da views pra ficar compativel com o novo modelo de professor, cronograma e substituicao
"""
class Professor(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    materia = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    google_calendar_id = models.CharField(max_length=255, blank=True, help_text="ID da agenda Google do professor")
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.materia}"
    
    
    
class Cronograma(models.Model):
    materia = models.CharField(max_length=100)
    data_prevista = models.DateField()
    topico = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    postado_no_classroom = models.BooleanField(default=False)
    sala_classroom_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Cronograma"
        verbose_name_plural = "Cronogramas"
    
    def __str__(self):
        return f"{self.materia}: {self.topico} ({self.data_prevista})"
    
    

class Substituicao(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Recusada', 'Recusada'),
    ]
    
    aula_planejada = models.ForeignKey(Cronograma, on_delete=models.CASCADE)
    professor_solicitante = models.ForeignKey(Professor, related_name='solicitacoes', on_delete=models.CASCADE)
    professor_substituto = models.ForeignKey(Professor, related_name='substituicoes', null=True, blank=True, on_delete=models.SET_NULL)
    motivo = models.TextField()
    status_troca = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name = "Substituição"
        verbose_name_plural = "Substituições"
    
    def __str__(self):
        return f"Substituição: {self.aula_planejada} ({self.status_troca})"
    
"""    


class UserAuth(AbstractUser):
    TIPO_CHOICES = (
        ('G', 'Gestão'),
        ('A', 'Aluno'),
        ('P', 'Professor'),
    )
    
    tipo_user = models.CharField(max_length=1, choices=TIPO_CHOICES)
    
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)
    
    def __str__(self):
        return self.username
    

class Professor(models.Model):
    matricula = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    disponibilidade = models.TextField(blank=True, null=True)
    
    # ID usado pela automacao da conta pra saber em qual agenda especifica deve criar as aulas do professor
    google_calendar_id = models.CharField(max_length=255, blank=True, help_text="ID da agenda Google do professor")
    
    
    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricula})"
    

class Aluno(models.Model):
    matricula = models.CharField(max_length=20, primary_key=True)
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricula})"
    

#===================================================================
    
    
class Disciplina(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=100)
    nome_no_drive = models.CharField(max_length=100, blank=True, null=True)
    link_no_drive = models.URLField(blank=True, null=True)
    ementa_URL = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
    
    def __str__(self):
        return f"{self.nome} - {self.codigo}"    
    
    
class Turma(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True)
    id_classroom = models.CharField(max_length=255, blank=True, null=True)
    id_calendar = models.CharField(max_length=255, blank=True, null=True)
    planilha_URL = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        
    def __str__(self):
        return f"{self.codigo}"    
    

class Matricula(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='historico_matriculas')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_matricula = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('aluno', 'turma')
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
    
    
#===================================================================


class ConteudoCategoria(models.Model):
    nome = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "Categoria de Conteúdo"
        verbose_name_plural = "Categorias de Conteúdo"
    
    def __str__(self):
        return f"{self.nome}"
    
    
class ConteudoDisciplina(models.Model):
    categoria = models.ForeignKey(ConteudoCategoria, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    nome_no_drive = models.CharField(max_length=255)
    link_no_drive = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Conteúdo de Disciplina"
        verbose_name_plural = "Conteúdos de Disciplinas"
        
    def __str__(self):
        return f"{self.disciplina.nome} - {self.categoria.nome} - {self.nome_no_drive}"
    
    
class TemplateCronograma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Template: {self.disciplina.nome} - {self.titulo}"
    
class TemplateCronogramaItem(models.Model):
    template = models.ForeignKey(TemplateCronograma, on_delete=models.CASCADE)
    titulo_aula = models.CharField(max_length=255, help_text="Ex: 'Aula 1 - Introdução'")
    
    def __str__(self):
        return f"{self.template.disciplina.nome} - {self.titulo_aula}"
    

#===================================================================


class Cronograma(models.Model):
    template = models.ForeignKey(TemplateCronograma, on_delete=models.CASCADE, null=True, blank=True)
    turma = models.ForeignKey(Turma, related_name='cronogramas', on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    class Meta:
        verbose_name = "Cronograma da Turma"
        verbose_name_plural = "Cronogramas das Turmas"
        
    def __str__(self):
        return f"Cronograma: {self.turma.codigo} - {self.template.disciplina.nome}: {self.data_inicio} a {self.data_fim}"
    

class CronogramaItem(models.Model):
    cronograma = models.ForeignKey(Cronograma, on_delete=models.CASCADE)
    template_item = models.ForeignKey(TemplateCronogramaItem, on_delete=models.CASCADE)
    data_prevista_evento = models.DateField()
    conteudos = models.ManyToManyField(ConteudoDisciplina, related_name='cronograma_items', blank=True)
    
    class Meta:
        verbose_name = "Item do Cronograma"
        verbose_name_plural = "Itens do Cronograma"
    
    def __str__(self):
        return f"{self.template_item.titulo_aula} - {self.data_prevista_evento}"
    
    
class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    cronograma_item = models.ForeignKey(CronogramaItem, on_delete=models.SET_NULL, null=True, blank=True)
    
    prof_titular = models.ForeignKey(Professor, related_name='aulas_titular', on_delete=models.CASCADE)
    prof_real = models.ForeignKey(Professor, related_name='aulas_lecionadas', on_delete=models.CASCADE)
    
    data_hora = models.DateTimeField()
    google_event_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        
    def __str__(self):
        return f"Aula de {self.disciplina.nome} - Turma {self.turma.codigo} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"
    
    
class Substituicao(models.Model):
    STATUS_CHOICES = (
        ('Pendente', 'Pendente'),
        ('Confirmada', 'Confirmada'),
        ('Recusada', 'Recusada'),
    )
    
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    
    prof_titular = models.ForeignKey(Professor, related_name='substituicoes_solicitadas', on_delete=models.CASCADE)
    prof_subst = models.ForeignKey(Professor, related_name='substituicoes_aceitas', null=True, blank=True, on_delete=models.SET_NULL)
    
    motivo = models.TextField()
    status_troca = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Substituição de Aula"
        verbose_name_plural = "Substituições de Aulas"
        
    def __str__(self):
        return f"Substituição: {self.aula} ({self.status_troca})"
    
    
    
#===================================================================


class AcompanhamentoItem(models.Model):
    cronograma_item = models.OneToOneField(CronogramaItem, on_delete=models.CASCADE)
    data_conclusao = models.DateField(blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Acompanhamento"
        verbose_name_plural = "Acompanhamentos"


class AgendamentoPostagem(models.Model):
    cronograma_item = models.ForeignKey(CronogramaItem, on_delete=models.CASCADE)
    aprovacao_automatica = models.BooleanField(default=True)
    data_da_postagem = models.DateTimeField()
    
    id_post_classroom = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Agendamento de Postagem"
        verbose_name_plural = "Agendamentos de Postagem"
    
    
    