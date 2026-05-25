from fastapi import APIRouter
from fastapi import Query

from Models.Transacao_model import Transacao

from Services.anomalias_services import (
    AnomaliasService
)
from Services.anomalias_estatistica_services import (
    AnomaliasEstatisticaService)

from Services.transacao_services import (
    TransacaoService
)

from Services.localizacao_service import (
    LocalizacaoService
)

from Services.gaussiana_service import (
    GaussianaService
)

from Services.zscore_service import (
    ZScoreService
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Transações"]
)

# =========================================================
# INSTÂNCIAS
# =========================================================

transacao_service = TransacaoService()

localizacao_service = LocalizacaoService()

anomalias_service = AnomaliasService()

estatistica_service = (AnomaliasEstatisticaService())
  
gaussiana_service = GaussianaService()

zscore_service = ZScoreService()


#criar o delete. update julgamento 

@router.get("/transacoes")
def listar_transacoes():

    return transacao_service.listar_transacoes()


@router.get("/transacoes/contas")
def listar_contas():

    return transacao_service.listar_contas()

#errado
@router.get("/transacoes/{conta}")
def buscar_transacao_por_conta(
    conta: str
):

    return transacao_service.buscar_transacao_por_conta(
        conta
    )


@router.post("/transacoes")
def criar_transacao(
    transacao: Transacao
):

    return transacao_service.criar_transacao(
        transacao
    )



@router.put("/transacoes/{id}/fraude")
def atualizar_status_fraude(
    id: int,
    is_fraude: bool
):

    return (
        transacao_service
        .atualizar_status_fraude(
            id,
            is_fraude
        )
    )


# =========================================================
# DELETAR TRANSAÇÃO
# =========================================================

@router.delete("/transacoes/{id}")
def deletar_transacao(
    id: int
):

    return (
        transacao_service
        .deletar_transacao(id)
    )


# =========================================================
# FILTROS
# =========================================================

@router.get("/transacoes/search")
def buscar_transacoes(

    categoria: str = Query(None),

    cidade: str = Query(None),

    valor_min: float = Query(None),

    valor_max: float = Query(None),

    tipo_transacao: str = Query(None),

    dispositivo: str = Query(None),

    data_inicio: str = Query(None),

    data_fim: str = Query(None)

):

    return transacao_service.buscar_transacoes(

        categoria=categoria,

        cidade=cidade,

        valor_min=valor_min,

        valor_max=valor_max,

        tipo_transacao=tipo_transacao,

        dispositivo=dispositivo,

        data_inicio=data_inicio,

        data_fim=data_fim
    )

#errado
@router.get("/zscore/{conta}")
def calcular_zscore(
    conta: str
):

    return (
        anomalias_service
        .zscore_por_conta(conta)
    )

#errado
@router.get("/gaussiana/{conta}")
def gaussiana(
    conta: str
):

    return (
        anomalias_service
        .gaussiana_por_conta(conta)
    )



    


@router.get("/distancia/{conta}")
def geo_distancia(
    conta: str
):

    return (
        localizacao_service
        .geo_distancia(conta)
    )

# =========================================================
# GEO IP
# =========================================================

@router.get("/ip/{conta}")
def geo_ip(
    conta: str
):

    return (
        localizacao_service
        .geo_ip(conta)
    )

# =========================================================
# GEO VELOCIDADE
# =========================================================

@router.get("/velocidade/{conta}")
def geo_velocidade(
    conta: str
):

    return (
        localizacao_service
        .geo_velocidade(conta)
    )



# =========================================================
# ESTATÍSTICAS
# =========================================================

@router.get("/analytics/fraud/cities")
def cidades_mais_anomalas():

    return (
        estatistica_service
        .cidades_mais_anomalas()
    )


@router.get("/analytics/fraud/count")
def numero_de_fraudes():

    return (
        estatistica_service
        .numero_de_fraudes()
    )


@router.get("/analytics/fraud/types")
def tipos_de_fraude():

    return (
        estatistica_service
        .fraudes_por_tipo()
    )


@router.get("/analytics/fraud/hours")
def horario_de_fraudes():

    return (
        estatistica_service
        .horario_fraudes()
    )


@router.get("/analytics/fraud/attempts")
def numero_de_tentativas():

    return (
        estatistica_service
        .numero_de_tentativas()
    )