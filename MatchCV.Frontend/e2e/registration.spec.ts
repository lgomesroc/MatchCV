
import { expect, test } from '@playwright/test';

test.describe('Cadastro', () => {
  test('não permite cadastro com senha que não atende aos requisitos', async ({
    page,
  }) => {
    await page.goto('/register');

    await page.getByLabel('Nome').fill('Pessoa Teste');
    await page.getByLabel('E-mail').fill('pessoa@example.com');
    await page.getByLabel('Senha', { exact: true }).fill('senha-fraca');
    await page.getByLabel('Repita a senha').fill('senha-fraca');

    await expect(
      page.getByRole('button', { name: 'Criar conta' }),
    ).toBeDisabled();
  });

  test('mostra erro quando as senhas são diferentes', async ({ page }) => {
    await page.goto('/register');

    await page.getByLabel('Nome').fill('Pessoa Teste');
    await page.getByLabel('E-mail').fill('pessoa@example.com');
    await page.getByLabel('Senha', { exact: true }).fill('SenhaForte123!');
    await page.getByLabel('Repita a senha').fill('OutraSenha123!');

    await expect(page.getByRole('alert')).toContainText(
      'As senhas não coincidem.',
    );

    await expect(
      page.getByRole('button', { name: 'Criar conta' }),
    ).toBeDisabled();
  });

  test('cadastra a conta e encaminha para login após sucesso da API', async ({
    page,
  }) => {
    let submittedBody: Record<string, unknown> | undefined;

    await page.route('**/api/v1/auth/register', async (route) => {
      submittedBody = route.request().postDataJSON();

      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'e2e-user',
          name: 'Pessoa Teste',
          email: 'pessoa@example.com',
        }),
      });
    });

    await page.goto('/register');

    await page.getByLabel('Nome').fill('Pessoa Teste');
    await page.getByLabel('E-mail').fill('pessoa@example.com');
    await page.getByLabel('Senha', { exact: true }).fill('SenhaForte123!');
    await page.getByLabel('Repita a senha').fill('SenhaForte123!');

    await page.getByRole('button', { name: 'Criar conta' }).click();

    await expect(page).toHaveURL(/\/login\?registered=true$/);
    await expect(page.getByRole('status')).toBeVisible();

    expect(submittedBody).toEqual({
      name: 'Pessoa Teste',
      email: 'pessoa@example.com',
      password: 'SenhaForte123!',
    });
  });
});
