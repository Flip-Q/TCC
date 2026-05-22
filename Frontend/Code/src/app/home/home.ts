import { Component, inject, signal, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Data } from '../services/data';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.html',
  styleUrl: './home.css'
})

export class Home implements OnInit {
  private router = inject(Router);
  private data = inject(Data);

  protected readonly nomeUsuario = signal('');

  ngOnInit() {
    this.data.getPerfilProfessor().subscribe({
      next: (dados) => {
        this.nomeUsuario.set(dados.nome);
      },
      error: (err) => {
        console.error('Erro ao obter perfil do professor:', err);
      }
    })
  }

  irParaAgendamento() {
    this.router.navigate(['/agendamento']);
  }

  logout() {
    //window.location.href = 'http://localhost:8000/auth/logout/';

    const form = document.createElement('form');
    form.method = 'POST';
    //form.action = 'http://localhost:8000/auth/logout/';
    form.action = `${environment.apiUrl}/auth/logout/`;

    document.body.appendChild(form);
    form.submit();
  }
}