
import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AnalysisComponent } from './analysis';
import { AnalysisService } from '../../core/services/analysis.service';
import { AnalysisResponse } from '../../core/models/analysis-response';

describe('AnalysisComponent', () => {
  let analysisService: {
    analyze: ReturnType<typeof vi.fn>;
    getErrorMessage: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    analysisService = {
      analyze: vi.fn(),
      getErrorMessage: vi.fn().mockReturnValue('Erro de análise.'),
    };

    await TestBed.configureTestingModule({
      imports: [AnalysisComponent],
      providers: [
        provideRouter([]),
        {
          provide: AnalysisService,
          useValue: analysisService,
        },
      ],
    }).compileComponents();
  });

  function createComponent() {
    const fixture = TestBed.createComponent(AnalysisComponent);
    fixture.detectChanges();

    return {
      fixture,
      component: fixture.componentInstance,
    };
  }

  const validJob =
    'Vaga para pessoa desenvolvedora com experiência em APIs, bancos de dados e testes automatizados.';

  it('deve criar o componente', () => {
    const { component } = createComponent();

    expect(component).toBeTruthy();
    expect(component.currentView).toBe('input');
  });

  it('deve rejeitar descrição da vaga com menos de trinta caracteres', () => {
    const { component } = createComponent();

    component.jobDescription = 'Vaga de desenvolvedor';
    component.resumeText = 'Currículo de teste';

    expect(component.canAnalyze()).toBe(false);
  });

  it('deve rejeitar descrição acima do limite de quinze mil caracteres', () => {
    const { component } = createComponent();

    component.jobDescription = 'A'.repeat(15001);
    component.resumeText = 'Currículo de teste';

    expect(component.canAnalyze()).toBe(false);
  });

  it('deve aceitar descrição e currículo no limite de quinze mil caracteres', () => {
    const { component } = createComponent();
    component.jobDescription = 'A'.repeat(15000);
    component.resumeText = 'A'.repeat(15000);
    expect(component.canAnalyze()).toBe(true);
  });

  it('deve rejeitar currículo acima do limite de quinze mil caracteres', () => {
    const { component } = createComponent();
    component.jobDescription = validJob;
    component.onResumeTextChange('A'.repeat(15001));
    expect(component.errorMessage).toContain('15000 caracteres');
    expect(component.canAnalyze()).toBe(false);
  });

  it('deve aceitar descrição válida e currículo em texto', () => {
    const { component } = createComponent();

    component.jobDescription = validJob;
    component.resumeText = 'Currículo com experiência em desenvolvimento.';

    expect(component.canAnalyze()).toBe(true);
  });

  it('deve aceitar descrição válida e currículo em arquivo', () => {
    const { component } = createComponent();

    component.jobDescription = validJob;
    component.selectedFile = new File(
      ['currículo'],
      'curriculo.pdf',
      { type: 'application/pdf' },
    );

    expect(component.canAnalyze()).toBe(true);
  });

  it('deve rejeitar análise sem currículo', () => {
    const { component } = createComponent();

    component.jobDescription = validJob;

    expect(component.canAnalyze()).toBe(false);
  });

  it('deve rejeitar descrição com emoji', () => {
    const { component } = createComponent();

    component.onJobDescriptionChange(`${validJob} 🚀`);

    expect(component.errorMessage).toContain('emojis ou emoticons');
    expect(component.canAnalyze()).toBe(false);
  });

  it('deve rejeitar currículo com emoticon', () => {
    const { component } = createComponent();

    component.jobDescription = validJob;
    component.onResumeTextChange('Currículo de teste :)');

    expect(component.errorMessage).toContain('emojis ou emoticons');
    expect(component.canAnalyze()).toBe(false);
  });

  it('deve rejeitar extensão de arquivo não permitida', () => {
    const { component } = createComponent();

    const input = document.createElement('input');
    input.type = 'file';

    const file = new File(['conteúdo'], 'curriculo.exe');
    Object.defineProperty(input, 'files', {
      value: [file],
    });

    component.onFileSelected({
      target: input,
    } as unknown as Event);

    expect(component.errorMessage).toContain('Formato de arquivo inválido');
    expect(component.selectedFile).toBeNull();
    expect(input.value).toBe('');
  });

  it('deve rejeitar arquivo vazio', () => {
    const { component } = createComponent();

    const input = document.createElement('input');
    input.type = 'file';

    const file = new File([], 'curriculo.pdf');
    Object.defineProperty(input, 'files', {
      value: [file],
    });

    component.onFileSelected({
      target: input,
    } as unknown as Event);

    expect(component.errorMessage).toContain('arquivo selecionado está vazio');
    expect(component.selectedFile).toBeNull();
  });

  it('deve rejeitar arquivo maior que um megabyte', () => {
    const { component } = createComponent();

    const input = document.createElement('input');
    input.type = 'file';

    const file = new File(
      [new Uint8Array(1_048_577)],
      'curriculo.pdf',
    );

    Object.defineProperty(input, 'files', {
      value: [file],
    });

    component.onFileSelected({
      target: input,
    } as unknown as Event);

    expect(component.errorMessage).toContain('no máximo 1 MB');
    expect(component.selectedFile).toBeNull();
  });

  it('deve limpar o texto ao selecionar arquivo válido', () => {
    const { component } = createComponent();

    component.resumeText = 'Currículo digitado anteriormente';

    const input = document.createElement('input');
    input.type = 'file';

    const file = new File(['conteúdo'], 'curriculo.docx');
    Object.defineProperty(input, 'files', {
      value: [file],
    });

    component.onFileSelected({
      target: input,
    } as unknown as Event);

    expect(component.resumeText).toBe('');
    expect(component.selectedFile).toBe(file);
    expect(component.errorMessage).toBe('');
  });

  it('deve limpar o arquivo selecionado', () => {
    const { component } = createComponent();

    component.selectedFile = new File(['conteúdo'], 'curriculo.pdf');
    component.errorMessage = 'Erro anterior';

    component.clearSelectedFile();

    expect(component.selectedFile).toBeNull();
    expect(component.errorMessage).toBe('');
  });

  it('deve limpar o texto do currículo', () => {
    const { component } = createComponent();

    component.resumeText = 'Currículo de teste';
    component.errorMessage = 'Erro anterior';

    component.clearResumeText();

    expect(component.resumeText).toBe('');
    expect(component.errorMessage).toBe('');
  });

  it('não deve chamar o serviço quando os dados forem inválidos', () => {
    const { component } = createComponent();

    component.analyze();

    expect(analysisService.analyze).not.toHaveBeenCalled();
    expect(component.currentView).toBe('input');
    expect(component.errorMessage).toContain('descrição de vaga válida');
  });

  it('deve apresentar o resultado quando a análise for concluída', () => {
    const { component } = createComponent();

    const response = {
      status: 'completed',
    } as AnalysisResponse;

    analysisService.analyze.mockReturnValue(of(response));

    component.jobDescription = validJob;
    component.resumeText = 'Currículo de teste';

    component.analyze();

    expect(analysisService.analyze).toHaveBeenCalledWith(
      validJob,
      'Currículo de teste',
      null,
    );
    expect(component.currentView).toBe('result');
    expect(component.result).toEqual(response);
  });

  it('deve exibir falha quando a API não concluir a análise', () => {
    const { component } = createComponent();

    analysisService.analyze.mockReturnValue(
      of({ status: 'failed' } as AnalysisResponse),
    );

    component.jobDescription = validJob;
    component.resumeText = 'Currículo de teste';

    component.analyze();

    expect(component.currentView).toBe('failed');
    expect(component.errorMessage).toContain('não foi concluída');
  });

  it('deve tratar erro HTTP durante a análise', () => {
    const { component } = createComponent();

    const error = new HttpErrorResponse({
      status: 500,
      statusText: 'Internal Server Error',
    });

    analysisService.analyze.mockReturnValue(
      throwError(() => error),
    );

    component.jobDescription = validJob;
    component.resumeText = 'Currículo de teste';

    component.analyze();

    expect(analysisService.getErrorMessage).toHaveBeenCalledWith(error);
    expect(component.currentView).toBe('failed');
    expect(component.errorMessage).toBe('Erro de análise.');
  });

  it('deve voltar para entrada e limpar os dados após resultado concluído', () => {
    const { component } = createComponent();

    component.currentView = 'result';
    component.jobDescription = validJob;
    component.resumeText = 'Currículo de teste';
    component.selectedFile = new File(['teste'], 'curriculo.pdf');
    component.result = { status: 'completed' } as AnalysisResponse;

    component.backToInput();

    expect(component.currentView).toBe('input');
    expect(component.jobDescription).toBe('');
    expect(component.resumeText).toBe('');
    expect(component.selectedFile).toBeNull();
    expect(component.result).toBeNull();
  });

  it('deve preservar os dados ao voltar antes de concluir a análise', () => {
    const { component } = createComponent();

    component.currentView = 'failed';
    component.jobDescription = validJob;
    component.resumeText = 'Currículo de teste';
    component.errorMessage = 'Falha';

    component.backToInput();

    expect(component.currentView).toBe('input');
    expect(component.jobDescription).toBe(validJob);
    expect(component.resumeText).toBe('Currículo de teste');
    expect(component.errorMessage).toBe('');
  });
});
