
import { expect, test } from '@playwright/test';

test.describe('Login', () => {
  test('exibe os campos de acesso e os links de navegação', async ({
    page,
  }) => {
    await page.goto('/login');

    await expect(
      page.getByRole('heading', { name: 'Entre na sua conta' }),
    ).toBeVisible();

    await expect(page.getByLabel('E-mail')).toBeVisible();
    await expect(page.getByLabel('Senha')).toBeVisible();

    await expect(
      page.getByRole('button', { name: 'Entrar' }),
    ).toBeVisible();

    await expect(
      page.getByRole('link', { name: /esqueci minha senha/i }),
    ).toHaveAttribute('href', '/forgot-password');

    await expect(
      page.getByRole('link', { name: /criar conta/i }),
    ).toHaveAttribute('href', '/register');
  });

  test('mostra mensagem quando a API rejeita as credenciais', async ({
    page,
  }) => {
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' }),
      });
    });

    await page.goto('/login');

    await page.getByLabel('E-mail').fill('pessoa@example.com');
    await page.getByLabel('Senha').fill('SenhaIncorreta123!');
    await page.getByRole('button', { name: 'Entrar' }).click();

    await expect(page.getByRole('alert')).toContainText(
      'E-mail ou senha inválidos.',
    );

    await expect(page).toHaveURL(/\/login$/);
  });

  test('redireciona para login ao acessar análise sem autenticação', async ({
    page,
  }) => {
    await page.goto('/analysis');

    await expect(page).toHaveURL(/\/login$/);
    await expect(
      page.getByRole('heading', { name: 'Entre na sua conta' }),
    ).toBeVisible();
  });
});
