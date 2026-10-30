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

async function fillAnalysisForm(page: Page): Promise<void> {
  await page.getByLabel('Descrição da vaga').fill(jobDescription);
  await page.getByLabel('Seu currículo').fill(resumeText);
}

test.describe('Estados e erros da análise', () => {
  test('mostra o estado de processamento enquanto aguarda a API', async ({
    page,
  }) => {
    let releasePolling: (() => void) | undefined;
    const pollingGate = new Promise<void>((resolve) => {
      releasePolling = resolve;
    });

    await page.route('**/api/v1/analysis/resume', async (route) => {
      await route.fulfill({
        status: 202,
        contentType: 'application/json',
        body: JSON.stringify({ analysis_id: 'e2e-loading', status: 'pending' }),
      });
    });

    await page.route('**/api/v1/analysis/e2e-loading', async (route) => {
      await pollingGate;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'completed',
          evidenced_requirements: ['Experiência com APIs REST'],
          unevidenced_requirements: [],
          gaps: [],
          resume_issues: [],
          suggestions: [],
        }),
      });
    });

    await loginAndOpenAnalysis(page);
    await fillAnalysisForm(page);
    await page.getByRole('button', { name: /analisar currículo/i }).click();

    await expect(
      page.getByRole('heading', { name: 'Analisando seu currículo' }),
    ).toBeVisible();

    releasePolling?.();

    await expect(
      page.getByRole('heading', { name: 'Resultado da análise' }),
    ).toBeVisible();
  });

  test('explica quando a cota de análises terminou', async ({ page }) => {
    await page.route('**/api/v1/analysis/resume', async (route) => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Você atingiu sua cota de análises disponível.',
        }),
      });
    });

    await loginAndOpenAnalysis(page);
    await fillAnalysisForm(page);
    await page.getByRole('button', { name: /analisar currículo/i }).click();

    await expect(
      page.getByRole('heading', {
        name: /não foi possível concluir a análise/i,
      }),
    ).toBeVisible();
    await expect(page.getByRole('alert')).toContainText(
      'Você atingiu sua cota de análises disponível.',
    );

    await page.getByRole('button', { name: 'Voltar ao formulário' }).click();
    await expect(
      page.getByRole('heading', { name: /analise seu currículo/i }),
    ).toBeVisible();
  });

  test('explica quando a API está indisponível e permite voltar ao formulário', async ({
    page,
  }) => {
    await page.route('**/api/v1/analysis/resume', async (route) => {
      await route.abort('failed');
    });

    await loginAndOpenAnalysis(page);
    await fillAnalysisForm(page);
    await page.getByRole('button', { name: /analisar currículo/i }).click();

    await expect(
      page.getByRole('heading', {
        name: /não foi possível concluir a análise/i,
      }),
    ).toBeVisible();
    await expect(page.getByRole('alert')).toContainText(
      'Não foi possível conectar à API do MatchCV.',
    );

    await page.getByRole('button', { name: 'Voltar ao formulário' }).click();
    await expect(
      page.getByRole('heading', { name: /analise seu currículo/i }),
    ).toBeVisible();
  });
});
