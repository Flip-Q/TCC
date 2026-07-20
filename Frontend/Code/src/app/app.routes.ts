import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Home } from './home/home';
import { Agendamento } from './agendamento/agendamento';
import { Cronograma } from './cronograma/cronograma';
import { ItensTemplateCronograma } from './itens-template-cronograma/itens-template-cronograma';
import { CronogramaTurma } from './cronograma-turma/cronograma-turma';
import { Substituicoes } from './substituicoes/substituicoes';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'home', component: Home },
  { path: 'agendamento', component: Agendamento },
  { path: 'cronograma', component: Cronograma },
  { path: 'cronograma/itens/:id', component: ItensTemplateCronograma },
  { path: 'cronograma-real', component: CronogramaTurma },
  { path: 'substituicoes', component: Substituicoes },
  { path: '**', redirectTo: '/login' }
];