import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Data } from '../services/data';

declare var gapi: any;
declare var google: any;

@Component({
  selector: 'app-agendamento',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './agendamento.html',
  styleUrl: './agendamento.css'
})

export class Agendamento implements OnInit, OnDestroy {
  private router = inject(Router);
  private data = inject(Data);

  protected readonly tarefasAgendadas = signal<any[]>([]);
  protected readonly exibirModal = signal(false);
  protected readonly listaArquivos = signal<{ nome: string, url: string }[]>([]);
  protected readonly listaTurmas = signal<any[]>([]);
  protected readonly listaDisciplinas = signal<any[]>([]);

  protected assunto = '';
  protected dataPrevista = '';
  protected turmaCodigo = '';
  protected codigoDisciplina = '';
  private googleToken = '';
  private googleClientId = '';
  private googleApiKey = '';

  protected agendamentoIdEmEdicao: number | null = null;
  private intervaloAtualizacao: any;

  ngOnInit() {
    this.buscarTurmas();
    this.buscarDisciplinas();
    this.buscarTarefasAgendadas();
    this.carregarScriptGooglePicker();

    this.data.getGoogleToken().subscribe({
      next: (res) => {
        this.googleToken = res.access_token;
        this.googleClientId = res.client_id;
        this.googleApiKey = res.api_key;
      },
      error: (err) => {
        console.error('Erro ao obter token do Google:', err);
      }
    });

    this.intervaloAtualizacao = setInterval(() => {
      this.verificarAtualizacoes();
    }, 5000); // Verifica a cada 15 segundos
  }

  ngOnDestroy() {
    if (this.intervaloAtualizacao) {
      clearInterval(this.intervaloAtualizacao);
    }
  }

  verificarAtualizacoes() {
    this.data.getAgendamentos().subscribe({
      next: (dados) => {
        this.tarefasAgendadas.set(dados);
      }
    });
  }


  buscarTurmas() {
    this.data.getTurmas().subscribe({
      next: (dados) => {
        this.listaTurmas.set(dados);
      },
      error: (err) => {
        console.error('Erro ao obter turmas:', err);
      }
    });
  }

  buscarDisciplinas() {
    this.data.getDisciplinas().subscribe({
      next: (dados) => {
        this.listaDisciplinas.set(dados);
      },
      error: (err) => {
        console.error('Erro ao obter disciplinas:', err);
      }
    });
  }

  buscarTarefasAgendadas() {
    this.data.getAgendamentos().subscribe({
      next: (dados) => {
        this.tarefasAgendadas.set(dados);
      },
      error: (err) => {
        console.error('Erro ao obter agendamentos:', err);
      }
    });
  }

  enviarAgora(id: number) {
    if(confirm('Deseja postar essa tarefa agora?')) {
      this.data.dispararPostagens(id).subscribe({
        next: () => {
          alert('Tarefa postada com sucesso!');
          this.buscarTarefasAgendadas(); // Atualiza a lista após disparar a postagem
        },
        error: (err) => {
          alert('Erro ao postar a tarefa.');
        }
      });
    }
  }

  excluirAgendamento(tarefaId: number) {
    if (confirm('Tem certeza que deseja excluir este agendamento?')) {
      this.data.excluirAgendamento(tarefaId).subscribe({
        next: () => {
          this.buscarTarefasAgendadas(); 
        },
        error: (err) => {
          alert('Erro ao excluir o agendamento.');
        }
      });
    }
  }

  abrirModalEdicao(tarefa: any) {
    this.agendamentoIdEmEdicao = tarefa.id;
    this.assunto = tarefa.assunto;

    if (tarefa.data_prevista) {
      const dataAjustada = new Date(tarefa.data_prevista);
      dataAjustada.setMinutes(dataAjustada.getMinutes() - dataAjustada.getTimezoneOffset());
      this.dataPrevista = dataAjustada.toISOString().slice(0, 16);
    }

    this.turmaCodigo = tarefa.turma_codigo || '';
    this.codigoDisciplina = tarefa.disciplina_codigo || '';

    if (tarefa.arquivos && tarefa.arquivos.length > 0) {
      this.listaArquivos.set([...tarefa.arquivos]);
    } else{
      this.listaArquivos.set([]);
    }

    this.exibirModal.set(true);
  }

