import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io


class GeoIP:

    def __init__(self, conn, conta):

        sns.set_theme(style="whitegrid")

        # ==========================================
        # QUERY
        # ==========================================

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

        # ==========================================
        # LIMPEZA
        # ==========================================

        df = df.dropna(subset=['ip_origem'])

        if len(df) < 2:
            raise ValueError(
                "Poucas transações"
            )

        # ==========================================
        # EXTRAÇÃO DA REDE
        # ==========================================

        df['rede'] = (
            df['ip_origem']
            .astype(str)
            .str.split('.')
            .str[:2]
            .str.join('.')
        )

        # ==========================================
        # FREQUÊNCIA DAS REDES
        # ==========================================

        freq = (
            df['rede']
            .value_counts(normalize=True)
        )

        # ==========================================
        # SCORE DE RARIDADE
        # ==========================================

        df['frequencia'] = (
            df['rede']
            .map(freq)
        )

        df['score'] = (
            1 - df['frequencia']
        )

        # ==========================================
        # NORMALIZAÇÃO
        # ==========================================

        score_max = df['score'].max()

        score_min = df['score'].min()

        if score_max == score_min:

            df['score_normalizado'] = 0

        else:

            df['score_normalizado'] = (
                (df['score'] - score_min)
                / (score_max - score_min)
            )

        # ==========================================
        # ANOMALIA
        # ==========================================

        df['anomalia'] = (
            df['score_normalizado'] > 0.8
        )

        # ==========================================
        # GRÁFICO
        # ==========================================

        fig, ax = plt.subplots(figsize=(12, 6))

        scatter = ax.scatter(
            range(len(df)),
            df['score_normalizado'],
            c=df['score_normalizado'],
            cmap='coolwarm',
            s=60,
            edgecolors='white',
            linewidths=0.5
        )

        ax.set_title(
            f'Anomalia de IP - Conta {conta}',
            fontsize=14,
            fontweight='bold'
        )

        ax.set_xlabel(
            'Transações'
        )

        ax.set_ylabel(
            'Raridade da Rede'
        )

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