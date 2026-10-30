import { expect, test, type Page } from '@playwright/test';

const loginResponse = {
  access_token: 'e2e-access-token',
  token_type: 'bearer',
  user: {
    id: 'e2e-user',
    name: 'Pessoa Teste',
    email: 'pessoa@example.com',
  },
};

const analysisResponse = {
  status: 'completed',
  evidenced_requirements: ['Experiência com APIs REST'],
  unevidenced_requirements: ['Experiência com Kubernetes'],
  gaps: ['O currículo não demonstra experiência com Kubernetes'],
  resume_issues: ['Falta detalhar resultados dos projetos'],
  suggestions: ['Descrever responsabilidades e resultados concretos'],
};

const jobDescription =
  'Desenvolvedor backend com experiência em APIs REST, testes e bancos de dados.';

const resumeText =
  'Desenvolvedor com experiência na criação e manutenção de APIs REST e testes automatizados.';

async function loginAndOpenAnalysis(page: Page): Promise<void> {
  await page.route('**/api/v1/auth/login', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(loginResponse),
    });
  });

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(loginResponse.user),
    });
  });

  await page.goto('/login');

  await page.getByLabel('E-mail').fill('pessoa@example.com');
  await page.getByLabel('Senha').fill('SenhaForte123!');
  await page.getByRole('button', { name: 'Entrar' }).click();

  await expect(page).toHaveURL(/\/analysis$/);
  await expect(
    page.getByRole('heading', { name: /analise seu currículo/i }),
  ).toBeVisible();
}

test.describe('Análise de currículo', () => {
  test('não permite analisar sem currículo e descrição válida', async ({
    page,
  }) => {
    await loginAndOpenAnalysis(page);

    await expect(
      page.getByRole('button', { name: /analisar currículo/i }),
    ).toBeDisabled();
  });

  test('envia os campos corretos, acompanha a análise e apresenta o resultado', async ({
    page,
  }) => {
    let submittedBody = '';

    await page.route('**/api/v1/analysis/resume', async (route) => {
      const request = route.request();
      const contentType = request.headers()['content-type'] ?? '';

      expect(contentType).toContain('multipart/form-data');

      const body = request.postData();
      expect(body).not.toBeNull();
      submittedBody = body ?? '';

      await route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({ analysis_id: 'e2e-analysis', status: 'pending' }),
      });
    });

    await page.route('**/api/v1/analysis/e2e-analysis', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(analysisResponse),
      });
    });

    await loginAndOpenAnalysis(page);
    await page.getByLabel('Descrição da vaga').fill(jobDescription);
    await page.getByLabel('Seu currículo').fill(resumeText);

    await expect(
      page.getByRole('button', { name: /analisar currículo/i }),
    ).toBeEnabled();

    await page.getByRole('button', { name: /analisar currículo/i }).click();

    await expect(
      page.getByRole('heading', { name: 'Resultado da análise' }),
    ).toBeVisible();

    await expect(
      page.getByText('Experiência com APIs REST', { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText('Experiência com Kubernetes', { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText('Descrever responsabilidades e resultados concretos', {
        exact: true,
      }),
    ).toBeVisible();

    expect(submittedBody).toContain('name="job_description"');
    expect(submittedBody).toContain(jobDescription);
    expect(submittedBody).toContain('name="resume_text"');
    expect(submittedBody).toContain(resumeText);
    expect(submittedBody).not.toContain('name="resume";');
  });

  test('mostra a falha da API e permite voltar ao formulário', async ({
    page,
  }) => {
    await page.route('**/api/v1/analysis/resume', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Erro simulado no servidor' }),
      });
    });

    await loginAndOpenAnalysis(page);
    await page.getByLabel('Descrição da vaga').fill(jobDescription);
    await page.getByLabel('Seu currículo').fill(resumeText);
    await page.getByRole('button', { name: /analisar currículo/i }).click();

    await expect(
      page.getByRole('heading', {
        name: /não foi possível concluir a análise/i,
      }),
    ).toBeVisible();
    await expect(page.getByRole('alert')).toContainText(
      'Erro simulado no servidor',
    );

    await page.getByRole('button', { name: 'Voltar ao formulário' }).click();

    await expect(
      page.getByRole('heading', { name: /analise seu currículo/i }),
    ).toBeVisible();
    await expect(page.getByLabel('Descrição da vaga')).toHaveValue(
      jobDescription,
    );
    await expect(page.getByLabel('Seu currículo')).toHaveValue(resumeText);
  });
});
