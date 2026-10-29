import { expect, test, type Page } from '@playwright/test';
import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

const live = process.env.MATCHCV_LIVE_SERVICES === 'true';
const frontendURL = process.env.MATCHCV_LIVE_FRONTEND_URL;
const apiBaseURL = (process.env.MATCHCV_LIVE_API_URL ?? '').replace(/\/$/, '');
const confirm = process.env.MATCHCV_LIVE_CONFIRM_PRODUCTION;
const quota = 3;
const adminEmail = process.env.MATCHCV_LIVE_ADMIN_EMAIL;
const adminPassword = process.env.MATCHCV_LIVE_ADMIN_PASSWORD;

const jobDescription =
  'Vaga de teste sintética: desenvolver APIs REST, escrever testes automatizados, utilizar SQL Server e documentar serviços backend. Não representa uma vaga real.';
const resumeText =
  'Currículo de teste sintético: desenvolvedor backend de demonstração, com prática em APIs REST, testes automatizados e consultas SQL. Este texto não contém dados pessoais.';

type Session = { email: string; password: string; token: string; id: string; role: string };

function required(name: string, value: string | undefined): string {
  if (!value?.trim()) throw new Error(`Variável obrigatória ausente: ${name}`);
  return value.trim();
}

async function waitForAnalysis(
  request: import('@playwright/test').APIRequestContext,
  token: string,
  analysisId: string,
  timeoutMs = 12 * 60 * 1000,
) {
  const deadline = Date.now() + timeoutMs;
  let lastStatus = 'unknown';
  while (Date.now() < deadline) {
    const response = await request.get(`${apiBaseURL}/api/v1/analysis/${analysisId}`, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 45_000,
    });
    if (!response.ok()) {
      throw new Error(`Polling da análise retornou HTTP ${response.status()}: ${(await response.text()).slice(0, 300)}`);
    }
    const result = await response.json();
    lastStatus = result.status;
    if (result.status === 'completed') {
      for (const field of ['evidenced_requirements', 'unevidenced_requirements', 'gaps', 'resume_issues', 'suggestions']) {
        expect(result[field], `campo ${field} no resultado`).toBeInstanceOf(Array);
      }
      return result;
    }
    if (result.status === 'failed') {
      throw new Error(`A análise ${analysisId} terminou como failed.`);
    }
    await new Promise((resolve) => setTimeout(resolve, 2_000));
  }
  throw new Error(`Timeout esperando análise ${analysisId}; último status: ${lastStatus}`);
}

async function register(page: Page, email: string, name: string, password: string) {
  const responsePromise = page.waitForResponse((r) =>
    r.url().includes('/api/v1/auth/register') && r.request().method() === 'POST',
  );
  await page.goto('/register');
  await page.getByLabel('Nome').fill(name);
  await page.getByLabel('E-mail').fill(email);
  await page.getByLabel('Senha', { exact: true }).fill(password);
  await page.getByLabel('Repita a senha').fill(password);
  await page.getByRole('button', { name: 'Criar conta' }).click();
  const response = await responsePromise;
  expect(response.status(), 'cadastro pela API').toBe(201);
  await expect(page).toHaveURL(/\/login\?registered=true$/);
}

async function login(page: Page, email: string, password: string): Promise<Session> {
  const responsePromise = page.waitForResponse((r) =>
    r.url().includes('/api/v1/auth/login') && r.request().method() === 'POST',
  );
  await page.goto('/login');
  await page.getByLabel('E-mail').fill(email);
  await page.getByLabel('Senha').fill(password);
  await page.getByRole('button', { name: 'Entrar' }).click();
  const response = await responsePromise;
  expect(response.status(), 'login pela API').toBe(200);
  const payload = await response.json();
  expect(payload.access_token).toBeTruthy();
  expect(payload.user.id).toBeTruthy();
  await expect(page).toHaveURL(/\/analysis$/);
  const me = await page.request.get(`${apiBaseURL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${payload.access_token}` },
  });
  expect(me.status(), 'sessão autenticada /me').toBe(200);
  return {
    email,
    password,
    token: payload.access_token,
    id: payload.user.id,
    role: payload.user.role,
  };
}

