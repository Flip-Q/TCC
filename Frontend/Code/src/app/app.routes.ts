import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Home } from './home/home';
import { Agendamento } from './agendamento/agendamento';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'home', component: Home },
  { path: 'agendamento', component: Agendamento },
  { path: '**', redirectTo: '/login' }
];