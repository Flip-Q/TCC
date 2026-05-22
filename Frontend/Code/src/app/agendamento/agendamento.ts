import { Component, inject, signal, OnInit } from '@angular/core';
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

export class Agendamento implements OnInit {
  private router = inject(Router);
  private data = inject(Data);

  protected readonly tarefasAgendadas = signal<any[]>([]);
  protected readonly exibirModal = signal(false);
  protected readonly listaArquivos = signal<{ nome: string, url: string }[]>([]);

  protected assunto = '';
  protected dataPrevista = '';
  protected turmaCodigo = '';
  protected codigoDisciplina = '';
  private googleToken = '';
  private googleClientId = '';
  private googleApiKey = '';

  ngOnInit() {
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
        .setCallback((data: any) => {
          if (data.action === 'picked') {
            const doc = data.docs[0];
            const novoArquivo = {
              nome: doc.name,
              url: doc.url
            };
            this.listaArquivos.update(arquivos => [...arquivos, novoArquivo]);
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

  salvarNovoAgendamento() {
    const payload = {
      turma_codigo: this.turmaCodigo,
      disciplina_codigo: this.codigoDisciplina,
      assunto: this.assunto,
      data_prevista: this.dataPrevista,
      arquivos: this.listaArquivos()
    };

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
  }

  private limparFormulario() {
    this.assunto = '';
    this.dataPrevista = '';
    this.listaArquivos.set([]);
  }


  voltar() {
    this.router.navigate(['/home']);
  }
}