function createSyntheticPdf(): Buffer {
  const stream = 'BT /F1 10 Tf 20 100 Td (Synthetic test resume: backend developer, REST APIs, automated tests, SQL.) Tj ET\n';
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${Buffer.byteLength(stream, 'ascii')} >>\nstream\n${stream}endstream`,
  ];
  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  for (let index = 0; index < objects.length; index++) {
    offsets.push(Buffer.byteLength(pdf, 'ascii'));
    pdf += `${index + 1} 0 obj\n${objects[index]}\nendobj\n`;
  }
  const xrefOffset = Buffer.byteLength(pdf, 'ascii');
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets.slice(1)) {
    pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return Buffer.from(pdf, 'ascii');
}

async function submitAnalysis(page: Page, mode: 'text' | 'file') {
  await page.goto('/analysis');
  await page.getByLabel('Descrição da vaga').fill(jobDescription);
  if (mode === 'text') {
    await page.getByLabel('Seu currículo').fill(resumeText);
  } else {
    const pdf = createSyntheticPdf();
    await page.locator('input[type="file"]').setInputFiles({
      name: 'synthetic-test-resume.pdf',
      mimeType: 'application/pdf',
      buffer: pdf,
    });
  }
  const submission = page.waitForResponse((r) =>
    r.url().includes('/api/v1/analysis/resume') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: /analisar currículo/i }).click();
  const response = await submission;
  expect(response.status(), `submissão de análise ${mode}`).toBe(202);
  const queued = await response.json();
  expect(queued.analysis_id).toBeTruthy();
  await expect(page.getByText(/processando|análise em andamento/i)).toBeVisible({ timeout: 30_000 }).catch(() => undefined);
  await expect(page.getByRole('heading', { name: 'Resultado da análise' })).toBeVisible({ timeout: 12 * 60 * 1000 });
  for (const heading of ['Requisitos evidenciados', 'Não evidenciados', 'Lacunas identificadas', 'Pontos de atenção', 'Sugestões']) {
    await expect(page.getByText(heading, { exact: true })).toBeVisible();
  }
  return queued.analysis_id as string;
}

test.describe('Fluxo real completo: Angular → API → SQL Server → fila → worker → IA → resultado', () => {
  test.skip(!live, 'Defina MATCHCV_LIVE_SERVICES=true para executar contra os serviços publicados.');

  test('cadastro, login, análises por texto e PDF, isolamento, cota e resultado real', async ({ page, request }) => {
    expect(frontendURL, 'URL do Angular publicado').toBeTruthy();
    expect(apiBaseURL, 'URL base da API publicada').toBeTruthy();
    expect(confirm, 'confirmação para gerar dados reais').toBe('YES');
    expect(apiBaseURL).toMatch(/^https:\/\//);
    expect(frontendURL).toMatch(/^https:\/\//);
    expect(Number.isInteger(quota) && quota > 0).toBeTruthy();

    const suffix = randomUUID().replaceAll('-', '').slice(0, 14);
    const password = `LiveTest-${randomUUID()}-Aa1!`;
    const userEmail = `matchcv.live.${suffix}@example.com`;
    const otherEmail = `matchcv.other.${suffix}@example.com`;
    const name = 'MatchCV Teste E2E';
    const report: Record<string, unknown> = {
      startedAt: new Date().toISOString(),
      frontendURL,
      apiBaseURL,
      syntheticDataOnly: true,
      checks: [],
    };
    const checks = report.checks as string[];

    try {
      const health = await request.get(`${apiBaseURL}/health`, { timeout: 45_000 });
      expect(health.status(), 'health da API').toBe(200);
      expect((await health.json()).status).toBe('ok');
      checks.push('API health real');

      await register(page, userEmail, name, password);
      checks.push('Cadastro real pela interface Angular');

      const user = await login(page, userEmail, password);
      expect(user.role).not.toBe('admin');
      checks.push('Login e /auth/me reais');

      const textId = await submitAnalysis(page, 'text');
      const textResult = await waitForAnalysis(request, user.token, textId);
      checks.push('Análise por texto concluída pelo worker e provedor de IA');
      report.textAnalysis = { id: textId, status: textResult.status };

      const fileId = await submitAnalysis(page, 'file');
      const fileResult = await waitForAnalysis(request, user.token, fileId);
      checks.push('Análise por arquivo PDF concluída pelo worker e provedor de IA');
      report.fileAnalysis = { id: fileId, status: fileResult.status };

      await register(page, otherEmail, name, password);
      const other = await login(page, otherEmail, password);
      const denied = await request.get(`${apiBaseURL}/api/v1/analysis/${textId}`, {
        headers: { Authorization: `Bearer ${other.token}` },
      });
      expect([403, 404]).toContain(denied.status());
      checks.push('Usuário diferente não consegue ler análise alheia');

      const quotaResponses: number[] = [];
      for (let index = 0; index < quota + 1; index++) {
        const response = await request.post(`${apiBaseURL}/api/v1/analysis/resume`, {
          headers: { Authorization: `Bearer ${other.token}` },
          multipart: { job_description: jobDescription, resume_text: resumeText },
          timeout: 45_000,
        });
        quotaResponses.push(response.status());
        if (response.status() === 403) break;
        expect(response.status(), `envio ${index + 1} no teste de cota`).toBe(202);
        const queued = await response.json();
        expect(queued.analysis_id).toBeTruthy();
      }
      expect(quotaResponses).toContain(403);
      checks.push('Cota de usuário comum bloqueia a quarta reserva com HTTP 403');

      const admin = await login(page, required('MATCHCV_LIVE_ADMIN_EMAIL', adminEmail), required('MATCHCV_LIVE_ADMIN_PASSWORD', adminPassword));
      expect(admin.role.toLowerCase()).toBe('admin');
      for (let index = 0; index < quota + 1; index++) {
        const response = await request.post(`${apiBaseURL}/api/v1/analysis/resume`, {
          headers: { Authorization: `Bearer \${admin.token}` },
          multipart: { job_description: jobDescription, resume_text: resumeText },
          timeout: 45_000,
        });
        expect(response.status(), `envio administrativo \${index + 1}`).toBe(202);
      }
      checks.push('Administrador pode enfileirar mais de três análises sem bloqueio de cota');

      report.checks = checks;
      report.finishedAt = new Date().toISOString();
      report.outcome = 'passed';
      const output = process.env.MATCHCV_LIVE_REPORT_PATH ?? join(process.cwd(), 'test-results', 'live-services-e2e-report.json');
      await mkdir(dirname(output), { recursive: true });
      await writeFile(output, JSON.stringify(report, null, 2), { encoding: 'utf8' });
    } catch (error) {
      report.checks = checks;
      report.finishedAt = new Date().toISOString();
      report.outcome = 'failed';
      report.error = error instanceof Error ? error.message : 'Erro não identificado';
      const output = process.env.MATCHCV_LIVE_REPORT_PATH ?? join(process.cwd(), 'test-results', 'live-services-e2e-report.json');
      await mkdir(dirname(output), { recursive: true });
      await writeFile(output, JSON.stringify(report, null, 2), { encoding: 'utf8' });
      throw error;
    }
  });
});
