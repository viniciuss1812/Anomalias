import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os
import io


class Gaussiana:

    def __init__(self, caminho):

       
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            data = json.load(arquivo)

        df = pd.DataFrame(data)

        df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        df = df.dropna(subset=['valor'])

       
        mu = df['valor'].mean()
        sigma = df['valor'].std()

        if sigma == 0:
            sigma = 1

       
        df['log_prob'] = -((df['valor'] - mu) ** 2) / (2 * sigma ** 2)

        df['score_fraude'] = (
            (df['log_prob'].max() - df['log_prob']) /
            (df['log_prob'].max() - df['log_prob'].min())
        )

        # 4. GRÁFICO EM MEMÓRIA (MELHORADO)
        X = np.arange(len(df))
        Y = df['valor'].to_numpy()

        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 6))

        # scatter mais limpo
        scatter = ax.scatter(
            X,
            Y,
            c=df['score_fraude'],
            cmap='coolwarm',
            s=50,
            edgecolors='white',
            linewidths=0.5,
            alpha=0.9
        )

        ax.axhline(mu, color='red', linestyle='--', linewidth=1.5, label='Média')

        ax.set_title('Detecção de Anomalias (Gaussiana)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Índice da Transação', fontsize=11)
        ax.set_ylabel('Valor', fontsize=11)

        ax.legend(loc='upper right')
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Score de Anomalia')

        sns.despine()

        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        plt.close(fig)

        self.image = buf