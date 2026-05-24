from Repository.transacao_repository import (
    TransacaoRepository
)

from Services.anomalias_estatistica_services import (
    AnomaliasEstatisticaService
)

class EstatisticaService:

    def __init__(self):

        self.repository = (
            TransacaoRepository()
        )

        self.anomalias_service = (
            AnomaliasEstatisticaService()
        )

    # =====================================================
    # CIDADES MAIS ANÔMALAS
    # =====================================================

    def cidades_mais_anomalas(self):

        dados = (

            self.repository
            .buscar_cidades_mais_anomalas()
        )

        return (

            self.anomalias_service
            .cidades_mais_anomalas(
                dados
            )
        )

    # =====================================================
    # NÚMERO DE FRAUDES
    # =====================================================

    def numero_de_fraudes(self):

        dados = (

            self.repository
            .buscar_numero_de_fraudes()
        )

        return (

            self.anomalias_service
            .numero_de_fraudes(
                dados
            )
        )

    # =====================================================
    # FRAUDES POR TIPO
    # =====================================================

    def fraudes_por_tipo(self):

        dados = (

            self.repository
            .buscar_fraudes_por_tipo()
        )

        return (

            self.anomalias_service
            .fraudes_por_tipo(
                dados
            )
        )

    # =====================================================
    # HORÁRIO DAS FRAUDES
    # =====================================================

    def horario_fraudes(self):

        dados = (

            self.repository
            .buscar_horario_fraudes()
        )

        return (

            self.anomalias_service
            .horario_fraudes(
                dados
            )
        )

    # =====================================================
    # NÚMERO DE TENTATIVAS
    # =====================================================

    def numero_de_tentativas(self):

        dados = (

            self.repository
            .buscar_numero_de_tentativas()
        )

        return (

            self.anomalias_service
            .numero_de_tentativas(
                dados
            )
        )