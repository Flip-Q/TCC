import { Component, signal, inject, OnInit } from '@angular/core';
import { RouterOutlet, RouterModule, Router, NavigationEnd } from '@angular/router';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit{
  protected readonly title = signal('portal-prevest');
  protected isMenuAberto = signal(true);
  protected mostrarLayout = signal(false);
  
  private router = inject(Router); // checar a URL para mostrar ou ocultar o layout

  ngOnInit() {
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        this.mostrarLayout.set(!event.urlAfterRedirects.includes('/login')); // se a URL incluir '/login', oculta o layout, caso contrário, mostra
      }
    });
  }

  toggleMenu() {
    this.isMenuAberto.update(estadoAtual => !estadoAtual);
  }

  logout() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `${environment.apiUrl}/auth/logout/`;

    document.body.appendChild(form);
    form.submit();
  }
}
