"""Divisão da documentação em trechos."""

from __future__ import annotations

from pathlib import Path

from model.corpus import (
    SourceDocument,
    build_chunks,
    chunk_document,
    fingerprint,
    load_documents,
    slugify,
)

MARKDOWN = """Texto de abertura, antes de qualquer cabeçalho, com tamanho suficiente para não cair no filtro de trechos vazios.

# Projeto

Introdução do projeto, com corpo suficiente para virar um trecho de verdade e não ser descartada.

## Riscos

Conteúdo sobre riscos que precisa de algum tamanho para sobreviver ao filtro mínimo de caracteres.

### R08 — Tempo insuficiente

A avaliação permanece em 16, mas o acompanhamento subiu bastante nesta sprint.

## Seção vazia

## Ferramentas

Python, FastAPI e Vite compõem a base técnica adotada pela equipe neste ciclo.
"""


def documento(texto: str = MARKDOWN) -> SourceDocument:
    return SourceDocument(
        name="Projeto.md", relative_path="Projeto.md", path=Path("Projeto.md"), text=texto
    )


def test_cabecalhos_viram_o_caminho_da_secao():
    trechos = chunk_document(documento())
    secoes = [t.section for t in trechos]

    assert "Projeto" in secoes
    assert "Projeto > Riscos" in secoes
    # A hierarquia é acumulada: o H3 carrega o H2 e o H1 acima dele.
    assert "Projeto > Riscos > R08 — Tempo insuficiente" in secoes


def test_subir_de_nivel_desempilha_a_hierarquia():
    trechos = chunk_document(documento())
    ferramentas = next(t for t in trechos if t.section.endswith("Ferramentas"))
    # Voltar para H2 não pode deixar o R08 (H3) pendurado no caminho.
    assert ferramentas.section == "Projeto > Ferramentas"


def test_secao_sem_corpo_e_descartada():
    trechos = chunk_document(documento())
    assert all("Seção vazia" not in t.section for t in trechos)


def test_texto_antes_do_primeiro_cabecalho_nao_se_perde():
    trechos = chunk_document(documento())
    assert any(t.section == "Projeto.md" for t in trechos)


def test_cabecalho_dentro_de_bloco_de_codigo_nao_conta():
    texto = (
        "# Instalação\n\nPasso a passo da instalação do ambiente de desenvolvimento.\n\n"
        "```bash\n# isto é um comentário de shell, não um cabeçalho\npip install -r requirements.txt\n```\n\n"
        "Depois disso, o serviço sobe normalmente na porta configurada pelo ambiente.\n"
    )
    trechos = chunk_document(documento(texto))
    assert all("isto é um comentário" not in t.section for t in trechos)


def test_o_texto_vetorizado_carrega_documento_e_secao():
    trechos = chunk_document(documento())
    risco = next(t for t in trechos if "R08" in t.section)
    # Sem isso, "qual o risco R08?" não casaria com um trecho que não repete
    # a palavra "risco" no corpo.
    assert risco.embed_text.startswith("Projeto.md — Projeto > Riscos > R08")
    assert risco.text in risco.embed_text


def test_secao_longa_e_dividida_respeitando_o_teto():
    corpo = "\n\n".join(f"Parágrafo {i} " + "palavra " * 60 for i in range(20))
    trechos = chunk_document(documento(f"# Longa\n\n{corpo}\n"), max_chunk_chars=1200)
    assert len(trechos) > 1
    assert all(len(t.text) <= 1400 for t in trechos)
    # Todos continuam apontando para a mesma seção.
    assert {t.section for t in trechos} == {"Longa"}


def test_ancora_segue_o_estilo_do_github():
    assert slugify("8.7 Contrato da API") == "87-contrato-da-api"
    assert slugify("R08 — Tempo insuficiente") == "r08--tempo-insuficiente"
    assert slugify("**Ferramentas** e `Tecnologias`") == "ferramentas-e-tecnologias"


def test_arquivo_sem_carregador_e_reportado(tmp_path):
    (tmp_path / "nota.md").write_text("# Nota\n\n" + "conteúdo suficiente " * 10, encoding="utf-8")
    (tmp_path / "planilha.xlsx").write_bytes(b"binario")
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "foto.png").write_bytes(b"png")

    documentos, ignorados = load_documents(tmp_path)

    assert [d.name for d in documentos] == ["nota.md"]
    # A planilha aparece como pendência explícita; a pasta de imagens é ruído
    # conhecido e não polui o relatório.
    assert ignorados == ["planilha.xlsx"]


def test_impressao_digital_muda_com_o_conteudo(tmp_path):
    arquivo = tmp_path / "doc.md"
    arquivo.write_text("# A\n\n" + "conteúdo original " * 10, encoding="utf-8")
    _, documentos, _ = build_chunks(tmp_path)
    antes = fingerprint(documentos)

    arquivo.write_text("# A\n\n" + "conteúdo revisado " * 10, encoding="utf-8")
    _, documentos, _ = build_chunks(tmp_path)

    assert fingerprint(documentos) != antes
