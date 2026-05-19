from django.contrib import admin
from .models import Professor, Cronograma, Substituicao

from .models import (UserAuth, Aluno, Professor, Disciplina, Turma, Matricula, ConteudoCategoria,
                     ConteudoDisciplina, Aula, Substituicao, TemplateCronograma, TemplateCronogramaItem,
                     Cronograma, CronogramaItem, AgendamentoPostagem, AcompanhamentoItem)

admin.site.register(UserAuth)
admin.site.register(Aluno)
admin.site.register(Professor)

admin.site.register(Disciplina)
admin.site.register(Turma)
admin.site.register(Matricula)

admin.site.register(ConteudoCategoria)
admin.site.register(ConteudoDisciplina)
admin.site.register(Aula)
admin.site.register(Substituicao)

admin.site.register(TemplateCronograma)
admin.site.register(TemplateCronogramaItem)
admin.site.register(Cronograma)
admin.site.register(CronogramaItem)

admin.site.register(AgendamentoPostagem)
admin.site.register(AcompanhamentoItem)
