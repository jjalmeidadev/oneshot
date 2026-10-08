import { test, expect, type Page, type Route } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Cartao de alteracao de dados pelo chat (S5-07) nos tres tamanhos de tela.
 *
 * O servidor E2E so autentica a persona PMO e nao tem as rotas da S5-06, entao
 * a resposta do chat e as rotas do cartao sao simuladas com `page.route`. A
 * permissao de escrita e verificada no backend (S5-06); aqui o foco e a
 * interface: previa, confirmacao, cancelamento, erro, desfazer e historico.
 */

const WCAG_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

const preview = {
  pending_change_id: '7b022b89-6b47-4028-a3fd-e1e144846011',
  project: {
    code: 'PRJ-0442',
    title: 'Modernizacao do Sistema de Sinalizacao da Linha Azul',
  },
  target: {
    entity: 'projeto',
    id: 'f4022396-603b-416d-abe1-5f91e1fdc37f',
    label: 'PRJ-0442',
  },
  field: { key: 'projeto.prazo_final', label: 'Prazo final previsto' },
  before: { value: '2026-12-20', display: '20/12/2026' },
  after: { value: '2027-03-31', display: '31/03/2027' },
  warnings: ['A data informada já passou.'],
  expires_at: new Date(Date.now() + 10 * 60_000).toISOString(),
  undo_window_minutes: 15,
};

const chatBody = {
  text: 'Confira a alteração antes de confirmar. Prazo final previsto de PRJ-0442: 20/12/2026 → 31/03/2027. Nada foi gravado ainda; a prévia vale por 10 minutos.',
  model: 'alteracao-dados-chat',
  interaction_id: null,
  trace_id: 'aa077c94-0bdb-4538-90ce-a6c6c3b2de3e',
  latency_ms: 0,
  retrieval_ms: 0,
  usage: { input_tokens: 0, output_tokens: 0, thought_tokens: 0, total_tokens: 0 },
  sources: [],
  data_change: { status: 'preview', preview },
};

const applied = {
  change_id: '312c0d1a-3959-4628-9be1-f834a49f26ab',
  status: 'aplicada',
  field: preview.field,
  target: preview.target,
  before: preview.before,
  after: preview.after,
  applied_at: new Date().toISOString(),
  undo_available_until: new Date(Date.now() + 15 * 60_000).toISOString(),
  correlation_id: 'correlacao-1',
};

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

async function openPreview(page: Page) {
  await page.route('**/api/chat', (route) => json(route, chatBody));
  await page.goto('/');
  await page.getByLabel('Persona').selectOption('pmo');
  await page.getByLabel('Senha', { exact: true }).fill('e2e-password');
  await page.getByRole('button', { name: 'Entrar' }).click();
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('Prorroga o prazo do PRJ-0442 para 31/03/2027');
  await input.press('Enter');
  const card = page.getByRole('region', { name: 'Alteração de dados' });
  await expect(card).toBeVisible();
  return card;
}

async function expectAccessible(page: Page, state: string) {
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((a) => a.effect?.getTiming().iterations !== Infinity)
        .map((a) => a.finished.catch(() => undefined)),
    ),
  );
  const { violations } = await new AxeBuilder({ page })
    .include('section[aria-label="Alteração de dados"]')
    .withTags(WCAG_TAGS)
    .analyze();
  expect(
    violations.map((v) => ({
      state,
      id: v.id,
      nodes: v.nodes.map(
        (n) => n.target.join(' ') + ' :: ' + (n.any[0]?.message ?? ''),
      ),
    })),
  ).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
}

