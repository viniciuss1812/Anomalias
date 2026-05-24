from Repository.transacao_repository import (
    TransacaoRepository
)

from Services.zscore_service import (
    ZScoreService
)

from Services.gaussiana_service import (
    GaussianaService
)


class AnomaliasService:

    def __init__(self):

        self.repository = (
            TransacaoRepository()
        )

        self.zscore_service = (
            ZScoreService()
        )

        self.gaussiana_service = (
            GaussianaService()
        )

    # =====================================================
    # ZSCORE
    # =====================================================

    def zscore_por_conta(
        self,
        conta: str
    ):

        df = (

            self.repository
            .buscar_valores_por_conta(
                conta
            )
        )

        return (

            self.zscore_service
            .calcular_zscore(
                df,
                conta
            )
        )

    # =====================================================
    # GAUSSIANA
    # =====================================================

    def gaussiana_por_conta(
        self,
        conta: str
    ):

        df = (

            self.repository
            .buscar_valores_por_conta(
                conta
            )
        )

        return (

            self.gaussiana_service
            .calcular_gaussiana(
                df,
                conta
            )
        )