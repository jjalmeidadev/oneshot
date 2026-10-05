import { test, expect, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * S5-21: a interface precisa funcionar nas três larguras dos projetos do
 * Playwright (desktop 1440, tablet 768 e celular 390) sem rolagem horizontal,
 * sem violação na verificação automática e com o fluxo principal operável só
 * pelo teclado.
 */

const WCAG_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

async function expectNoHorizontalScroll(page: Page) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);
}

async function expectNoAxeViolations(page: Page, state: string) {
  // Espera as animações de entrada terminarem para medir o contraste final.
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((a) => a.effect?.getTiming().iterations !== Infinity)
        .map((a) => a.finished.catch(() => undefined)),
    ),
  );
  const { violations } = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
  expect(
    violations.map((v) => ({
      state,
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.map((n) => n.target.join(' ')),
    })),
  ).toEqual([]);
}

async function ask(page: Page, text: string) {
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill(text);
  await input.press('Enter');
  await expect(
    page.getByRole('log').getByText(`Resposta para: ${text}.`, { exact: false }),
  ).toBeVisible();
}

for (const scheme of ['light', 'dark'] as const) {
  test(`largura e verificação automática nos estados principais (${scheme})`, async ({
    page,
  }) => {
    await page.emulateMedia({ colorScheme: scheme });
    await page.goto('/');
    await expectNoHorizontalScroll(page);
    await expectNoAxeViolations(page, 'vazio');

    await ask(page, 'prazo do projeto PRJ-0442 e próximos marcos do cronograma');
    await expectNoHorizontalScroll(page);
    await expectNoAxeViolations(page, 'resposta');

    await page.getByRole('button', { name: 'Ajustes do agente' }).click();
    await expect(page.getByRole('dialog', { name: 'Ajustes do agente' })).toBeVisible();
    await expectNoHorizontalScroll(page);
    await expectNoAxeViolations(page, 'ajustes');
    await page.getByRole('switch', { name: 'Mostrar detalhes técnicos' }).click();
    await page.keyboard.press('Escape');

    await page.getByRole('button', { name: /da última resposta/ }).click();
    await expect(
      page.getByRole('heading', { name: /Fontes da resposta/ }),
    ).toBeVisible();
    await expectNoHorizontalScroll(page);
    await expectNoAxeViolations(page, 'fontes e modo técnico');
  });
}

test('fluxo principal só pelo teclado', async ({ page }, testInfo) => {
  const wide = testInfo.project.name === 'desktop';
  await page.goto('/');
  // Espera a interface montar antes do primeiro Tab.
  await expect(
    page.getByRole('textbox', { name: 'Mensagem para o agente' }),
  ).toBeVisible();

  // O primeiro Tab revela o atalho que leva direto ao campo de mensagem.
  await page.keyboard.press('Tab');
  const skip = page.getByRole('link', { name: 'Pular para o campo de mensagem' });
  await expect(skip).toBeFocused();
  await page.keyboard.press('Enter');
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await expect(input).toBeFocused();

  await page.keyboard.type('prazo');
  await page.keyboard.press('Enter');
  await expect(
    page.getByRole('log').getByText('Resposta para: prazo.', { exact: false }),
  ).toBeVisible();

  // Volta pelo teclado até a primeira fonte citada e a abre.
  const firstSource = page.getByRole('log').getByRole('button', { name: /^1/ });
  for (
    let i = 0;
    i < 15 && !(await firstSource.evaluate((el) => el === document.activeElement));
    i++
  )
    await page.keyboard.press('Shift+Tab');
  await expect(firstSource).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByText('Trecho de teste: entrega em dezembro.')).toBeVisible();
  if (!wide) {
    // No painel deslizante, Escape fecha e devolve o foco à fonte.
    await page.keyboard.press('Escape');
    await expect(firstSource).toBeFocused();
  }

  // Ajustes: abre com Enter, alterna com Espaço e fecha com Escape.
  const settings = page.getByRole('button', { name: 'Ajustes do agente' });
  await settings.focus();
  await page.keyboard.press('Enter');
  const technical = page.getByRole('switch', { name: 'Mostrar detalhes técnicos' });
  for (
    let i = 0;
    i < 6 && !(await technical.evaluate((el) => el === document.activeElement));
    i++
  )
    await page.keyboard.press('Tab');
  await expect(technical).toBeFocused();
  await page.keyboard.press('Space');
  await expect(technical).toHaveAttribute('aria-checked', 'true');
  await page.keyboard.press('Escape');
  await expect(settings).toBeFocused();
  await expect(
    page.getByText('provedor-de-teste', { exact: true }).first(),
  ).toBeVisible();

  // Nova conversa pelo teclado (no celular e no tablet, pela gaveta de conversas).
  if (!(testInfo.project.name === 'desktop')) {
    const menu = page.getByRole('button', { name: 'Abrir conversas' });
    await menu.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('dialog', { name: 'Conversas' })).toBeVisible();
  }
  const newConversation = page.getByRole('button', { name: 'Nova conversa' });
  await newConversation.focus();
  await page.keyboard.press('Enter');
  if (!(testInfo.project.name === 'desktop')) await page.keyboard.press('Escape');
  await expect(page.getByRole('log')).toHaveCount(0);
});
