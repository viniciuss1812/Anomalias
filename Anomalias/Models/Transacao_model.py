from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class Transacao(BaseModel):
    id: int
    valor: float
    data: date
    hora: time
    dia_semana: str
    categoria: str
    conta: str
    cidade: str
    estado: str
    pais: str
    latitude: float
    longitude: float
    tipo_transacao: str
    dispositivo: str
    estabelecimento: str
    tentativas: int
    ip_origem: str
    is_fraude: bool