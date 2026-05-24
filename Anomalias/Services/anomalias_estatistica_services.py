import io

import matplotlib.pyplot as plt

from fastapi.responses import StreamingResponse

from Repository.transacao_repository import (
    TransacaoRepository
)


class AnomaliasEstatisticaService:

    def __init__(self):

        self.repository = (
            TransacaoRepository()
        )

    # =====================================================
    # CIDADES MAIS ANÔMALAS
    # =====================================================

    def cidades_mais_anomalas(self):

        dados = (
            self.repository
            .buscar_cidades_mais_anomalas()
        )

        cidades = [
            row[0]
            for row in dados
        ]

        valores = [
            row[1]
            for row in dados
        ]

        plt.figure(figsize=(10, 5))

        plt.bar(
            cidades,
            valores
        )

        plt.xticks(rotation=45)

        plt.title(
            "Cidades com Mais Fraudes"
        )

        plt.xlabel("Cidade")

        plt.ylabel(
            "Quantidade de Fraudes"
        )

        buf = io.BytesIO()

        plt.savefig(
            buf,
            format="png",
            bbox_inches="tight"
        )

        buf.seek(0)

        plt.close()

        return StreamingResponse(
            buf,
            media_type="image/png"
        )

    # =====================================================
    # NÚMERO DE FRAUDES
    # =====================================================

    def numero_de_fraudes(self):

        dados = (
            self.repository
            .buscar_numero_de_fraudes()
        )

        fraudes = dados.get(1, 0)

        nao_fraudes = dados.get(0, 0)

        labels = [
            "Fraudes",
            "Não fraudes"
        ]

        valores = [
            fraudes,
            nao_fraudes
        ]

        plt.figure(figsize=(8, 5))

        plt.bar(
            labels,
            valores
        )

        plt.title(
            "Número de Fraudes"
        )

        plt.ylabel(
            "Quantidade"
        )

        buf = io.BytesIO()

        plt.savefig(
            buf,
            format="png"
        )

        buf.seek(0)

        plt.close()

        return StreamingResponse(
            buf,
            media_type="image/png"
        )

    # =====================================================
    # FRAUDES POR TIPO
    # =====================================================

    def fraudes_por_tipo(self):

        dados = (
            self.repository
            .buscar_fraudes_por_tipo()
        )

        tipos = [
            row[0]
            for row in dados
        ]

        valores = [
            row[1]
            for row in dados
        ]

        plt.figure(figsize=(10, 5))

        plt.bar(
            tipos,
            valores
        )

        plt.xticks(rotation=45)

        plt.title(
            "Fraudes por Tipo de Transação"
        )

        plt.xlabel(
            "Tipo de Transação"
        )

        plt.ylabel(
            "Quantidade"
        )

        buf = io.BytesIO()

        plt.savefig(
            buf,
            format="png",
            bbox_inches="tight"
        )

        buf.seek(0)

        plt.close()

        return StreamingResponse(
            buf,
            media_type="image/png"
        )

    # =====================================================
    # HORÁRIO DAS FRAUDES
    # =====================================================

    def horario_fraudes(self):

        dados = (
            self.repository
            .buscar_horario_fraudes()
        )

        if not dados:

            return {
                "msg": "Nenhuma fraude encontrada"
            }

        horas = [
            f"{row[0]:02d}:00"
            for row in dados
        ]

        valores = [
            row[1]
            for row in dados
        ]

        plt.figure(figsize=(12, 6))

        plt.bar(
            horas,
            valores
        )

        plt.title(
            "Horários com Maior Número de Fraudes"
        )

        plt.xlabel(
            "Horários"
        )

        plt.ylabel(
            "Quantidade de Fraudes"
        )

        plt.xticks(rotation=45)

        plt.grid(
            axis="y",
            linestyle="--",
            alpha=0.5
        )

        buf = io.BytesIO()

        plt.savefig(
            buf,
            format="png",
            bbox_inches="tight",
            dpi=300
        )

        buf.seek(0)

        plt.close()

        return StreamingResponse(
            buf,
            media_type="image/png"
        )

    # =====================================================
    # NÚMERO DE TENTATIVAS
    # =====================================================

    def numero_de_tentativas(self):

        dados = (
            self.repository
            .buscar_numero_de_tentativas()
        )

        if not dados:

            return {
                "msg": "Nenhuma fraude encontrada"
            }

        tentativas = [
            str(row[0])
            for row in dados
        ]

        valores = [
            row[1]
            for row in dados
        ]

        plt.figure(figsize=(10, 5))

        plt.bar(
            tentativas,
            valores
        )

        plt.title(
            "Fraudes por Número de Tentativas"
        )

        plt.xlabel(
            "Número de Tentativas"
        )

        plt.ylabel(
            "Quantidade de Fraudes"
        )

        plt.grid(
            axis="y",
            linestyle="--",
            alpha=0.5
        )

        buf = io.BytesIO()

        plt.savefig(
            buf,
            format="png",
            bbox_inches="tight",
            dpi=300
        )

        buf.seek(0)

        plt.close()

        return StreamingResponse(
            buf,
            media_type="image/png"
        )