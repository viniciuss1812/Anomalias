import io
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse

from Core.conexao import get_connection
import pandas as pd


class TransacaoRepository:

   
    def get_transacoes(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT TOP 100 * FROM transacoes")

        colunas = [col[0] for col in cursor.description]

        dados = [
            dict(zip(colunas, row))
            for row in cursor.fetchall()
        ]

        conn.close()

        return {
            "mensagem": "Retornando as 100 primeiras transações do banco",
            "transacoes": dados
        }

    def get_transacao_por_conta(self, conta: str):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM transacoes WHERE conta = ?",
            (conta,)
        )

        row = cursor.fetchone()

        if row:
            colunas = [col[0] for col in cursor.description]

            resultado = dict(zip(colunas, row))

            conn.close()

            return resultado

        conn.close()

        return {"erro": "Transação não encontrada"}

    def get_contas(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT TOP 100 conta FROM transacoes"
        )

        contas = [row[0] for row in cursor.fetchall()]

        conn.close()

        return {
            "mensagem": "Retornando as 100 primeiras contas",
            "contas": contas
        }

    def inserir_transacao(self, transacao):

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO transacoes (
                    id,
                    valor,
                    data,
                    hora,
                    dia_semana,
                    categoria,
                    conta,
                    cidade,
                    estado,
                    pais,
                    latitude,
                    longitude,
                    tipo_transacao,
                    dispositivo,
                    estabelecimento,
                    tentativas,
                    ip_origem,
                    is_fraude
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
                int(transacao.is_fraude)
            ))

            conn.commit()

            return {
                "msg": "Transação inserida com sucesso"
            }

        except Exception as e:

            conn.rollback()

            return {
                "erro": str(e)
            }

        finally:
            conn.close()

    # =========================================================
    # QUERY DINÂMICA
    # =========================================================

    def query_transacoes(
        self,
        categoria=None,
        cidade=None,
        valor_min=None,
        valor_max=None,
        tipo_transacao=None,
        dispositivo=None,
        data_inicio=None,
        data_fim=None
    ):

        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM transacoes WHERE 1=1"

        params = []

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

        dados = [
            dict(zip(colunas, row))
            for row in cursor.fetchall()
        ]

        conn.close()

        return {
            "total": len(dados),
            "dados": dados
        }
    


    def buscar_valores_por_conta(
        self,
        conta: str
    ):

        conn = get_connection()

        query = """
            SELECT
                valor,
                data,
                hora
            FROM transacoes
            WHERE conta = ?
            ORDER BY data, hora
        """

        df = pd.read_sql(
            query,
            conn,
            params=[conta]
        )

        conn.close()

        return df



    def buscar_localizacao_por_conta(
        self,
        conta: str
    ):

        conn = get_connection()

        query = """
            SELECT
                latitude,
                longitude
            FROM transacoes
            WHERE conta = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=[conta]
        )

        conn.close()

        return df



    # =====================================================
    # GEO IP
    # =====================================================

    def buscar_ips_por_conta(
        self,
        conta: str
    ):

        conn = get_connection()

        query = """
            SELECT ip_origem
            FROM transacoes
            WHERE conta = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=[conta]
        )

        conn.close()

        return df

    # =====================================================
    # GEO VELOCIDADE
    # =====================================================

    def buscar_velocidade_geografica(
        self,
        conta: str
    ):

        conn = get_connection()

        query = """
            SELECT
                data,
                hora,
                latitude,
                longitude
            FROM transacoes
            WHERE conta = ?
            ORDER BY data, hora
        """

        df = pd.read_sql(
            query,
            conn,
            params=[conta]
        )

        conn.close()

        return df

    # =====================================================
    # ESTATÍSTICAS
    # =====================================================

    def buscar_cidades_mais_anomalas(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT TOP 10
                cidade,
                COUNT(*) as total
            FROM transacoes
            WHERE is_fraude = 1
            GROUP BY cidade
            ORDER BY total DESC
        """)

        dados = cursor.fetchall()

        conn.close()

        return dados

    def buscar_numero_de_fraudes(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                is_fraude,
                COUNT(*)
            FROM transacoes
            GROUP BY is_fraude
        """)

        dados = dict(
            cursor.fetchall()
        )

        conn.close()

        return dados

    def buscar_fraudes_por_tipo(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT TOP 10
                tipo_transacao,
                COUNT(*) as total
            FROM transacoes
            WHERE is_fraude = 1
            GROUP BY tipo_transacao
            ORDER BY total DESC
        """)

        dados = cursor.fetchall()

        conn.close()

        return dados

    def buscar_horario_fraudes(self):

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

        return dados

    def buscar_numero_de_tentativas(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                tentativas,
                COUNT(*) as total
            FROM transacoes
            WHERE is_fraude = 1
            AND tentativas >= 2
            GROUP BY tentativas
            ORDER BY tentativas ASC
        """)

        dados = cursor.fetchall()

        conn.close()

        return dados















































































  