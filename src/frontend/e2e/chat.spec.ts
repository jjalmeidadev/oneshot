import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('texto, fontes, métricas e navegação responsiva', async ({ page }, testInfo) => {
  await page.goto('/');
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('prazo');
  await page.getByRole('button', { name: 'Enviar mensagem' }).click();
  await expect(
    page.getByRole('log').getByText('Resposta para: prazo.', { exact: false }),
  ).toBeVisible();
  await page.getByRole('button', { name: /Documentos recuperados/ }).click();
  if (testInfo.project.name === 'desktop')
    await page.getByRole('button', { name: /Documentos recuperados/ }).click();
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

test('gravação sintética, WAV, upload e resposta pelo backend', async ({
  page,
}, testInfo) => {
  await page.goto('/');
  if (testInfo.project.name === 'mobile')
    await page.getByRole('button', { name: 'Abrir conversas' }).click();
  await page.getByLabel('Token de acesso para áudio').fill('e2e-token');
  if (testInfo.project.name === 'mobile')
    await page.getByRole('button', { name: 'Fechar menu' }).click();
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
