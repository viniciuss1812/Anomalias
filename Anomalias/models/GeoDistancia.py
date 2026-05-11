import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

from math import radians, sin, cos, sqrt, atan2


class GeoDistancia:

    def __init__(self, conn, conta):

        query = """
            SELECT latitude, longitude
            FROM transacoes
            WHERE conta = ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=[conta]
        )

        df = df.dropna()

        if len(df) < 3:
            raise ValueError(
                "Poucas transações"
            )

        # Centro médio
        lat_media = df['latitude'].mean()
        lon_media = df['longitude'].mean()

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

        # Distância ao centro
        df['distancia'] = df.apply(
            lambda row: haversine(
                lat_media,
                lon_media,
                row['latitude'],
                row['longitude']
            ),
            axis=1
        )

        # Score
        df['score'] = (
            df['distancia']
            / df['distancia'].max()
        )

        fig, ax = plt.subplots(figsize=(12, 6))

        scatter = ax.scatter(
            range(len(df)),
            df['distancia'],
            c=df['score'],
            cmap='coolwarm'
        )

        ax.set_title(
            f'Distância Geográfica - Conta {conta}'
        )

        cbar = plt.colorbar(scatter)

        cbar.set_label('Score')

        buf = io.BytesIO()

        fig.savefig(
            buf,
            format='png',
            dpi=300
        )

        buf.seek(0)

        plt.close(fig)

        self.image = buf