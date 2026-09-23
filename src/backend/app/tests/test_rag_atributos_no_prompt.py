"""Regressao do DEF-RNF04-01: atributos estruturados precisam chegar ao prompt.

Defeito encontrado na execucao do RNF04. O recuperador devolvia o
extrato correto, mas `build_rag_input` montava o bloco `[Fonte N]` apenas com
titulo, lista, data de atualizacao e `content_text`. Vigencia, status, linha e
categoria vivem em `source_extracts.metadata` e eram descartados antes do
prompt.

Efeito observado: perguntado sobre o periodo da operacao assistida na Linha
1-Azul, o agente recuperou o comunicado certo e respondeu que o contexto nao era
suficiente para informar as datas — que estavam no registro recuperado.

Estes testes existem para que a correcao nao regrida silenciosamente.
"""

from app.rag.sharepoint import (
    RetrievedDocument,
    SharePointDocument,
    attributes_from_fields,
    attributes_from_metadata,
    build_rag_input,
)


def _documento(**sobrescritas) -> SharePointDocument:
    base = {
        "source_id": "comunicados-servico:201",
        "title": "Operacao assistida na Linha Azul",
        "list_name": "Comunicados de Servico",
        "content": "Durante o periodo ficticio, o intervalo entre trens podera ser ampliado.",
        "web_url": "https://mock.sharepoint.local/Lists/Comunicados/201",
        "last_modified": "2026-08-01 12:00:00+00:00",
        "search_text": "linha azul intervalo trens",
    }
    base.update(sobrescritas)
    return SharePointDocument(**base)


class TestExtracaoDeAtributos:
    def test_metadata_do_banco_vira_vigencia_legivel(self):
        atributos = attributes_from_metadata(
            {
                "validity": {"start": "2026-08-24", "end": "2026-08-28"},
                "status": "Programado",
                "line": "Linha 1-Azul",
                "category": "Operacao",
            }
        )

        assert ("Vigencia", "de 2026-08-24 a 2026-08-28") in atributos
        assert ("Status", "Programado") in atributos
        assert ("Linha", "Linha 1-Azul") in atributos
        assert ("Categoria", "Operacao") in atributos

    def test_vigencia_vazia_nao_gera_atributo(self):
        """Extratos sem validade nao devem poluir o prompt com rotulo vazio."""

        atributos = attributes_from_metadata({"validity": {}, "status": "Vigente"})

        assert not any(rotulo == "Vigencia" for rotulo, _ in atributos)
        assert ("Status", "Vigente") in atributos

    def test_apenas_uma_das_datas_produz_intervalo_aberto(self):
        assert attributes_from_metadata({"validity": {"start": "2026-08-24"}}) == (
            ("Vigencia", "a partir de 2026-08-24"),
        )
        assert attributes_from_metadata({"validity": {"end": "2026-09-05"}}) == (
            ("Vigencia", "ate 2026-09-05"),
        )

    def test_metadata_ausente_ou_invalido_nao_quebra(self):
        assert attributes_from_metadata(None) == ()
        assert attributes_from_metadata({}) == ()
        assert attributes_from_metadata("texto") == ()

    def test_campos_do_json_local_viram_atributos(self):
        atributos = attributes_from_fields(
            {
                "Title": "Acesso alternativo na Estacao Republica",
                "Conteudo": "Um dos acessos estara fechado.",
                "PalavrasChave": "republica acesso",
                "Tipo": "Acessibilidade",
                "Linha": "Linhas 3-Vermelha e 4-Amarela",
                "ValidadeInicio": "2026-08-20",
                "ValidadeFim": "2026-09-05",
                "Status": "Programado",
            }
        )

        assert ("Vigencia", "de 2026-08-20 a 2026-09-05") in atributos
        assert ("Status", "Programado") in atributos
        assert ("Linha", "Linhas 3-Vermelha e 4-Amarela") in atributos

    def test_campos_ja_renderizados_nao_se_repetem_como_atributo(self):
        """Titulo, conteudo e palavras-chave ja tem lugar proprio no bloco."""

        rotulos = {
            rotulo
            for rotulo, _ in attributes_from_fields(
                {
                    "Title": "Titulo",
                    "Conteudo": "Corpo",
                    "PalavrasChave": "a b c",
                    "Status": "Vigente",
                }
            )
        }

        assert rotulos == {"Status"}


class TestPromptCarregaOsAtributos:
    def test_vigencia_chega_ao_bloco_da_fonte(self):
        """O caso exato que falhou no RNF04-P-07."""

        documento = _documento(
            attributes=(
                ("Vigencia", "de 2026-08-24 a 2026-08-28"),
                ("Status", "Programado"),
                ("Linha", "Linha 1-Azul"),
            )
        )

        prompt = build_rag_input(
            "Qual e o periodo da operacao assistida na Linha 1-Azul?",
            [RetrievedDocument(document=documento, score=4.0)],
        )

        assert "Vigencia: de 2026-08-24 a 2026-08-28" in prompt
        assert "Status: Programado" in prompt
        assert "Linha: Linha 1-Azul" in prompt

    def test_atributos_ficam_dentro_do_bloco_da_propria_fonte(self):
        """Atributo fora do bloco certo faria o modelo atribuir dado a fonte errada."""

        primeiro = _documento(
            source_id="a:1", title="Comunicado A", attributes=(("Status", "Programado"),)
        )
        segundo = _documento(
            source_id="b:2", title="Comunicado B", attributes=(("Status", "Encerrado"),)
        )

        prompt = build_rag_input(
            "status dos comunicados",
            [
                RetrievedDocument(document=primeiro, score=3.0),
                RetrievedDocument(document=segundo, score=2.0),
            ],
        )

        bloco_1 = prompt.index("[Fonte 1]")
        bloco_2 = prompt.index("[Fonte 2]")
        assert bloco_1 < prompt.index("Status: Programado") < bloco_2
        assert bloco_2 < prompt.index("Status: Encerrado")

    def test_conteudo_continua_presente_e_depois_dos_atributos(self):
        documento = _documento(attributes=(("Status", "Vigente"),))

        prompt = build_rag_input(
            "qual o procedimento",
            [RetrievedDocument(document=documento, score=1.0)],
        )

        assert "Conteudo:" in prompt
        assert prompt.index("Status: Vigente") < prompt.index("Conteudo:")

    def test_documento_sem_atributos_mantem_o_bloco_anterior(self):
        """Extratos sem metadata nao podem ganhar linha em branco no prompt."""

        prompt = build_rag_input(
            "qual o procedimento",
            [RetrievedDocument(document=_documento(), score=1.0)],
        )

        assert "[Fonte 1] Operacao assistida na Linha Azul" in prompt
        assert "\n\nConteudo:" not in prompt
