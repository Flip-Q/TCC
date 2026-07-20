import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Data } from '../services/data';

@Component({
  selector: 'app-substituicoes',
  imports: [CommonModule],
  templateUrl: './substituicoes.html',
  styleUrl: './substituicoes.css'
})
export class Substituicoes implements OnInit {
  private data = inject(Data);

  protected abaAtiva: 'recebidos' | 'enviados' = 'recebidos';

  protected convitesRecebidos = signal<any[]>([]);
  protected minhasSolicitacoes = signal<any[]>([]);

  ngOnInit() {
    this.carregarSubstituicoes();
  }

  protected setAba(aba: 'recebidos' | 'enviados') {
    this.abaAtiva = aba;
  }

  protected carregarSubstituicoes() {
    this.data.getConvitesRecebidos().subscribe({
      next: (dados) => this.convitesRecebidos.set(dados),
      error: (err) => console.error('Erro ao buscar convites recebidos:', err)
    });

    this.data.getMinhasSolicitacoes().subscribe({
      next: (dados) => this.minhasSolicitacoes.set(dados),
      error: (err) => console.error('Erro ao buscar minhas solicitações:', err)
    });
  }

  protected responderConvite(idSubstituicao: number, statusResposta: string) {
    const payload = { status: statusResposta }; 

    this.data.responderSubstituicao(idSubstituicao, payload).subscribe({
      next: (res) => {
        alert(res.mensagem);
        this.carregarSubstituicoes();
      },
      error: (err) => {
        console.error('Erro ao responder convite:', err);
        alert('Erro ao processar a resposta. Por favor, tente novamente.');
      }
    });
  }
}