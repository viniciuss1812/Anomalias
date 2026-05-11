from fastapi import APIRouter
import os
import shutil
import ijson
import json
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import io
from collections import Counter
from models.Guassianasql import Gaussiana as GaussianaSQL
from models.dados import Transacao
from models.GeoDistancia import GeoDistancia
from models.GeoVelocidade import GeoVelocidade
from models.GeoIP import GeoIP
from models.ZScoresql import ZScoreSQL
import pyodbc
from fastapi import Query



def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.;"
        "DATABASE=banco;"
        "Trusted_Connection=yes;"
    )

router = APIRouter()


@router.get("/transactions/")
def get_transacoes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT TOP 100 * FROM transacoes")
    colunas = [col[0] for col in cursor.description]

    dados = [dict(zip(colunas, row)) for row in cursor.fetchall()]

    conn.close()

    return {
        "mensagem": "Retornando as 100 primeiras transações do banco",
        "transacoes": dados
    }

@router.get("/transactions/{conta}")
def get_transacao_id(conta: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transacoes WHERE conta = ?", (conta,))
    row = cursor.fetchone()

    conn.close()

    if row:
        colunas = [col[0] for col in cursor.description]
        return dict(zip(colunas, row))

    return {"erro": "Transação não encontrada"}

@router.get("/contas/")
def get_contas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT TOP 100 conta FROM transacoes")

    contas = [row[0] for row in cursor.fetchall()]

    conn.close()

    return {
        "mensagem": "Retornando as 100 primeiras contas",
        "contas": contas
    }

@router.post("/transactions/")
def inserir_transacao(transacao: Transacao):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO transacoes (
                id, valor, data, hora, dia_semana, categoria, conta,
                cidade, estado, pais, latitude, longitude,
                tipo_transacao, dispositivo, estabelecimento,
                tentativas, ip_origem, is_fraude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transacao.id,
            transacao.valor,
            transacao.data,
            transacao.hora,
            transacao.dia_semana,
            transacao.categoria,
            transacao.conta,
            transacao.cidade,
            transacao.estado,
            transacao.pais,
            transacao.latitude,
            transacao.longitude,
            transacao.tipo_transacao,
            transacao.dispositivo,
            transacao.estabelecimento,
            transacao.tentativas,
            transacao.ip_origem,
            int(transacao.is_fraude)  # 🔥 converte bool → bit
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return {"erro": str(e)}

    finally:
        conn.close()

    return {"msg": "Transação inserida com sucesso"}


@router.get("/querry/")
def querry(
    categoria: str = Query(None),
    cidade: str = Query(None),
    valor_min: float = Query(None),
    valor_max: float = Query(None),
    tipo_transacao: str = Query(None),
    dispositivo: str = Query(None),
    data_inicio: str = Query(None),
    data_fim: str = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔥 base da query
    query = "SELECT * FROM transacoes WHERE 1=1"
    params = []

    # 🔥 filtros dinâmicos
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)

    if cidade:
        query += " AND cidade = ?"
        params.append(cidade)

    if valor_min is not None:
        query += " AND valor >= ?"
        params.append(valor_min)

    if valor_max is not None:
        query += " AND valor <= ?"
        params.append(valor_max)

    if tipo_transacao:
        query += " AND tipo_transacao = ?"
        params.append(tipo_transacao)

    if dispositivo:
        query += " AND dispositivo = ?"
        params.append(dispositivo)

    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)

    cursor.execute(query, params)

    colunas = [col[0] for col in cursor.description]
    dados = [dict(zip(colunas, row)) for row in cursor.fetchall()]

    conn.close()

    return {
        "total": len(dados),
        "dados": dados
    }

@router.get("/calculogaussiana/")
def gaussiana():
    conn = get_connection()

    model = GaussianaSQL(conn)

    conn.close()

    return StreamingResponse(model.image, media_type="image/png")

@router.get("/calculogaussiana/{conta}")
def gaussiana(conta : str):
    conn = get_connection()

    model = GaussianaSQL(conn)

    conn.close()

    return StreamingResponse(model.image, media_type="image/png")


@router.get("/calculozscore/")
def zscore():
    conn = get_connection()

    model = ZScoreSQL(conn)

    conn.close()

    return StreamingResponse(model.image, media_type="image/png")


@router.get("/calculozscore/{conta}")
def zscore(conta: str):

    conn = get_connection()

    model = ZScoreSQL(conn, conta)

    conn.close()

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )


