"""Falhas de origem independentes do canal e do provedor de dados."""


class RagSourceError(ValueError):
    """A origem configurada não pôde ser carregada como dados estruturados."""
