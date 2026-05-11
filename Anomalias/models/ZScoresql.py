import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import io
from scipy.interpolate import make_interp_spline


class ZScoreSQL:

    def __init__(self, conn, conta):

        sns.set_theme(style="whitegrid")

        # ==========================================
        # BUSCA SOMENTE A CONTA INFORMADA
        # ==========================================

        query = f"""
            SELECT *
            FROM transacoes
            WHERE conta = '{conta}'
        """

        df = pd.read_sql(query, conn)

        # ==========================================
        # TRATAMENTO DOS DADOS
        # ==========================================

        df['valor'] = pd.to_numeric(
            df['valor'],
            errors='coerce'
        )

        df = df.dropna(subset=['valor'])

        # Se não houver dados
        if len(df) == 0:
            raise ValueError(
                f"Nenhuma transação encontrada para a conta {conta}"
            )

        # ==========================================
        # CÁLCULO ESTATÍSTICO
        # ==========================================

        # Média da conta
        media = df['valor'].mean()

        # Desvio padrão da conta
        desvio = df['valor'].std()

        # Evita divisão por zero
        if desvio == 0 or np.isnan(desvio):
            desvio = 1

        # ==========================================
        # Z-SCORE
        # ==========================================

        df['z_score'] = (
            (df['valor'] - media)
            / desvio
        )

        # ==========================================
        # SCORE DE FRAUDE
        # ==========================================

        df['score_fraude'] = np.abs(
            df['z_score']
        )

        max_score = df['score_fraude'].max()

        if max_score != 0:
            df['score_fraude'] = (
                df['score_fraude']
                / max_score
            )

        # ==========================================
        # CLASSIFICAÇÃO DE ANOMALIA
        # ==========================================

        df['anomalia'] = (
            np.abs(df['z_score']) > 3
        )

        # ==========================================
        # GRÁFICO
        # ==========================================

        X = np.arange(len(df))
        Y = df['valor'].to_numpy()

        fig, ax = plt.subplots(figsize=(12, 6))

        # Linha suavizada
        if len(df) >= 4:

            X_smooth = np.linspace(
                X.min(),
                X.max(),
                300
            )

            spline = make_interp_spline(
                X,
                Y,
                k=3
            )

            Y_smooth = spline(X_smooth)

            ax.plot(
                X_smooth,
                Y_smooth,
                linewidth=2.2
            )

        else:

            ax.plot(
                X,
                Y,
                linewidth=2.2
            )

        # Pontos
        scatter = ax.scatter(
            X,
            Y,
            c=df['score_fraude'],
            cmap='coolwarm',
            s=35,
            edgecolors='white',
            linewidths=0.4
        )

        # ==========================================
        # INFORMAÇÕES DO GRÁFICO
        # ==========================================

        ax.set_title(
            f'Detecção de Anomalias - Conta {conta}',
            fontsize=14,
            fontweight='bold'
        )

        ax.set_xlabel(
            'Índice da Transação'
        )

        ax.set_ylabel(
            'Valor'
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
        # EXPORTAÇÃO DA IMAGEM
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