  private carregarScriptGooglePicker() {
    if (typeof gapi !== 'undefined') return;

    const script = document.createElement('script');
    script.src = 'https://apis.google.com/js/api.js';
    script.onload = () => {
      gapi.load('picker', {callback: () => console.log('Google Picker carregado com sucesso.')});
    };
    document.head.appendChild(script);
  }

  abrirSeletorDrive() {
    if (typeof gapi === 'undefined' || typeof google === 'undefined' || typeof google.picker === 'undefined') {
      gapi.load('picker', {
        callback: () => {
          console.log('Google Picker carregado com sucesso.');
          this.abrirSeletorDrive(); 
        }
      });
      return;
    }

    if (!this.googleToken) {
      alert('Erro na autenticação com Google. Faça login novamente.');
      return;
    }

    if (!this.googleApiKey || this.googleApiKey === '') {
      console.error('A chave da API esta vazia! Verifique o .env do Django e reinicie o servidor.');
      alert('Configuração de servidor incompleta (API Key ausente).');
      return;
    }


    try {
      const numeroDoProjeto = this.googleClientId.split('-')[0];

      const view = new google.picker.DocsView();
      
      const picker = new google.picker.PickerBuilder()
        .setOAuthToken(this.googleToken)
        //.setAppId(this.googleClientId)
        .setAppId(numeroDoProjeto)
        .setOrigin(window.location.protocol + '//' + window.location.host)
        .setDeveloperKey(this.googleApiKey)
        .addView(view)
        .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
        .setCallback((data: any) => {
          if (data.action === 'picked') {
            //const doc = data.docs[0];
            //const novoArquivo = {
            const novosArquivos = data.docs.map((doc: any) => ({
              nome: doc.name,
              url: doc.url
            }));
            this.listaArquivos.update(arquivos => [...arquivos, ...novosArquivos]);
          }
        })
        .build();

      picker.setVisible(true);
    } catch (err) {
      console.error('Erro ao abrir o seletor', err);
    }
  }


  removerArquivo(index: number) {
    this.listaArquivos.update(arquivos => arquivos.filter((_, i) => i !== index));
  }

  private finalizarSalvamentoModal(msg: string) {
    alert(msg);
    this.exibirModal.set(false);
    this.buscarTarefasAgendadas();
    this.limparFormulario();
  }

  salvarNovoAgendamento() {
    const payload = {
      turma_codigo: this.turmaCodigo,
      disciplina_codigo: this.codigoDisciplina,
      assunto: this.assunto,
      data_prevista: this.dataPrevista,
      arquivos: this.listaArquivos()
    };
  
    if (this.agendamentoIdEmEdicao) { // Se estiver editando um agendamento existente
      this.data.editarAgendamento(this.agendamentoIdEmEdicao, payload).subscribe({
        next: () => this.finalizarSalvamentoModal('Agendamento editado com sucesso.'),
        error: (err) => alert('Erro ao editar agendamento: ' + (err.error?.erro || 'Erro interno do servidor'))
      });
    }
    else{ // Criar um novo agendamento
      this.data.criarAgendamento(payload).subscribe({
        next: () => this.finalizarSalvamentoModal('Agendamento criado com sucesso.'),
        error: (err) => alert('Erro ao salvar agendmento' + (err.error?.erro || 'Erro interno do servidor'))
      });
    }
  
  
    /**
    this.data.criarAgendamento(payload).subscribe({
      next: () => {
        alert('Agendamento criado com sucesso!');
        this.exibirModal.set(false);
        this.buscarTarefasAgendadas();
        this.limparFormulario();
      },
      error: (err) => {
        alert('Erro ao salvar agendamento: ' + (err.error?.erro || 'Erro interno do servidor'));
      }
    });
  */
  }

  private limparFormulario() {
    this.agendamentoIdEmEdicao = null;
    this.assunto = '';
    this.dataPrevista = '';
    this.turmaCodigo = '';
    this.codigoDisciplina = '';
    this.listaArquivos.set([]);
  }


  voltar() {
    this.router.navigate(['/home']);
  }
}