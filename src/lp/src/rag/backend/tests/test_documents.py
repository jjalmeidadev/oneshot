"""Catálogo e download das fontes."""

from __future__ import annotations


def test_pasta_vazia_devolve_lista_vazia(client, documents_dir):
    assert client.get("/api/documents").json()["documents"] == []


def test_arquivo_aparece_e_pode_ser_baixado(client, documents_dir):
    (documents_dir / "Cronograma — rev. ago.xlsx").write_bytes(b"conteudo")

    documento = client.get("/api/documents").json()["documents"][0]
    assert documento["name"] == "Cronograma — rev. ago.xlsx"
    assert documento["size_bytes"] == 8

    baixado = client.get(documento["download_url"])
    assert baixado.status_code == 200
    assert baixado.content == b"conteudo"


def test_identificador_desconhecido_e_404(client, documents_dir):
    assert client.get("/api/documents/naoexiste/download").status_code == 404


def test_caminho_relativo_nao_e_aceito_como_identificador(client, documents_dir):
    # O identificador é opaco: nenhum caminho chega ao sistema de arquivos.
    assert client.get("/api/documents/..%2F..%2Fmain.py/download").status_code == 404
