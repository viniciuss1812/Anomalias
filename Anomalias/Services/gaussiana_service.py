import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fastapi.responses import (
    StreamingResponse
)

class GaussianaService:

    # =====================================================
    # DISTRIBUIÇÃO GAUSSIANA
    # =====================================================

    def calcular_gaussiana(
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
        # LIMPEZA
        # ==============================================

        df["valor"] = pd.to_numeric(
            df["valor"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["valor"]
        )

        if df.empty:

            return {
                "erro": (
                    "Valores inválidos"
                )
            }

        # ==============================================
        # MÉDIA
        # ==============================================

        mu = (
            df["valor"]
            .mean()
        )

        # ==============================================
        # DESVIO PADRÃO
        # ==============================================

        sigma = (
            df["valor"]
            .std()
        )

        if sigma == 0:

            sigma = 1

        # ==============================================
        # LOG PROBABILIDADE
        # ==============================================

        df["log_prob"] = (

            -(
                (
                    df["valor"] - mu
                ) ** 2
            )

            / (2 * sigma ** 2)
        )

        # ==============================================
        # SCORE DE FRAUDE
        # ==============================================

        max_prob = (
            df["log_prob"]
            .max()
        )

        min_prob = (
            df["log_prob"]
            .min()
        )

        if max_prob == min_prob:

            df["score_fraude"] = 0

        else:

            df["score_fraude"] = (

                (
                    max_prob
                    - df["log_prob"]
                )

                /

                (
                    max_prob
                    - min_prob
                )
            )

        # ==============================================
        # GRÁFICO
        # ==============================================

        X = np.arange(len(df))

        Y = df["valor"].to_numpy()

        plt.style.use(
            "seaborn-v0_8-whitegrid"
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        scatter = ax.scatter(

            X,

            Y,

            c=df["score_fraude"],

            cmap="coolwarm"
        )

        ax.axhline(
            mu,
            linestyle="--"
        )

        ax.set_title(
            f"Distribuição Gaussiana - Conta {conta}"
        )

        ax.set_xlabel(
            "Transações"
        )

        ax.set_ylabel(
            "Valor"
        )

        cbar = plt.colorbar(
            scatter,
            ax=ax
        )

        cbar.set_label(
            "Score de Fraude"
        )

        buf = io.BytesIO()

        fig.savefig(
            buf,
            format="png",
            bbox_inches="tight",
            dpi=300
        )

        buf.seek(0)

        plt.close(fig)

        return StreamingResponse(
            buf,
            media_type="image/png"
        )