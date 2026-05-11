import json
import pyodbc
from datetime import datetime

# conexão usando Windows Authentication
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.;"
    "DATABASE=banco;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

with open("transacoes_treino.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

for t in dados:
    try:
        hora_convertida = datetime.strptime(t["hora"], "%H:%M").time()

        cursor.execute("""
            INSERT INTO transacoes (
                id, valor, data, hora, dia_semana, categoria, conta,
                cidade, estado, pais, latitude, longitude,
                tipo_transacao, dispositivo, estabelecimento,
                tentativas, ip_origem, is_fraude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t["id"],
            t["valor"],
            t["data"],
            hora_convertida,
            t["dia_semana"],
            t["categoria"],
            t["conta"],
            t["cidade"],
            t["estado"],
            t["pais"],
            t["latitude"],
            t["longitude"],
            t["tipo_transacao"],
            t["dispositivo"],
            t["estabelecimento"],
            t["tentativas"],
            t["ip_origem"],
            int(t["is_fraude"])
        ))

    except Exception as e:
        print(f"Erro ao inserir ID {t.get('id')}: {e}")

conn.commit()
cursor.close()
conn.close()

print("✅ Inserção concluída!")