for (const scheme of ['light', 'dark'] as const) {
  test(`prévia, confirmação, histórico e desfazer (${scheme})`, async ({
    page,
  }, testInfo) => {
    await page.emulateMedia({ colorScheme: scheme });
    let confirmBody: unknown = null;
    await page.route('**/api/data-change-previews/*/confirm', async (route) => {
      confirmBody = route.request().postDataJSON();
      await json(route, applied);
    });
    await page.route('**/api/data-changes?*', (route) =>
      json(route, {
        items: [
          {
            ...applied,
            requested_by: '[DEMO] Gerente de Projeto',
            status: 'aplicada',
            can_undo: true,
            undo_available_until: applied.undo_available_until,
          },
        ],
      }),
    );
    await page.route('**/api/data-changes/*/undo', (route) =>
      json(route, {
        change_id: applied.change_id,
        status: 'desfeita',
        restored: preview.before,
        undone_at: new Date().toISOString(),
      }),
    );

    const card = await openPreview(page);
    await expect(card.getByText('Antes')).toBeVisible();
    await expect(card.getByText('31/03/2027')).toBeVisible();
    await expect(card.getByRole('list', { name: 'Avisos' })).toContainText('já passou');
    await expectAccessible(page, `previa ${scheme}`);
    await page.screenshot({
      path: testInfo.outputPath(`previa-${scheme}-${testInfo.project.name}.png`),
      fullPage: false,
    });

    await card.getByLabel(/Justificativa/).fill('Replanejamento aprovado em 03/10');
    await card.getByRole('button', { name: 'Confirmar alteração' }).click();
    await expect(card.getByRole('status')).toContainText('Alteração gravada');
    expect(confirmBody).toEqual({ reason: 'Replanejamento aprovado em 03/10' });
    // O foco vai para o resultado, e nao para o inicio da pagina.
    await expect(card.locator('[tabindex="-1"]')).toBeFocused();

    await card.getByRole('button', { name: 'Histórico do campo' }).click();
    await expect(card.getByRole('list', { name: 'Alterações do campo' })).toContainText(
      '[DEMO] Gerente de Projeto',
    );
    await expectAccessible(page, `confirmada ${scheme}`);
    await page.screenshot({
      path: testInfo.outputPath(`confirmada-${scheme}-${testInfo.project.name}.png`),
      fullPage: false,
    });

    await card.getByRole('button', { name: 'Desfazer' }).click();
    await expect(card.getByRole('status')).toContainText('voltou para 20/12/2026');
  });
}

test('cancelamento não grava e erro final não oferece repetir', async ({
  page,
}, testInfo) => {
  await page.route('**/api/data-change-previews/*/cancel', (route) =>
    json(route, { status: 'cancelada' }),
  );
  const card = await openPreview(page);
  await card.getByRole('button', { name: 'Cancelar' }).click();
  await expect(card.getByRole('status')).toHaveText(
    'Alteração cancelada. Nada foi gravado.',
  );
  await expect(card.getByRole('button', { name: 'Confirmar alteração' })).toHaveCount(
    0,
  );
  await card.screenshot({
    path: testInfo.outputPath(`cancelada-${testInfo.project.name}.png`),
  });

  await page.unroute('**/api/chat');
  await page.route('**/api/chat', (route) => json(route, chatBody));
  await page.route('**/api/data-change-previews/*/confirm', (route) =>
    json(
      route,
      {
        error: {
          code: 'STALE_PREVIEW',
          message:
            'O valor mudou depois da prévia. Peça a alteração de novo para conferir o valor atual.',
        },
      },
      409,
    ),
  );
  const input = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await input.fill('Prorroga o prazo do PRJ-0442 para 31/03/2027');
  await input.press('Enter');
  const second = page.getByRole('region', { name: 'Alteração de dados' }).last();
  await second.getByRole('button', { name: 'Confirmar alteração' }).click();
  await expect(second.getByRole('alert')).toContainText(
    'O valor mudou depois da prévia',
  );
  await expect(
    second.getByRole('button', { name: /Confirmar|Tentar de novo/ }),
  ).toHaveCount(0);
  await expectAccessible(page, 'erro');
  await second.screenshot({
    path: testInfo.outputPath(`erro-${testInfo.project.name}.png`),
  });
});
