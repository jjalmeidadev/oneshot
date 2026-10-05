import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readFile } from 'node:fs/promises';

/** O token fica na engrenagem de ajustes, no cabeçalho, nos dois tamanhos. */
async function authenticate(page: import('@playwright/test').Page) {
  await page.getByRole('button', { name: 'Ajustes do agente' }).click();
  await page.getByLabel('Token de acesso da sessão').fill('e2e-token');
  await page.keyboard.press('Escape');
}

test('texto, fontes, modo técnico e navegação responsiva', async ({
  page,
}, testInfo) => {
  await page.goto('/');
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('prazo');
  await page.getByRole('button', { name: 'Enviar mensagem' }).click();
  await expect(
    page.getByRole('log').getByText('Resposta para: prazo.', { exact: false }),
  ).toBeVisible();
  // Tela padrão: sem modelo nem métricas; o painel de fontes começa fechado.
  await expect(page.getByText('provedor-de-teste', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('switch')).toHaveCount(0);
  await page.getByRole('button', { name: 'Ajustes do agente' }).click();
  await page.getByRole('switch', { name: 'Mostrar detalhes técnicos' }).click();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: /Fontes da resposta/ }).click();
  await expect(page.getByText('Trecho de teste: entrega em dezembro.')).toBeVisible();
  await page.getByRole('tab', { name: 'Resposta', exact: true }).click();
  await expect(
    page.getByText('provedor-de-teste', { exact: true }).last(),
  ).toBeVisible();
  if (testInfo.project.name === 'mobile') await page.keyboard.press('Escape');
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});

test('falha controlada, recuperação e interrupção', async ({ page }) => {
  await page.goto('/');
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('falha');
  await input.press('Enter');
  await expect(page.getByRole('alert')).toContainText('indisponível');
  await expect(page.getByRole('alert')).not.toContainText('privado');
  await input.fill('demorada');
  await input.press('Enter');
  await page.getByRole('button', { name: 'Interromper resposta' }).click();
  await expect(page.getByRole('button', { name: 'Enviar mensagem' })).toBeVisible();
  await input.fill('recuperada');
  await input.press('Enter');
  await expect(
    page.getByRole('log').getByText('Resposta para: recuperada.', { exact: false }),
  ).toBeVisible();
  await expect(
    page.getByRole('log').getByText('Resposta para: demorada.', { exact: false }),
  ).toHaveCount(0);
});

test('gravação sintética, WAV, upload e resposta pelo backend', async ({ page }) => {
  await page.goto('/');
  await authenticate(page);
  await page.getByRole('button', { name: 'Gravar pergunta em áudio' }).click();
  await expect(page.getByRole('button', { name: 'Concluir gravação' })).toBeVisible();
  // O sinal sintético precisa de amostras suficientes para validar a duração.
  await page.waitForTimeout(1200);
  await page.getByRole('button', { name: 'Concluir gravação' }).click();
  await page.getByRole('button', { name: 'Enviar áudio' }).click();
  await expect(page.getByText('Transcrito', { exact: true })).toBeVisible();
  await expect(
    page
      .getByRole('log')
      .getByText('Resposta para: pergunta de áudio.', { exact: false }),
  ).toBeVisible();
});

test('acessibilidade automática e tema nos dois tamanhos', async ({
  page,
}, testInfo) => {
  await page.goto('/');
  if (testInfo.project.name === 'mobile')
    await page.getByRole('button', { name: 'Abrir conversas' }).click();
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();
  expect(
    results.violations.map((v) => ({
      id: v.id,
      nodes: v.nodes.map((n) => n.failureSummary),
    })),
  ).toEqual([]);
  await page.getByRole('button', { name: /tema escuro/i }).click();
  await expect(page.locator('html')).toHaveClass(/dark/);
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((a) => a.effect?.getTiming().iterations !== Infinity)
        .map((a) => a.finished.catch(() => undefined)),
    ),
  );
  const dark = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();
  expect(
    dark.violations.map((v) => ({
      id: v.id,
      nodes: v.nodes.map((n) => n.failureSummary),
    })),
  ).toEqual([]);
});

test('PLN inicia fluxo guiado e entrega DOCX baixavel no chat', async ({ page }) => {
  await page.goto('/');
  await authenticate(page);

  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('gere um relatorio executivo');
  await input.press('Enter');

  await expect(page.getByText(/abranger um projeto ou um subportfolio/i)).toBeVisible();
  await page.getByRole('button', { name: 'Projeto', exact: true }).click();
  await page.getByRole('button', { name: /PRJ-0442/ }).click();
  await page.getByLabel('Inicio').fill('2026-08-01');
  await page.getByLabel('Fim').fill('2026-08-31');
  await page.getByRole('button', { name: 'Continuar', exact: true }).click();
  await page.getByRole('button', { name: 'Diretoria', exact: true }).click();
  await page.getByRole('button', { name: 'Governanca mensal', exact: true }).click();
  await page.getByText('Cronograma', { exact: true }).click();
  await page.getByText('Riscos', { exact: true }).click();
  await page.getByRole('button', { name: 'Continuar', exact: true }).click();
  await page
    .getByPlaceholder('Contexto adicional (opcional)')
    .fill('Destacar o proximo marco.');
  await page.getByRole('button', { name: 'Adicionar e continuar' }).click();
  await expect(page.getByText('Revise antes de gerar')).toBeVisible();
  await page.getByRole('button', { name: 'Confirmar e gerar DOCX' }).click();

  const downloadButton = page.getByRole('button', { name: /Baixar no chat/ });
  await expect(downloadButton).toBeVisible({ timeout: 20_000 });
  const downloadPromise = page.waitForEvent('download');
  await downloadButton.click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.docx$/i);
  const artifactPath = await download.path();
  expect(artifactPath).not.toBeNull();
  const bytes = await readFile(artifactPath!);
  expect(bytes.subarray(0, 2).toString()).toBe('PK');
});
