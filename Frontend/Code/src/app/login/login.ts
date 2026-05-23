import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-login',
  imports: [],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  loginComGoogle() {
    //window.location.href = 'http://localhost:8000/auth/login/google-oauth2/';
    window.location.href = `${environment.apiUrl}/auth/login/google-oauth2/`;
  }
}
