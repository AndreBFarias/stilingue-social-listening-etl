from src.transformers.transformers import (
    calcular_percentuais_sentimento,
    calcular_saude_marca,
    mapear_sentimento,
    normalizar_registros,
)


def test_calcular_percentuais_sentimento():
    resultado = calcular_percentuais_sentimento(
        positivo=3275, neutro=2100, negativo=4500, total=9875
    )
    assert resultado["pct_positivo"] == 33.16
    assert resultado["pct_neutro"] == 21.27
    assert resultado["pct_negativo"] == 45.57


def test_calcular_percentuais_sentimento_total_zero():
    resultado = calcular_percentuais_sentimento(
        positivo=0, neutro=0, negativo=0, total=0
    )
    assert resultado["pct_positivo"] == 0.0
    assert resultado["pct_neutro"] == 0.0
    assert resultado["pct_negativo"] == 0.0


def test_calcular_saude_marca():
    score = calcular_saude_marca(positivo=3275, negativo=4500, total=9875)
    assert score == -12.41


def test_calcular_saude_marca_total_zero():
    score = calcular_saude_marca(positivo=0, negativo=0, total=0)
    assert score == 0.0


def test_calcular_saude_marca_positiva():
    score = calcular_saude_marca(positivo=2100, negativo=800, total=5000)
    assert score == 26.0


def test_mapear_sentimento_positivo():
    assert mapear_sentimento(1) == "Positivo"


def test_mapear_sentimento_negativo():
    assert mapear_sentimento(-1) == "Negativo"


def test_mapear_sentimento_neutro():
    assert mapear_sentimento(0) == "Neutro"


def test_mapear_sentimento_desconhecido():
    assert mapear_sentimento(99) == "Neutro"


def test_normalizar_registros_vazio():
    df = normalizar_registros([])
    assert df.empty


def test_normalizar_registros_com_dados():
    registros = [
        {"nome": "test_user", "valor": 10, "texto": None},
        {"nome": "user_1", "valor": None, "texto": "teste"},
    ]
    df = normalizar_registros(registros)
    assert len(df) == 2
    assert df.iloc[0]["texto"] == ""
    assert df.iloc[1]["valor"] == 0


def test_mapear_sentimento_none():
    assert mapear_sentimento(None) == "Neutro"


def test_calcular_percentuais_valores_extremos():
    resultado = calcular_percentuais_sentimento(
        positivo=1_000_000, neutro=0, negativo=0, total=1_000_000
    )
    assert resultado["pct_positivo"] == 100.0
    assert resultado["pct_neutro"] == 0.0
    assert resultado["pct_negativo"] == 0.0


def test_calcular_saude_marca_extremo_negativo():
    score = calcular_saude_marca(positivo=0, negativo=10000, total=10000)
    assert score == -100.0


def test_normalizar_registros_colunas_heterogeneas():
    registros = [
        {"a": 1, "b": "x"},
        {"a": 2, "c": "y"},
    ]
    df = normalizar_registros(registros)
    assert len(df) == 2
    assert df.iloc[0]["b"] == "x"
    assert df.iloc[1]["b"] == ""
    assert df.iloc[0]["c"] == ""
    assert df.iloc[1]["c"] == "y"
