import { test, expect, type Page } from '@playwright/test';

/**
 * S5-23 (#277): fluxos integrados e falhas de comunicação contra o backend.
 *
 * O backend é o `e2e_server.py`: rotas reais da API, repositórios em memória e
 * provedores determinísticos. O alerta percorre o workflow real de
 * `app/alerts` até a assinatura ficar ativa. As falhas vêm de duas origens:
 * o próprio backend (503, 502 e 500) e a rede entre a interface e a API
 * (504 de gateway, *timeout* do cliente e perda de conexão). Em todos os
 * casos a interface precisa mostrar uma mensagem controlada, sem detalhe
 * interno, e voltar a funcionar depois.
 *
 * Os outros fluxos principais já têm spec próprio: texto, áudio e relatório
 * em `chat.spec.ts`; alteração de dados em `alteracao-dados.spec.ts`.
 */

const MENSAGENS = {
  indisponivel: 'O serviço está indisponível. Tente novamente em instantes.',
  gateway: 'Não foi possível obter uma resposta do serviço. Tente novamente.',
  generica: 'Não foi possível concluir a solicitação. Tente novamente em instantes.',
  demorou: 'O processamento demorou mais que o esperado. Tente novamente.',
};

/** Trechos que nunca podem chegar à tela. */
const DETALHES_INTERNOS = [
  /privado/i,
  /traceback/i,
  /internal server error/i,
  /corpo bruto/i,
];

async function entrar(page: Page) {
  await page.goto('/');
  await page.getByLabel('Persona').selectOption('pmo');
  await page.getByLabel('Senha', { exact: true }).fill('e2e-password');
  await page.getByRole('button', { name: 'Entrar' }).click();
  const campo = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await expect(campo).toBeVisible();
  return campo;
}

async function enviar(page: Page, texto: string) {
  const campo = page.getByRole('textbox', { name: 'Mensagem para o agente' });
  await campo.fill(texto);
  await campo.press('Enter');
}

async function esperarErroControlado(page: Page, mensagem: string, timeout = 5_000) {
  const alerta = page.getByRole('alert').filter({ hasText: mensagem });
  await expect(alerta).toBeVisible({ timeout });
  for (const detalhe of DETALHES_INTERNOS) {
    await expect(alerta).not.toContainText(detalhe);
  }
}

async function esperarResposta(page: Page, texto: string) {
  await expect(
    page.getByRole('log').getByText(`Resposta para: ${texto}.`, { exact: false }),
  ).toBeVisible();
}

test.describe('fluxo integrado de alerta', () => {
  test('configura e ativa o alerta pelo workflow do backend', async ({ page }) => {
    await entrar(page);
    await enviar(page, 'Quero um alerta de atraso de prazo');

    const cartao = page.getByRole('region', { name: 'Configuracao do alerta' });
    await expect(cartao).toBeVisible();
    await expect(cartao).toContainText('Qual projeto deve ser monitorado?');
    await cartao.getByRole('button', { name: 'Projeto de Sinalizacao' }).click();

    await expect(cartao).toContainText(
      'Depois de quantos dias corridos de atraso devo avisar?',
    );
    await cartao.getByLabel('Dias de atraso').fill('5');
    await cartao.getByRole('button', { name: 'Continuar' }).click();

    await cartao.getByRole('button', { name: 'Diariamente as 08:00' }).click();
    await cartao.getByRole('button', { name: 'Nao repetir' }).click();

    await cartao.getByRole('button', { name: 'Ativar alerta' }).click();
    await expect(cartao.getByRole('status')).toContainText('Alerta ativo');

    // A assinatura existe no backend, não só na tela.
    const resposta = await page.request.get('/api/alert-subscriptions', {
      headers: { Authorization: 'Bearer e2e-token' },
    });
    expect(resposta.ok()).toBe(true);
    const assinaturas = (await resposta.json()) as {
      project_id?: string;
      status?: string;
    }[];
    expect(
      assinaturas.some((item) => JSON.stringify(item).includes('PRJ-SINALIZACAO')),
    ).toBe(true);
  });

  test('falha de comunicação no meio do workflow mostra erro e permite repetir', async ({
    page,
  }) => {
    await entrar(page);
    await enviar(page, 'Quero um alerta de atraso de prazo');
    const cartao = page.getByRole('region', { name: 'Configuracao do alerta' });
    await expect(cartao).toContainText('Qual projeto deve ser monitorado?');

    await page.route('**/api/alert-workflow-sessions/*/answers', (route) =>
      route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: '{"detail":"x"}',
      }),
    );
    await cartao.getByRole('button', { name: 'Projeto de Sinalizacao' }).click();
    await expect(cartao.getByRole('alert')).toHaveText(
      'Nao foi possivel atualizar o alerta.',
    );
    await expect(cartao).toContainText('Qual projeto deve ser monitorado?');

    await page.unroute('**/api/alert-workflow-sessions/*/answers');
    await cartao.getByRole('button', { name: 'Projeto de Sinalizacao' }).click();
    await expect(cartao).toContainText(
      'Depois de quantos dias corridos de atraso devo avisar?',
    );
    await expect(cartao.getByRole('alert')).toHaveCount(0);
  });
});

