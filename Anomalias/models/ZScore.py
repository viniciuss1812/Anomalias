import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import json
import io
from scipy.interpolate import make_interp_spline


class ZScore:

    def __init__(self, caminho):

        
        sns.set_theme(style="whitegrid")

      
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            data = json.load(arquivo)

        df = pd.DataFrame(data)

        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df = df.dropna(subset=['valor'])

        mu = df['valor'].mean()
        sigma = df['valor'].std()

        if sigma == 0:
            sigma = 1

       
        df['z_score'] = (df['valor'] - mu) / sigma

        df['score_fraude'] = np.abs(df['z_score'])
        df['score_fraude'] = df['score_fraude'] / df['score_fraude'].max()

        
        X = np.arange(len(df))
        Y = df['valor'].to_numpy()

        fig, ax = plt.subplots(figsize=(12, 6))

       
        if len(df) >= 4:
            X_smooth = np.linspace(X.min(), X.max(), 300)
            spline = make_interp_spline(X, Y, k=3)
            Y_smooth = spline(X_smooth)

            ax.fill_between(X_smooth, Y_smooth, alpha=0.15)
            ax.plot(X_smooth, Y_smooth, linewidth=2.2)
        else:
            ax.plot(X, Y, linewidth=2.2)

      
        scatter = ax.scatter(
            X,
            Y,
            c=df['score_fraude'],
            cmap='coolwarm',
            s=35,
            edgecolors='white',
            linewidths=0.4
        )

        
        #ax.axhline(mu, color='red', linestyle='--', linewidth=1.5, label='Média')

        #ax.axhline(mu + 2 * sigma, linestyle='--', linewidth=1, label='±2σ')
        #ax.axhline(mu - 2 * sigma, linestyle='--', linewidth=1)

        #ax.axhline(mu + 3 * sigma, linestyle=':', linewidth=1, label='±3σ')
       # ax.axhline(mu - 3 * sigma, linestyle=':', linewidth=1)

       
        ax.set_title('Detecção de Anomalias (Z-Score)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Índice da Transação')
        ax.set_ylabel('Valor')

        ax.legend()

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Score de Anomalia')

        sns.despine()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        plt.close(fig)

        self.image = buf