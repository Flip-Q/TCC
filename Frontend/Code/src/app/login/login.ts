import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  loginComGoogle() {
    window.location.href = 'http://localhost:8000/auth/login/google-oauth2/';
  }
}
