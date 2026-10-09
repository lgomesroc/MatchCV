
import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { AnalysisResponse } from '../../../../core/models/analysis-response';

interface ResultSection {
  id: string;
  title: string;
  description: string;
  items: string[];
  emptyMessage: string;
}

@Component({
  selector: 'app-analysis-result',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analysis-result.html',
  styleUrl: './analysis-result.scss',
})
export class AnalysisResultComponent {
  @Input({ required: true }) result!: AnalysisResponse;

  @Output() back = new EventEmitter<void>();

  get sections(): ResultSection[] {
    if (!this.result) {
      return [];
    }

    return [
      {
        id: 'evidenced',
        title: 'Requisitos evidenciados',
        description:
          'Requisitos para os quais foram encontradas evidências no conteúdo do currículo.',
        items: this.result.evidenced_requirements ?? [],
        emptyMessage:
          'Nenhum requisito foi identificado como evidenciado nesta análise.',
      },
      {
        id: 'unevidenced',
        title: 'Requisitos não evidenciados',
        description:
          'Requisitos da vaga para os quais o currículo não apresentou evidências suficientes.',
        items: this.result.unevidenced_requirements ?? [],
        emptyMessage:
          'Não foram listados requisitos nesta categoria.',
      },
      {
        id: 'gaps',
        title: 'Lacunas identificadas',
        description:
          'Pontos de diferença entre o que a vaga solicita e o que está demonstrado no currículo.',
        items: this.result.gaps ?? [],
        emptyMessage:
          'Nenhuma lacuna foi listada pela análise.',
      },
      {
        id: 'issues',
        title: 'Pontos de atenção no currículo',
        description:
          'Problemas ou aspectos do currículo que podem ser melhorados, conforme a análise.',
        items: this.result.resume_issues ?? [],
        emptyMessage:
          'Nenhum ponto de atenção foi listado.',
      },
      {
        id: 'suggestions',
        title: 'Sugestões de melhoria',
        description:
          'Sugestões para tornar o currículo mais claro e alinhado às informações verdadeiras da sua experiência.',
        items: this.result.suggestions ?? [],
        emptyMessage:
          'Nenhuma sugestão foi retornada.',
      },
    ];
  }

  onBack(): void {
    this.back.emit();
  }
}
