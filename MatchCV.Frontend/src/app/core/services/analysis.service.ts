
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { AnalysisResponse } from '../models/analysis-response';

@Injectable({
  providedIn: 'root',
})
export class AnalysisService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl =
    'http://localhost:8000/api/v1/analysis/resume';

  analyze(
    jobDescription: string,
    resumeText: string,
    resumeFile: File | null,
  ): Observable<AnalysisResponse> {
    const formData = new FormData();

    formData.append('job_description', jobDescription);

    if (resumeFile !== null) {
      formData.append('resume', resumeFile, resumeFile.name);
    } else {
      formData.append('resume_text', resumeText);
    }

    return this.http.post<AnalysisResponse>(
      this.apiUrl,
      formData,
    );
  }

  getErrorMessage(error: unknown): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'Não foi possível realizar a análise.';
    }

    const detail = error.error?.detail;

    if (typeof detail === 'string' && detail.trim().length > 0) {
      return detail;
    }

    if (error.status === 0) {
      return 'Não foi possível conectar à API do MatchCV. Verifique se o servidor está em execução.';
    }

    if (error.status === 413) {
      return 'O arquivo enviado ultrapassa o limite de tamanho permitido.';
    }

    if (error.status === 422) {
      return 'Os dados enviados não foram aceitos pela API. Confira a descrição da vaga e o currículo.';
    }

    if (error.status === 429) {
      return 'O serviço de análise está recebendo muitas solicitações. Tente novamente mais tarde.';
    }

    if (error.status >= 500) {
      return 'Ocorreu um erro no servidor durante a análise. Tente novamente mais tarde.';
    }

    return 'Não foi possível realizar a análise. Confira os dados enviados e tente novamente.';
  }
}
