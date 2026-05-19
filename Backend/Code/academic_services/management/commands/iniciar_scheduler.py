import sys
from django.core.management.base import BaseCommand, call_command
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore


class Command(BaseCommand):
    help = "Inicia o scheduler pra enviar, em segundo plano, as tarefas agendadas"
    
    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        def tarefa_postagem():
            call_command('disparar_postagens')
        
        scheduler.add_job(
            tarefa_postagem,
            trigger = CronTrigger(minute="*/1"), #mudar pra CronTrigger(hour=6, minute=0) --> envia diariamente as 6am
            id="rotina_diaria_de_postagens",
            max_instances=1,
            replace_existing=True,
        )
        
        try: 
            self.stdout.write(self.style.SUCCESS("Iniciando o scheduler. Aperte Ctrl+C para interromper."))
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("Scheduler parado pelo usuario."))
            scheduler.shutdown()
            sys.exit(0)