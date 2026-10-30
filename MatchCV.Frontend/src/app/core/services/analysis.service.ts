import {
  HttpClient,
  HttpErrorResponse,
} from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import {
  Observable,
  filter,
  switchMap,
  take,
  takeUntil,
  takeWhile,
  tap,
  throwError,
  throwIfEmpty,
  timer,
} from 'rxjs';

import { environment } from '../../../environments/environment';
import { AnalysisResponse } from '../models/analysis-response';
import { MemoryCacheService } from './memory-cache.service';

export class AnalysisPollingTimeoutError extends Error {
  constructor() {
    super('O tempo máximo de espera pela análise foi excedido.');
    this.name = 'AnalysisPollingTimeoutError';
  }
}

@Injectable({
  providedIn: 'root',
})
export class AnalysisService {
  static readonly ANALYSIS_POLLING_TIMEOUT_MS = 5 * 60 * 1000;

  private readonly http = inject(HttpClient);
  private readonly memoryCache = inject(MemoryCacheService);

  private readonly apiUrl = `${environment.apiUrl}/analysis/resume`;

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
    ).pipe(
      switchMap((queued) => {
        if (!queued.analysis_id) {
          return throwError(() => new Error('A API não retornou o identificador da análise.'));
        }

        return timer(0, 2000).pipe(
          switchMap(() => this.http.get<AnalysisResponse>(
            `${environment.apiUrl}/analysis/${queued.analysis_id}`,
          )),
          takeWhile((response) => response.status === 'pending' || response.status === 'processing', true),
          filter((response) => response.status === 'completed' || response.status === 'failed'),
          take(1),
          takeUntil(timer(AnalysisService.ANALYSIS_POLLING_TIMEOUT_MS)),
          throwIfEmpty(() => new AnalysisPollingTimeoutError()),
          tap(() => this.invalidateAnalysisCache()),
        );
      }),
    );
  }

  invalidateAnalysisCache(): void {
    this.memoryCache.invalidatePrefix('analysis:');
    this.memoryCache.invalidatePrefix('history:');
  }

  getErrorMessage(error: unknown): string {
    if (error instanceof AnalysisPollingTimeoutError) {
      return 'A análise está demorando mais que o esperado. Ela pode continuar sendo processada no servidor. Não criamos outra análise automaticamente; aguarde um pouco antes de tentar novamente.';
    }

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