@router.get("/cidadesmaisanomalas/")
def cidadesmaisanomalas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 10 cidade, COUNT(*) as total
        FROM transacoes
        WHERE is_fraude = 1
        GROUP BY cidade
        ORDER BY total DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    cidades = [row[0] for row in dados]
    valores = [row[1] for row in dados]

    plt.figure(figsize=(10, 5))
    plt.bar(cidades, valores)
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@router.get("/numerodefraudes/")
def numerodefraudes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_fraude, COUNT(*) 
        FROM transacoes
        GROUP BY is_fraude
    """)

    dados = dict(cursor.fetchall())
    conn.close()

    fraudes = dados.get(1, 0)
    nao_fraudes = dados.get(0, 0)

    labels = ["Fraudes", "Não fraudes"]
    valores = [fraudes, nao_fraudes]

    plt.figure()
    plt.bar(labels, valores)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@router.get("/geo/distancia/{conta}")
def geo_distancia(conta: str):

    conn = get_connection()

    model = GeoDistancia(conn, conta)

    conn.close()

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )

@router.get("/geo/velocidade/{conta}")
def geo_velocidade(conta: str):

    conn = get_connection()

    model = GeoVelocidade(conn, conta)

    conn.close()

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )

@router.get("/geo/ip/{conta}")
def geo_ip(conta: str):

    conn = get_connection()

    model = GeoIP(conn, conta)

    conn.close()

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )


@router.get("/fraudes/tipos/")
def fraudes_tipos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 10 tipo_transacao, COUNT(*) as total
        FROM transacoes
        WHERE is_fraude = 1
        GROUP BY tipo_transacao
        ORDER BY total DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    tipos = [row[0] for row in dados]
    valores = [row[1] for row in dados]

    plt.figure(figsize=(10, 5))
    plt.bar(tipos, valores)
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@router.get("/horariofraudes/")
def fraudes_horarios():
    conn = get_connection()
    cursor = conn.cursor()

   
    cursor.execute("""
        SELECT 
            DATEPART(HOUR, hora) as hora,
            COUNT(*) as total
        FROM transacoes
        WHERE is_fraude = 1
        GROUP BY DATEPART(HOUR, hora)
        ORDER BY hora ASC 
    """)

    dados = cursor.fetchall()
    conn.close()

    if not dados:
        return {"msg": "Nenhuma fraude encontrada"}

    horas = [f"{row[0]:02d}:00" for row in dados]
    valores = [row[1] for row in dados]

    plt.figure(figsize=(12, 6))
    plt.bar(horas, valores)

    plt.title("Horários com Maior Número de Fraudes")
    plt.xlabel("Horários")
    plt.ylabel("Quantidade de Fraudes")

    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@router.get("/numerodetentativas/")
def maiores_tentativas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            tentativas,
            COUNT(*) as total
        FROM transacoes
        WHERE is_fraude = 1 AND tentativas >= 2
        GROUP BY tentativas
        ORDER BY tentativas ASC
    """)

    dados = cursor.fetchall()
    conn.close()

    if not dados:
        return {"msg": "Nenhuma fraude encontrada"}

    tentativas = [str(row[0]) for row in dados]
    valores = [row[1] for row in dados]

    plt.figure(figsize=(10, 5))
    plt.bar(tentativas, valores)

    plt.title("Fraudes por Número de Tentativas")
    plt.xlabel("Número de Tentativas")
    plt.ylabel("Quantidade de Fraudes")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

#def posicaogeografica():
