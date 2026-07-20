import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Data } from '../services/data';


@Component({
  selector: 'app-cronograma',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cronograma.html',
  styleUrl: './cronograma.css'
})
export class Cronograma implements OnInit {
  private data = inject(Data);
  private router = inject(Router);

  protected exibirModal = signal(false);
  protected exibirModalNovoTemplate = signal(false);

  protected listaTurmas = signal<any[]>([]);
  protected listaDisciplinas = signal<any[]>([]);
  protected listaTemplates = signal<any[]>([]);

  protected turmaSelecionada = '';
  protected disciplinaSelecionada = '';
  protected dataInicio = '';
  protected dataFim = '';
  protected novoTemplateTitulo = '';
  protected novoTemplateDisciplina = '';

  ngOnInit() {
    this.buscarTurmas();
    this.buscarDisciplinas();
    this.buscarTemplates();
  }

  irParaItens(templateId: number) {
    this.router.navigate(['/cronograma/itens', templateId]);
  }

  irParaCronogramaReal() {
    this.router.navigate(['/cronograma-real']);
  }

  buscarTurmas() {
    this.data.getTurmas().subscribe({
      next: (dados) => this.listaTurmas.set(dados), 
      error: (err) => console.error('Erro ao obter turmas:', err)
    });
  }

  buscarDisciplinas() {
    this.data.getDisciplinas().subscribe({
      next: (dados) => this.listaDisciplinas.set(dados),
      error: (err) => console.error('Erro ao obter disciplinas:', err)
    });
  }

  buscarTemplates() {
    this.data.getTemplates().subscribe({
      next: (dados) => this.listaTemplates.set(dados),
      error: (err) => console.error('Erro ao obter templates:', err)
    });
  }

  abrirModalNovoTemplate() {
    this.exibirModalNovoTemplate.set(true);
  }

  fecharModalNovoTemplate() {
    this.exibirModalNovoTemplate.set(false);
    this.novoTemplateTitulo = '';
    this.novoTemplateDisciplina = '';
  }

  salvarNovoTemplate() {
    const payload = {
      titulo: this.novoTemplateTitulo,
      disciplina_codigo: this.novoTemplateDisciplina
    };

    this.data.criarTemplate(payload).subscribe({
      next: () => {
        alert('Template criado com sucesso!');
        this.fecharModalNovoTemplate();
        this.buscarTemplates();
      },
      error: (err: any) => alert('Erro ao criar template: ' + (err.error?.erro || 'Erro interno do servidor'))
    });
  }

  excluirTemplate(templateId: number) {
    if (confirm('Tem certeza que deseja excluir este template? Todos os itens dentro dele também serão apagados.')) {
      this.data.excluirTemplate(templateId).subscribe({
        next: () => {
          this.buscarTemplates();
        },
        error: (err: any) => {
          alert('Erro ao excluir template: ' + (err.error?.erro || 'Erro interno do servidor'));
        }
      });
    }
  }

  abrirModal() {
    this.exibirModal.set(true);
  }

  fecharModal() {
    this.exibirModal.set(false);
    this.limparFormulario();
  }

  private limparFormulario() {
    this.turmaSelecionada = '';
    this.disciplinaSelecionada = '';
    this.dataInicio = '';
    this.dataFim = '';
  }

  private finalizarCriacaoCronograma(msg: string) {
    alert(msg);
    this.exibirModal.set(false);
    //this.buscarTemplates();
    this.limparFormulario();
    this.irParaCronogramaReal();
  }

  gerarCronograma() {
    const payload = {
      turma_codigo: this.turmaSelecionada,
      disciplina_codigo: this.disciplinaSelecionada,
      data_inicio: this.dataInicio,
      data_fim: this.dataFim
    };

    this.data.criarCronograma(payload).subscribe({
      next: () => this.finalizarCriacaoCronograma('Cronograma criado com sucesso!'),
      error: (err) => alert('Erro ao gerar cronograma: ' + (err.error?.erro || 'Erro interno do servidor'))
    });
  }
}