import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Data } from '../services/data';

@Component({
  selector: 'app-itens-template-cronograma',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './itens-template-cronograma.html',
  styleUrl: './itens-template-cronograma.css',
})
export class ItensTemplateCronograma implements OnInit {
  private data = inject(Data);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  protected templateId!: number;
  protected templateInfo = signal<any>(null);
  protected listaItens = signal<any[]>([]);
  protected novoItemTitulo = '';
  
  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if(idParam) {
        this.templateId = +idParam; // Converte o ID de texto para número
        this.carregarDados();
      }
    });
  }

  carregarDados() {
    this.data.getTemplateItens(this.templateId).subscribe({
      next: (dados) => this.templateInfo.set(dados),
      error: (err) => console.error('Erro ao obter informações do template:', err)
    });

    this.buscarItens();
  }

  buscarItens() {
    this.data.getTemplateItens(this.templateId).subscribe({
      next: (dados) => this.listaItens.set(dados),
      error: (err) => console.error('Erro ao buscar itens', err)
    });
  }

  adicionarItem() {
    if (!this.novoItemTitulo.trim()) return;

    const payload = {
      titulo_aula: this.novoItemTitulo
    };
    this.data.criarTemplateItem(this.templateId, payload).subscribe({
      next: () => {
        this.novoItemTitulo = '';
        this.buscarItens();
      },
      error: (err: any) => alert('Erro ao adicionar aula: ' + (err.error?.erro || 'Erro no servidor'))
    });
  }

  excluirItem(itemId: number) {
    if (confirm('Deseja excluir esta aula do template?')) {
      this.data.excluirTemplateItem(itemId).subscribe({
        next: () => this.buscarItens(),
        error: (err) => alert('Erro ao excluir aula: ' + (err.error?.erro || 'Erro no servidor'))
      });
    }
  }

  voltar() {
    this.router.navigate(['/cronograma']);
  }





}
