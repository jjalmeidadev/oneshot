"""O prompt e a leitura da resposta do Gemini."""

from __future__ import annotations

from helpers import trecho

from model.generator import _extract_text, build_prompt
from model.store import SearchHit


def hits() -> list[SearchHit]:
    return [
        SearchHit(chunk=trecho("a", "Riscos"), score=0.81),
        SearchHit(chunk=trecho("b", "Cronograma"), score=0.72),
    ]


def test_o_prompt_numera_as_fontes_na_ordem():
    prompt = build_prompt("Tem marco atrasado?", hits())

    assert "[Fonte 1] Projeto.md — Riscos" in prompt
    assert "[Fonte 2] Projeto.md — Cronograma" in prompt
    assert prompt.index("[Fonte 1]") < prompt.index("[Fonte 2]")
    assert "Tem marco atrasado?" in prompt


def test_o_prompt_proibe_completar_de_cabeca():
    prompt = build_prompt("Qualquer coisa", hits())
    assert "apenas com o que estiver nos trechos" in prompt
    assert "nunca complete com conhecimento próprio" in prompt


def test_sem_trechos_o_prompt_manda_dizer_que_nao_encontrou():
    prompt = build_prompt("Qual a cor do céu?", [])
    assert "Nenhum trecho da documentação foi recuperado" in prompt
    assert "não encontrou" in prompt


def test_leitura_do_texto_da_resposta():
    corpo = {
        "steps": [
            {"type": "tool_call", "content": [{"type": "text", "text": "ignorar"}]},
            {
                "type": "model_output",
                "content": [
                    {"type": "text", "text": "Em andamento."},
                    {"type": "image", "text": "não é texto"},
                ],
            },
            {"type": "model_output", "content": [{"type": "text", "text": "Fonte: TAP."}]},
        ]
    }
    assert _extract_text(corpo) == "Em andamento.\n\nFonte: TAP."


def test_resposta_sem_saida_do_modelo_da_texto_vazio():
    assert _extract_text({"steps": [{"type": "tool_call", "content": []}]}) == ""
