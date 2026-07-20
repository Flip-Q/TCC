import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Data } from '../services/data';

@Component({
  selector: 'app-cronograma-turma',
  imports: [CommonModule, FormsModule],
  templateUrl: './cronograma-turma.html',
  styleUrl: './cronograma-turma.css',
})
export class CronogramaTurma implements OnInit{
  private data = inject(Data);

  protected listaTurmas = signal<any[]>([]);
  protected listaDisciplinas = signal<any[]>([]);
  protected listaAulas = signal<any[]>([]);
  protected listaProfessores = signal<any[]>([]);
  protected aulasSelecionadas: number[] = [];
 

  protected turmaSelecionada = '';
  protected disciplinaSelecionada = '';
  protected horaInicioPadrao = '';
  protected horaFimPadrao = '';
  protected professorSubstitutoId = '';
  protected motivoSubstituicao = '';
  protected buscou = false;
  protected mostrarModal = false;
  
  ngOnInit() {
    this.buscarTurmas();
    this.buscarDisciplinas();
    this.carregarProfessores();
  }

  buscarTurmas() {
    this.data.getTurmas().subscribe({
      next: (dados) => this.listaTurmas.set(dados),
      error: (err) => console.error('Erro ao buscar turmas:', err)
    });
  }

  buscarDisciplinas() {
    this.data.getDisciplinas().subscribe({
      next: (dados) => this.listaDisciplinas.set(dados),
      error: (err) => console.error('Erro ao buscar disciplinas:', err)
    });
  }

  buscarCronograma() {
    if (!this.turmaSelecionada || !this.disciplinaSelecionada) return;

    this.buscou = true;

    this.data.getCronogramaReal(this.turmaSelecionada, this.disciplinaSelecionada).subscribe({
      next: (dados) => this.listaAulas.set(dados),
      error: (err) => {
        console.error('Erro ao buscar cronograma:', err);
        this.listaAulas.set([]);
      }
    });
  }

  /**
  sincronizarComCalendar() {
    if (confirm('Deseja agendar todas as aulas no Google Calendar?')) {
      this.data.sicronizarCalendarioTurma(this.turmaSelecionada, this.disciplinaSelecionada).subscribe({
        next: (res) => alert('Sinconizacao concluida com sucesso! Eventos criados.'),
        error: (err) => alert('Erro ao sincronizar: ' + (err.error?.erro || 'Erro no servidor'))
      });
    }
  }
  */
  sincronizarComCalendar() {
    if (!this.horaInicioPadrao || !this.horaFimPadrao) return;

    if (confirm('Deseja agendar todas as aulas no Google Calendar?')) {
      const payload = {
        turma_codigo: this.turmaSelecionada, 
        disciplina_codigo: this.disciplinaSelecionada,
        hora_inicio: this.horaInicioPadrao,
        hora_fim: this.horaFimPadrao
      };

      this.data.sincronizarCalendarioTurma(payload).subscribe({
        next: (res: any) => {
          alert('Sincronização concluída com sucesso! Eventos criados.');
        },
        error: (err: any) => {
          alert('Erro ao sincronizar: ' + (err.error?.erro || 'Erro interno do servidor'));
        }
      });
    }
  }

  protected toggleSelecaoAula(aulaId: number) {
    const index = this.aulasSelecionadas.indexOf(aulaId);
    if (index === -1) {
      this.aulasSelecionadas.push(aulaId);     // Se não tiver na lista, adiciona
    }
    else {
      this.aulasSelecionadas.splice(index, 1); // Se tiver na lista, remove
    }
  }

  protected todasSelecionadas(): boolean {
    const aulas = this.listaAulas();
    return aulas.length > 0 && this.aulasSelecionadas.length === aulas.length;
  }

  protected toggleSelecionarTodas() {
    if (this.todasSelecionadas()) {
      this.aulasSelecionadas = [];
    }
    else {
      this.aulasSelecionadas = this.listaAulas().map(aula => aula.id);
    }
  }

  protected abrirModalSubstituicao() {
    this.professorSubstitutoId = '';
    this.motivoSubstituicao = '';
    this.mostrarModal = true;
  }

  protected fecharModalSubstituicao() {
    this.mostrarModal = false;
  }

  protected confirmarSubstituicao() {
    const payload = {
      aulas_ids: this.aulasSelecionadas,
      prof_substituto_matricula: this.professorSubstitutoId,
      motivo: this.motivoSubstituicao
    };

    this.data.solicitarSubstituicao(payload).subscribe({
      next: (res) => {
        alert(res.mensagem);
        this.fecharModalSubstituicao();
        this.aulasSelecionadas = [];    
      },
      error: (err) => {
        console.error('Erro ao solicitar substituição:', err);
        alert('Erro ao processar sua solicitação.')
      }
    });
   
  }

  protected carregarProfessores() {
    this.data.getProfessoresLista().subscribe({
      next: (dados) => this.listaProfessores.set(dados),
      error: (err) => console.error('Erro ao carregar lista de professores:', err)
    });
  }


}
