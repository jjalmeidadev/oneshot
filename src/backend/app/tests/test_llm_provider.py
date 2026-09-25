"""Selecao do provedor de LLM e contrato da chamada ao OpenRouter.

O cliente passou a aceitar dois provedores por `LLM_PROVIDER`: o Gemini direto,
que continua sendo o padrao, e o OpenRouter. A motivacao foi medir o RNF05 fora
do Free Tier do Gemini, cujo piso de latencia para uma chamada trivial ficou
entre 15 s e 37 s — acima do teto de 10 s do requisito para o pipeline inteiro.

Estes testes fixam tres coisas: o padrao nao mudou, o OpenRouter recebe o mesmo
prompt que o Gemini receberia, e um provedor mal configurado falha de forma
controlada em vez de cair silenciosamente no outro.
"""

import json

import pytest

from app.gemini import client
from app.gemini.client import GeminiAPIError, GeminiConfigurationError


class RespostaFalsa:
    def __init__(self, corpo: dict) -> None:
        self.corpo = corpo

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.corpo).encode("utf-8")


def _resposta_openrouter(texto: str = "Resposta com [Fonte 1].") -> dict:
    return {
        "id": "gen-abc123",
        "model": "google/gemini-3.7-flash",
        "choices": [{"message": {"role": "assistant", "content": texto}}],
        "usage": {
            "prompt_tokens": 640,
            "completion_tokens": 150,
            "total_tokens": 790,
            "completion_tokens_details": {"reasoning_tokens": 12},
        },
    }


@pytest.fixture
def captura(monkeypatch):
    """Substitui o urlopen e guarda a requisicao que o cliente montou."""

    enviado: dict = {}

    def urlopen_falso(requisicao, timeout):
        enviado["url"] = requisicao.full_url
        enviado["cabecalhos"] = {k.lower(): v for k, v in requisicao.header_items()}
        enviado["corpo"] = json.loads(requisicao.data.decode("utf-8"))
        return RespostaFalsa(enviado.get("resposta", _resposta_openrouter()))

    monkeypatch.setattr(client, "urlopen", urlopen_falso)
    return enviado


class TestSelecaoDoProvedor:
    def test_padrao_continua_sendo_o_gemini(self):
        assert client._provider() == "gemini"

    def test_openrouter_e_selecionado_por_configuracao(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")

        assert client._provider() == "openrouter"

    def test_valor_normalizado_para_minusculas(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "  OpenRouter ")

        assert client._provider() == "openrouter"

    def test_provedor_desconhecido_falha_em_vez_de_cair_no_padrao(self, monkeypatch):
        """Um erro de digitacao nao pode levar a medir o provedor errado."""

        monkeypatch.setenv("LLM_PROVIDER", "openrotuer")

        with pytest.raises(GeminiConfigurationError, match="LLM_PROVIDER invalido"):
            client._provider()


class TestChaveDoProvedor:
    def test_gemini_exige_a_propria_chave(self):
        with pytest.raises(GeminiConfigurationError, match="GEMINI_API_KEY"):
            client._api_key()

    def test_openrouter_exige_a_propria_chave(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("GEMINI_API_KEY", "chave-do-gemini")

        with pytest.raises(GeminiConfigurationError, match="OPENROUTER_API_KEY"):
            client._api_key()

    def test_openrouter_nao_usa_a_chave_do_gemini(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("GEMINI_API_KEY", "chave-do-gemini")
        monkeypatch.setenv("OPENROUTER_API_KEY", "chave-do-openrouter")

        assert client._api_key() == "chave-do-openrouter"


class TestChamadaAoOpenRouter:
    def test_usa_o_endpoint_e_a_autenticacao_do_openrouter(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")

        client._call_llm("prompt", api_key="sk-or-teste")

        assert captura["url"] == client.OPENROUTER_CHAT_URL
        assert captura["cabecalhos"]["authorization"] == "Bearer sk-or-teste"
        assert "x-goog-api-key" not in captura["cabecalhos"]

    def test_prompt_chega_identico_ao_que_o_gemini_receberia(self, monkeypatch, captura):
        """Trocar de provedor nao pode mudar o que o modelo le."""

        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        prompt = "[Fonte 1] Titulo\nVigencia: de 2026-08-24 a 2026-08-28\nPergunta: x"

        client._call_llm(prompt, api_key="k")

        assert captura["corpo"]["messages"] == [{"role": "user", "content": prompt}]

    def test_modelo_padrao_e_o_mesmo_do_mvp(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")

        client._call_llm("p", api_key="k")

        assert captura["corpo"]["model"] == "google/gemini-3.7-flash"

    def test_modelo_configuravel(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")

        client._call_llm("p", api_key="k")

        assert captura["corpo"]["model"] == "google/gemini-2.5-flash-lite"

    def test_limites_de_geracao_sao_repassados(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("GEMINI_MAX_OUTPUT_TOKENS", "256")
        monkeypatch.setenv("GEMINI_THINKING_LEVEL", "minimal")

        client._call_llm("p", api_key="k")

        assert captura["corpo"]["max_tokens"] == 256
        assert captura["corpo"]["reasoning"] == {"effort": "minimal"}

    def test_resposta_normalizada_para_o_contrato_do_backend(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")

        resultado = client._call_llm("p", api_key="k")

        assert resultado.text == "Resposta com [Fonte 1]."
        assert resultado.model == "google/gemini-3.7-flash"
        assert resultado.interaction_id == "gen-abc123"
        assert resultado.usage.input_tokens == 640
        assert resultado.usage.output_tokens == 150
        assert resultado.usage.thought_tokens == 12
        assert resultado.usage.total_tokens == 790
        assert resultado.latency_ms >= 0

    def test_conteudo_em_partes_e_concatenado(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        captura["resposta"] = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "Primeira parte."},
                            {"type": "text", "text": "Segunda parte."},
                        ]
                    }
                }
            ]
        }

        resultado = client._call_llm("p", api_key="k")

        assert resultado.text == "Primeira parte.\n\nSegunda parte."

    def test_resposta_sem_texto_e_erro_controlado(self, monkeypatch, captura):
        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        captura["resposta"] = {"choices": []}

        with pytest.raises(GeminiAPIError, match="nao retornou conteudo"):
            client._call_llm("p", api_key="k")

    def test_continuidade_de_conversa_e_ignorada_sem_quebrar(self, monkeypatch, captura):
        """O OpenRouter nao guarda estado: o id anterior nao pode vazar no corpo."""

        monkeypatch.setenv("LLM_PROVIDER", "openrouter")

        client._call_llm("p", api_key="k", previous_interaction_id="v1_anterior")

        assert "previous_interaction_id" not in captura["corpo"]


class TestGeminiDiretoInalterado:
    def test_gemini_continua_no_endpoint_de_interactions(self, captura):
        captura["resposta"] = {
            "id": "v1_x",
            "model": "gemini-3.7-flash",
            "steps": [
                {"type": "model_output", "content": [{"type": "text", "text": "ok"}]}
            ],
        }

        resultado = client._call_llm(
            "p", api_key="chave", previous_interaction_id="v1_anterior"
        )

        assert captura["url"] == client.GEMINI_INTERACTIONS_URL
        assert captura["cabecalhos"]["x-goog-api-key"] == "chave"
        assert captura["corpo"]["input"] == "p"
        assert captura["corpo"]["previous_interaction_id"] == "v1_anterior"
        assert resultado.text == "ok"
