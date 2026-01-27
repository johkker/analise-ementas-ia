from src.services.extractor.base import BaseExtractor

class CamaraExtractor(BaseExtractor):
    def __init__(self):
        super().__init__("https://dadosabertos.camara.leg.br/api/v2")

    async def get_deputados(self):
        data = await self.fetch_raw_data("/deputados")
        print(data)
        return data['dados']

    async def get_gastos(self, deputado_id: int, ano: int = 2024, pagina: int = 1, itens: int = 100):
        endpoint = f"/deputados/{deputado_id}/despesas"
        params = {
            "ano": ano, 
            "pagina": pagina,
            "itens": itens,
            "ordem": "ASC", 
            "ordenarPor": "dataDocumento"
        }
        data = await self.fetch_raw_data(endpoint, params=params)
        return data['dados']

    async def get_proposicoes(self, data_inicio: str, data_fim: str, pagina: int = 1, itens: int = 100):
        endpoint = "/proposicoes"
        params = {
            "dataApresentacaoInicio": data_inicio,
            "dataApresentacaoFim": data_fim,
            "pagina": pagina,
            "itens": itens,
            "ordem": "ASC",
            "ordenarPor": "id"
        }
        data = await self.fetch_raw_data(endpoint, params=params)
        return data['dados']

    async def get_votacoes(self, data_inicio: str, data_fim: str, pagina: int = 1, itens: int = 100):
        endpoint = "/votacoes"
        params = {
            "dataInicio": data_inicio,
            "dataFim": data_fim,
            "pagina": pagina,
            "itens": itens,
            "ordem": "DESC",
            "ordenarPor": "dataHoraRegistro"
        }
        data = await self.fetch_raw_data(endpoint, params=params)
        return data['dados']

    async def get_votacao_votos(self, votacao_id: str):
        endpoint = f"/votacoes/{votacao_id}/votos"
        try:
            data = await self.fetch_raw_data(endpoint)
            return data['dados']
        except Exception:
            # Algumas votações podem não ter votos registrados individualmente ou dar 404
            return []

    async def get_proposicao_autores(self, proposicao_id: int):
        endpoint = f"/proposicoes/{proposicao_id}/autores"
        try:
            data = await self.fetch_raw_data(endpoint)
            return data['dados']
        except Exception:
             # Pode não haver autores ou dar 404
            return []

    def parse_schema(self, data: dict):
        # Implementação específica se necessário
        return data