test.describe('falhas de comunicação no chat', () => {
  const falhasDoBackend = [
    { mensagem: 'falha', status: 503, esperado: MENSAGENS.indisponivel },
    { mensagem: 'falha-gateway', status: 502, esperado: MENSAGENS.gateway },
    { mensagem: 'falha-inesperada', status: 500, esperado: MENSAGENS.generica },
  ];

  for (const falha of falhasDoBackend) {
    test(`backend responde ${falha.status}: mensagem controlada e recuperação`, async ({
      page,
    }) => {
      await entrar(page);
      const resposta = page.waitForResponse('**/api/chat');
      await enviar(page, falha.mensagem);
      expect((await resposta).status()).toBe(falha.status);
      await esperarErroControlado(page, falha.esperado);

      await enviar(page, 'recuperada');
      await esperarResposta(page, 'recuperada');
    });
  }

  test('gateway responde 504: mensagem de demora e recuperação', async ({ page }) => {
    await entrar(page);
    await page.route('**/api/chat', (route) =>
      route.fulfill({
        status: 504,
        contentType: 'text/html',
        body: '<html><body>504 Gateway Time-out nginx detalhe privado</body></html>',
      }),
    );
    await enviar(page, 'consulta lenta');
    await esperarErroControlado(page, MENSAGENS.demorou);

    await page.unroute('**/api/chat');
    await enviar(page, 'recuperada');
    await esperarResposta(page, 'recuperada');
  });

  test('timeout do cliente: interrompe a espera, avisa e libera o envio', async ({
    page,
  }) => {
    // O E2E sobe o Vite com VITE_API_TIMEOUT_MS=10000 (playwright.config.ts).
    test.setTimeout(60_000);
    await entrar(page);
    await page.route('**/api/chat', () => {
      // Sem resposta: simula o backend que nunca devolve.
    });
    await enviar(page, 'consulta sem resposta');
    await expect(
      page.getByRole('button', { name: 'Interromper resposta' }),
    ).toBeVisible();
    await esperarErroControlado(page, MENSAGENS.demorou, 20_000);
    await expect(page.getByRole('button', { name: 'Enviar mensagem' })).toBeVisible();

    await page.unroute('**/api/chat');
    await enviar(page, 'recuperada');
    await esperarResposta(page, 'recuperada');
  });

  test('perda de conexão: avisa sem travar e volta quando a rede retorna', async ({
    page,
    context,
  }) => {
    await entrar(page);
    await context.setOffline(true);
    await enviar(page, 'consulta sem rede');
    await esperarErroControlado(page, MENSAGENS.generica);
    await expect(page.getByRole('button', { name: 'Enviar mensagem' })).toBeVisible();

    await context.setOffline(false);
    await enviar(page, 'recuperada');
    await esperarResposta(page, 'recuperada');
  });
});
