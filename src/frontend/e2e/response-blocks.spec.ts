import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { response } from '../src/tests/fixtures';
import { responseBlocks } from '../src/tests/response-blocks-fixture';

for (const theme of ['light', 'dark']) {
  test(`blocos, contraste AA e teclado no tema ${theme}`, async ({
    page,
  }, testInfo) => {
    await page.route('**/api/**', async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (!path.startsWith('/api/')) {
        await route.continue();
        return;
      }
      const payload =
        path === '/api/access/login'
          ? {
              access_token: 'synthetic-test-token',
              profile: {
                display_name: 'Pessoa de teste',
                email: 'teste@example.org',
                role_name: 'PMO',
                profile_key: 'pmo',
                scope_label: 'Teste',
                can_read: true,
                can_write: true,
                can_export: true,
              },
            }
          : path === '/api/chat'
            ? {
                ...response,
                contract_version: '1.2.0',
                blocks: responseBlocks,
                proactive_suggestion: null,
              }
            : path === '/api/notifications'
              ? { items: [], unread_count: 0 }
              : [];
      await route.fulfill({ json: payload });
    });
    await page.route('**/health', (route) => route.fulfill({ json: { status: 'ok' } }));
    await page.goto('/');
    await page.getByLabel('Persona').selectOption('pmo');
    await page.getByLabel('Senha', { exact: true }).fill('synthetic-test-password');
    await page.getByRole('button', { name: 'Entrar', exact: true }).click();
    await expect(page.getByLabel('Mensagem para o agente')).toBeVisible();
    if (theme === 'dark') {
      if (testInfo.project.name !== 'desktop')
        await page.getByRole('button', { name: 'Abrir conversas' }).click();
      await page.getByRole('button', { name: /tema escuro/i }).click();
      await expect(page.locator('html')).toHaveClass(/dark/);
      if (testInfo.project.name !== 'desktop') await page.keyboard.press('Escape');
    }
    await page.getByLabel('Mensagem para o agente').fill('Mostre o avanço');
    await page.getByRole('button', { name: 'Enviar mensagem' }).click();
    const log = page.getByRole('log');
    await expect(log.getByRole('table', { name: 'Tabela da resposta' })).toBeVisible();
    await expect(log.getByRole('region', { name: 'Indicador: Avanço' })).toContainText(
      '42,5%',
    );
    await expect(
      log.getByRole('complementary', { name: 'Destaque da resposta' }),
    ).toContainText('Status: Em andamento');
    // Visibilidade não garante o fim da animação de entrada da mensagem.
    // Medir contraste apenas quando o ancestral animado estiver opaco.
    const responseMessage = log
      .locator(':scope > div')
      .filter({ has: page.getByRole('table', { name: 'Tabela da resposta' }) });
    await expect(responseMessage).toHaveCSS('opacity', '1');
    const tableRegion = log.getByRole('region', { name: /Tabela da resposta/ });
    await tableRegion.focus();
    await expect(tableRegion).toBeFocused();
    const results = await new AxeBuilder({ page })
      .include('[aria-label="Dados em destaque da resposta"]')
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    expect(results.violations).toEqual([]);
    // Não aceitar análise inconclusiva de contraste como aprovação.
    expect(results.incomplete.filter((item) => item.id === 'color-contrast')).toEqual(
      [],
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `../../docs/evidencias/sprint-05/blocos-271-${testInfo.project.name}-${theme}.png`,
    });
    const source = log.getByRole('button', { name: /Consultar Fonte 1/ }).first();
    await source.focus();
    await page.keyboard.press('Enter');
    await expect(
      page.getByText('Entrega prevista para dezembro.', { exact: true }),
    ).toBeVisible();
  });
}
