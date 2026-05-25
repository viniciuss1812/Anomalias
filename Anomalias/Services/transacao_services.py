#aqui é o service para fazer o crud transacoes

from Repository.transacao_repository import (
    TransacaoRepository
)

class TransacaoService:

    def __init__(self):

        self.repository = (
            TransacaoRepository()
        )

    # =====================================================
    # TRANSAÇÕES
    # =====================================================

    def listar_transacoes(self):

        return (
            self.repository
            .get_transacoes()
        )

    def buscar_transacao_por_conta(
        self,
        conta: str
    ):

        return (
            self.repository
            .get_transacao_por_conta(
                conta
            )
        )

    def listar_contas(self):

        return (
            self.repository
            .get_contas()
        )

    def criar_transacao(
        self,
        transacao
    ):

        return (
            self.repository
            .inserir_transacao(
                transacao
            )
        )
    
    def atualizar_status_fraude(
        self,
        id: int,
        is_fraude: bool
    ):

        return (
            self.repository
            .update_status_fraude(
                id,
                is_fraude
            )
        )

    # =====================================================
    # DELETAR TRANSAÇÃO
    # =====================================================

    def deletar_transacao(
        self,
        id: int
    ):

        return (
            self.repository
            .delete_transacao(id)
        )

    # =====================================================
    # FILTROS
    # =====================================================

    def buscar_transacoes(

        self,

        categoria=None,

        cidade=None,

        valor_min=None,

        valor_max=None,

        tipo_transacao=None,

        dispositivo=None,

        data_inicio=None,

        data_fim=None

    ):

        return (

            self.repository
            .query_transacoes(

                categoria=categoria,

                cidade=cidade,

                valor_min=valor_min,

                valor_max=valor_max,

                tipo_transacao=tipo_transacao,

                dispositivo=dispositivo,

                data_inicio=data_inicio,

                data_fim=data_fim
            )
        )
