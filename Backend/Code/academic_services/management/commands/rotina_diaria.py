from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Comando pra iniciar todas as rotinas diárias do sistema em sequência."
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("===== Iniciando rotina diária =====\n"))
        
        self.stdout.write(self.style.SUCCESS("Iniciando postagens do Classroom."))
        try:
            call_command('disparar_postagens')
            self.stdout.write(self.style.SUCCESS("\tRotina de postagens concluída com sucesso."))
            
        except Exception as e:  
            self.stdout.write(self.style.ERROR(f"\tErro durante a rotina de postagens: {str(e)}"))
           
        # Adicionar abaixo outros commands, como envio de emails, calendario, etc
        
        
        self.stdout.write(self.style.SUCCESS("\n===== Rotina Diária Concluída com Sucesso ====="))