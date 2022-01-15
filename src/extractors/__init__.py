from typing import Any


class RespostaAPIInvalida(Exception):
    pass


def validar_resposta(response: dict[str, Any], campo: str = "data") -> Any:
    if not isinstance(response, dict):
        raise RespostaAPIInvalida(f"Resposta invalida: esperado dict, recebido {type(response).__name__}")

    if "error" in response:
        raise RespostaAPIInvalida(f"API retornou erro: {response['error']}")

    valor = response.get(campo)
    if valor is None:
        raise RespostaAPIInvalida(f"Campo '{campo}' ausente ou None na resposta da API")

    return valor
