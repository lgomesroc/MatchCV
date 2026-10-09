
import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';

import { AnalysisResponse } from '../../core/models/analysis-response';
import { AnalysisService } from '../../core/services/analysis.service';

import { AnalysisFailedComponent } from './components/analysis-failed/analysis-failed';
import { AnalysisInputComponent } from './components/analysis-input/analysis-input';
import { AnalysisProcessingComponent } from './components/analysis-processing/analysis-processing';
import { AnalysisResultComponent } from './components/analysis-result/analysis-result';

type AnalysisView = 'input' | 'processing' | 'result' | 'failed';

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [
    CommonModule,
    AnalysisInputComponent,
    AnalysisProcessingComponent,
    AnalysisResultComponent,
    AnalysisFailedComponent,
  ],
  templateUrl: './analysis.html',
  styleUrl: './analysis.scss',
})
export class AnalysisComponent {
  private readonly analysisService = inject(AnalysisService);

  currentView: AnalysisView = 'input';

  jobDescription = '';
  resumeText = '';
  selectedFile: File | null = null;

  result: AnalysisResponse | null = null;
  errorMessage = '';

  private readonly maxJobDescriptionCharacters = 3000;
  private readonly maxResumeFileSizeBytes = 1_048_576;
  private readonly allowedExtensions = ['.pdf', '.doc', '.docx'];

  onJobDescriptionChange(value: string): void {
    this.jobDescription = value;
    this.errorMessage = '';
    this.result = null;

    if (this.containsEmojiOrEmoticon(value)) {
      this.errorMessage =
        'A descrição da vaga não pode conter emojis ou emoticons.';
    }
  }

  onResumeTextChange(value: string): void {
    this.resumeText = value;
    this.errorMessage = '';
    this.result = null;

    if (value.trim().length > 0) {
      this.selectedFile = null;
    }

    if (this.containsEmojiOrEmoticon(value)) {
      this.errorMessage =
        'O currículo não pode conter emojis ou emoticons.';
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) {
      return;
    }

    this.errorMessage = '';
    this.result = null;

    if (!this.isAllowedFile(file)) {
      this.errorMessage =
        'Formato de arquivo inválido. Selecione um arquivo PDF, DOC ou DOCX.';
      input.value = '';
      this.selectedFile = null;
      return;
    }

    if (file.size === 0) {
      this.errorMessage = 'O arquivo selecionado está vazio.';
      input.value = '';
      this.selectedFile = null;
      return;
    }

    if (file.size > this.maxResumeFileSizeBytes) {
      this.errorMessage =
        'O arquivo deve ter no máximo 1 MB. Selecione outro arquivo.';
      input.value = '';
      this.selectedFile = null;
      return;
    }

    this.resumeText = '';
    this.selectedFile = file;
  }

  clearSelectedFile(): void {
    this.selectedFile = null;
    this.errorMessage = '';
    this.result = null;
  }

  clearResumeText(): void {
    this.resumeText = '';
    this.errorMessage = '';
    this.result = null;
  }

  canAnalyze(): boolean {
    const job = this.jobDescription.trim();
    const hasResume = this.resumeText.trim().length > 0 || this.selectedFile !== null;

    return (
      job.length >= 30 &&
      job.length <= this.maxJobDescriptionCharacters &&
      hasResume &&
      !this.containsEmojiOrEmoticon(this.jobDescription) &&
      !this.containsEmojiOrEmoticon(this.resumeText)
    );
  }

  analyze(): void {
    this.errorMessage = '';
    this.result = null;

    if (!this.canAnalyze()) {
      this.errorMessage =
        'Informe uma descrição de vaga válida e um currículo em texto ou arquivo.';
      return;
    }

    this.currentView = 'processing';

    this.analysisService
      .analyze(
        this.jobDescription.trim(),
        this.resumeText,
        this.selectedFile,
      )
      .subscribe({
        next: (response: AnalysisResponse) => {
          if (response.status !== 'completed') {
            this.errorMessage =
              response.status === 'failed'
                ? 'A análise não foi concluída. Tente novamente.'
                : 'A API não devolveu um resultado final para a análise.';

            this.currentView = 'failed';
            return;
          }

          this.result = response;
          this.currentView = 'result';
        },
        error: (error: unknown) => {
          this.errorMessage =
            this.analysisService.getErrorMessage(error);
          this.currentView = 'failed';
        },
      });
  }

  backToInput(): void {
    this.currentView = 'input';
    this.errorMessage = '';
    this.result = null;
  }

  private isAllowedFile(file: File): boolean {
    const fileName = file.name.toLowerCase();

    return this.allowedExtensions.some((extension) =>
      fileName.endsWith(extension),
    );
  }

  private containsEmojiOrEmoticon(value: string): boolean {
    if (/[\p{Extended_Pictographic}\uFE0F]/u.test(value)) {
      return true;
    }

    const emoticonPatterns = [
      /:\)+/,
      /:-+\)+/,
      /:\(+/,
      /:-+\(+/,
      /;\)+/,
      /;-+\)+/,
      /;\(+/,
      /;-+\(+/,
      /:D+/i,
      /:-+D+/i,
      /[xX][dD]+/,
      /<3/,
      /:'\(/,
      /:'-\(/,
    ];

    return emoticonPatterns.some((pattern) => pattern.test(value));
  }
}
