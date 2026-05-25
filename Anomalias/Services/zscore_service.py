import io

import numpy as np

import matplotlib.pyplot as plt

from fastapi.responses import (
    StreamingResponse
)


class ZScoreService:

    # =====================================================
    # CÁLCULO Z-SCORE
    # =====================================================

    def calcular_zscore(
        self,
        df,
        conta: str
    ):

        if df.empty:

            return {
                "erro": (
                    "Nenhuma transação encontrada"
                )
            }

        # ==============================================
        # MÉDIA
        # ==============================================

        media = (
            df["valor"]
            .mean()
        )

        # ==============================================
        # DESVIO PADRÃO
        # ==============================================

        desvio_padrao = (
            df["valor"]
            .std()
        )

        if desvio_padrao == 0:

            return {
                "erro": (
                    "Desvio padrão inválido"
                )
            }

        # ==============================================
        # Z-SCORE
        # ==============================================

        df["zscore"] = (

            (df["valor"] - media)

            / desvio_padrao
        )

        # ==============================================
        # SCORE ABSOLUTO
        # ==============================================

        df["score_anomalia"] = (
            np.abs(df["zscore"])
        )

        # ==============================================
        # ANOMALIA
        # ==============================================

        df["anomalia"] = (
            df["score_anomalia"] > 2
        )

        # ==============================================
        # GRÁFICO
        # ==============================================

        plt.figure(figsize=(12, 6))

        cores = df["anomalia"].map({
            True: "red",
            False: "blue"
        })

        plt.scatter(

            range(len(df)),

            df["valor"],

            c=cores
        )

        plt.title(
            f"Z-Score - Conta {conta}"
        )

        plt.xlabel(
            "Transações"
        )

        plt.ylabel(
            "Valor"
        )

        plt.grid(True)

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