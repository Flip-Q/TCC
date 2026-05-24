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
}
