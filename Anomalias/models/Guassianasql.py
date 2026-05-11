import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

class Gaussiana:

    def __init__(self, conn):

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        import io

        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM transacoes")

        valores = [row[0] for row in cursor.fetchall()]

        df = pd.DataFrame(valores, columns=["valor"])

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

        X = np.arange(len(df))
        Y = df['valor'].to_numpy()

        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 6))

        scatter = ax.scatter(X, Y, c=df['score_fraude'], cmap='coolwarm')

        ax.axhline(mu, linestyle='--')

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Score')

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        plt.close(fig)

        self.image = buf