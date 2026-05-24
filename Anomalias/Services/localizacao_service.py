from Repository.transacao_repository import (
    TransacaoRepository
)

from Services.geo_services import (
    GeoServices
)


class LocalizacaoService:

    def __init__(self):

        self.repository = (
            TransacaoRepository()
        )

        self.geo_service = (
            GeoServices()
        )

    # =====================================================
    # DISTÂNCIA
    # =====================================================

    def geo_distancia(
        self,
        conta: str
    ):

        df = (

            self.repository
            .buscar_localizacao_por_conta(
                conta
            )
        )

        return (

            self.geo_service
            .geo_distancia(
                df,
                conta
            )
        )

    # =====================================================
    # GEO IP
    # =====================================================

    def geo_ip(
        self,
        conta: str
    ):

        df = (

            self.repository
            .buscar_ips_por_conta(
                conta
            )
        )

        return (

            self.geo_service
            .geo_ip(
                df,
                conta
            )
        )

    # =====================================================
    # GEO VELOCIDADE
    # =====================================================

    def geo_velocidade(
        self,
        conta: str
    ):

        df = (

            self.repository
            .buscar_velocidade_por_conta(
                conta
            )
        )

        return (

            self.geo_service
            .geo_velocidade(
                df,
                conta
            )
        )