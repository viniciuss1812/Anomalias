import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

from math import radians, sin, cos, sqrt, atan2


class GeoVelocidade:

    def __init__(self, conn, conta):

        sns.set_theme(style="whitegrid")

        # ==========================================
        # QUERY
        # ==========================================

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

        # ==========================================
        # LIMPEZA
        # ==========================================

        df = df.dropna(
            subset=[
                'latitude',
                'longitude',
                'data',
                'hora'
            ]
        )

        if len(df) < 2:
            raise ValueError(
                "A conta precisa ter pelo menos 2 transações"
            )

        # ==========================================
        # DATETIME
        # ==========================================

        df['datetime'] = pd.to_datetime(
            df['data'].astype(str)
            + ' '
            + df['hora'].astype(str),
            errors='coerce'
        )

        df = df.dropna(subset=['datetime'])

        # ==========================================
        # FUNÇÃO HAVERSINE
        # ==========================================

        def haversine(lat1, lon1, lat2, lon2):

            R = 6371

            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)

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

        # ==========================================
        # LOCALIZAÇÃO ANTERIOR
        # ==========================================

        df['lat_ant'] = df['latitude'].shift(1)
        df['lon_ant'] = df['longitude'].shift(1)

        # ==========================================
        # DISTÂNCIA ENTRE TRANSAÇÕES
        # ==========================================

        df['distancia_km'] = df.apply(

            lambda row:

            haversine(
                row['lat_ant'],
                row['lon_ant'],
                row['latitude'],
                row['longitude']
            )

            if pd.notnull(row['lat_ant'])
            else 0,

            axis=1
        )

        # ==========================================
        # TEMPO ENTRE TRANSAÇÕES
        # ==========================================

        df['tempo_horas'] = (
            df['datetime']
            .diff()
            .dt.total_seconds()
            / 3600
        )

        # Evita divisão por zero
        df['tempo_horas'] = (
            df['tempo_horas']
            .replace(0, np.nan)
        )

        # ==========================================
        # VELOCIDADE
        # ==========================================

        df['velocidade'] = (
            df['distancia_km']
            / df['tempo_horas']
        )

        df['velocidade'] = (
            df['velocidade']
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0)
        )

        # ==========================================
        # SCORE NORMALIZADO
        # ==========================================

        vel_max = df['velocidade'].max()

        if vel_max == 0:

            df['score'] = 0

        else:

            df['score'] = (
                df['velocidade']
                / vel_max
            )

        # ==========================================
        # ANOMALIA
        # ==========================================

        df['anomalia'] = (
            df['velocidade'] > 900
        )

        # ==========================================
        # GRÁFICO
        # ==========================================

        fig, ax = plt.subplots(figsize=(12, 6))

        scatter = ax.scatter(
            range(len(df)),
            df['velocidade'],
            c=df['score'],
            cmap='coolwarm',
            s=60,
            edgecolors='white',
            linewidths=0.5
        )

        ax.set_title(
            f'Velocidade Geográfica - Conta {conta}',
            fontsize=14,
            fontweight='bold'
        )

        ax.set_xlabel(
            'Transações'
        )

        ax.set_ylabel(
            'Velocidade (km/h)'
        )

        ax.axhline(
            900,
            linestyle='--',
            linewidth=1.5,
            label='Limite suspeito'
        )

        ax.legend()

        cbar = plt.colorbar(
            scatter,
            ax=ax
        )

        cbar.set_label(
            'Score de Anomalia'
        )

        sns.despine()

        # ==========================================
        # EXPORTAÇÃO
        # ==========================================

        buf = io.BytesIO()

        fig.savefig(
            buf,
            format='png',
            bbox_inches='tight',
            dpi=300
        )

        buf.seek(0)

        plt.close(fig)

        self.image = buf