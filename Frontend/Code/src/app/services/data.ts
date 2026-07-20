import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class Data {
  private http = inject(HttpClient);
  //private readonly API_URL = 'http://localhost:8000/api'; 
  private readonly API_URL = `${environment.apiUrl}/api`;

  getPerfilProfessor(): Observable<any> {
    return this.http.get(`${this.API_URL}/perfil/`, { withCredentials: true });
  }

  getAgendamentos(): Observable<any> {
    return this.http.get<any[]>(`${this.API_URL}/agendamentos/`, { withCredentials: true });
  }

  dispararPostagens(aulaId: number): Observable<any> {
    return this.http.post(`${this.API_URL}/disparar/${aulaId}/`, {}, { withCredentials: true });
  }

  getGoogleToken(): Observable<any> {
    return this.http.get(`${this.API_URL}/google-token/`, { withCredentials: true });
  }

  criarAgendamento(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/agendamentos/criar/`, data, { withCredentials: true });
  }

  getTurmas(): Observable<any> {
    return this.http.get(`${this.API_URL}/turmas/`, { withCredentials: true });
  }

  getDisciplinas(): Observable<any> {
    return this.http.get(`${this.API_URL}/disciplinas/`, { withCredentials: true });
  }

  getTemplates(): Observable<any> {
    return this.http.get<any[]>(`${this.API_URL}/templates/`, { withCredentials: true });
  }
  
  criarTemplate(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/templates/criar/`, data, { withCredentials: true });
  }
  
  getTemplate(templateId: number): Observable<any> {
    return this.http.get(`${this.API_URL}/templates/${templateId}/`, { withCredentials: true });
  }
  
  excluirTemplate(templateId: number): Observable<any> {
    return this.http.post(`${this.API_URL}/templates/${templateId}/excluir/`, {}, { withCredentials: true });
  }

  getTemplateItens(templateId: number): Observable<any> {
    return this.http.get(`${this.API_URL}/templates/${templateId}/itens/`, { withCredentials: true });
  }

  criarTemplateItem(templateId: number, data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/templates/${templateId}/itens/criar/`, data, { withCredentials: true });
  }

  excluirTemplateItem(itemId: number): Observable<any> {
    return this.http.post(`${this.API_URL}/templates/itens/${itemId}/excluir/`, {}, { withCredentials: true }); 
  }

  criarCronograma(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/cronogramas/gerar/`, data, { withCredentials: true });
  }

  getCronogramaReal(turmaId: string, disciplinaId: string): Observable<any> {
    return this.http.get(`${this.API_URL}/cronogramas/${turmaId}/${disciplinaId}/`, { withCredentials: true });
  }

  excluirAgendamento(tarefaId: number): Observable<any> {
    return this.http.post(`${this.API_URL}/agendamentos/${tarefaId}/excluir/`, {}, { withCredentials: true });
  }

  editarAgendamento(turmaId: number, data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/agendamentos/${turmaId}/editar/`, data, { withCredentials: true });
  }

  sincronizarCalendarioTurma(dados: any): Observable<any> {
    return this.http.post(`${this.API_URL}/cronogramas/sincronizar/`, dados, { withCredentials: true });
  }

  getProfessoresLista(): Observable<any> {
    return this.http.get(`${this.API_URL}/professores/lista/`, { withCredentials: true });
  }

  solicitarSubstituicao(dados: any): Observable<any> {
    return this.http.post(`${this.API_URL}/substituicoes/solicitar/`, dados, { withCredentials: true });
  }

  getConvitesRecebidos(): Observable<any> {
    return this.http.get(`${this.API_URL}/substituicoes/recebidas/`, { withCredentials: true });
  }

  getMinhasSolicitacoes(): Observable<any> {
    return this.http.get(`${this.API_URL}/substituicoes/enviadas/`, { withCredentials: true });
  }

  responderSubstituicao(id: number, dados: any): Observable<any> {
    return this.http.post(`${this.API_URL}/substituicoes/${id}/responder/`, dados, { withCredentials: true });
  }
}
