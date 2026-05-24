# =========================================================
# services/anomalias_localizacao_service.py
# =========================================================

import io

import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2
)

from fastapi.responses import (
    StreamingResponse
)


class GeoServices:

    def __init__(self):

        sns.set_theme(
            style="whitegrid"
        )

    # =====================================================
    # HAVERSINE
    # =====================================================

    def haversine(
        self,
        lat1,
        lon1,
        lat2,
        lon2
    ):

        R = 6371

        dlat = radians(
            lat2 - lat1
        )

        dlon = radians(
            lon2 - lon1
        )

        a = (

            sin(dlat / 2) ** 2

            + cos(radians(lat1))

            * cos(radians(lat2))

            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        )

        return R * c

    # =====================================================
    # DISTÂNCIA
    # =====================================================

    def geo_distancia(
        self,
        df,
        conta: str
    ):

        df = df.dropna()

        if len(df) < 3:

            return {
                "erro": "Poucas transações"
            }

        lat_media = (
            df["latitude"]
            .mean()
        )

        lon_media = (
            df["longitude"]
            .mean()
        )

        df["distancia"] = df.apply(

            lambda row:

            self.haversine(
                lat_media,
                lon_media,
                row["latitude"],
                row["longitude"]
            ),

            axis=1
        )

        df["score"] = (

            df["distancia"]

            / df["distancia"].max()
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        scatter = ax.scatter(

            range(len(df)),

            df["distancia"],

            c=df["score"],

            cmap="coolwarm"
        )

        ax.set_title(
            f"Distância Geográfica - Conta {conta}"
        )

        cbar = plt.colorbar(
            scatter
        )

        cbar.set_label(
            "Score"
        )

        buf = io.BytesIO()

        fig.savefig(
            buf,
            format="png",
            dpi=300
        )

        buf.seek(0)

        plt.close(fig)

        return StreamingResponse(
            buf,
            media_type="image/png"
        )

    # =====================================================
    # GEO IP
    # =====================================================

    def geo_ip(
        self,
        df,
        conta: str
    ):

        df = df.dropna(
            subset=["ip_origem"]
        )

        if len(df) < 2:

            return {
                "erro": "Poucas transações"
            }

        df["rede"] = (

            df["ip_origem"]

            .astype(str)

            .str.split(".")

            .str[:2]

            .str.join(".")
        )

        freq = (

            df["rede"]

            .value_counts(
                normalize=True
            )
        )

        df["frequencia"] = (
            df["rede"]
            .map(freq)
        )

        df["score"] = (
            1 - df["frequencia"]
        )

        score_max = (
            df["score"]
            .max()
        )

        score_min = (
            df["score"]
            .min()
        )

        if score_max == score_min:

            df["score_normalizado"] = 0

        else:

            df["score_normalizado"] = (

                (
                    df["score"]
                    - score_min
                )

                /

                (
                    score_max
                    - score_min
                )
            )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        scatter = ax.scatter(

            range(len(df)),

            df["score_normalizado"],

            c=df["score_normalizado"],

            cmap="coolwarm"
        )

        ax.set_title(
            f"Anomalia de IP - Conta {conta}"
        )

        cbar = plt.colorbar(
            scatter,
            ax=ax
        )

        cbar.set_label(
            "Score de Anomalia"
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

    # =====================================================
    # GEO VELOCIDADE
    # =====================================================

    def geo_velocidade(
        self,
        df,
        conta: str
    ):

        df = df.dropna(
            subset=[
                "latitude",
                "longitude",
                "data",
                "hora"
            ]
        )

        if len(df) < 2:

            return {
                "erro": (
                    "A conta precisa ter pelo menos 2 transações"
                )
            }

        df["datetime"] = pd.to_datetime(

            df["data"].astype(str)

            + " "

            + df["hora"].astype(str),

            errors="coerce"
        )

        df["lat_ant"] = (
            df["latitude"]
            .shift(1)
        )

        df["lon_ant"] = (
            df["longitude"]
            .shift(1)
        )

        df["distancia_km"] = df.apply(

            lambda row:

            self.haversine(
                row["lat_ant"],
                row["lon_ant"],
                row["latitude"],
                row["longitude"]
            )

            if pd.notnull(
                row["lat_ant"]
            )

            else 0,

            axis=1
        )

        df["tempo_horas"] = (

            df["datetime"]

            .diff()

            .dt.total_seconds()

            / 3600
        )

        df["tempo_horas"] = (

            df["tempo_horas"]

            .replace(
                0,
                np.nan
            )
        )

        df["velocidade"] = (

            df["distancia_km"]

            / df["tempo_horas"]
        )

        df["velocidade"] = (

            df["velocidade"]

            .replace(
                [np.inf, -np.inf],
                np.nan
            )

            .fillna(0)
        )

        vel_max = (
            df["velocidade"]
            .max()
        )

        if vel_max == 0:

            df["score"] = 0

        else:

            df["score"] = (
                df["velocidade"]
                / vel_max
            )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        scatter = ax.scatter(

            range(len(df)),

            df["velocidade"],

            c=df["score"],

            cmap="coolwarm"
        )

        ax.axhline(
            900,
            linestyle="--"
        )

        ax.set_title(
            f"Velocidade Geográfica - Conta {conta}"
        )

        cbar = plt.colorbar(
            scatter,
            ax=ax
        )

        cbar.set_label(
            "Score de Anomalia"
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