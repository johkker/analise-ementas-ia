from src.services.extractor.base import BaseExtractor

class CamaraExtractor(BaseExtractor):
    def __init__(self):
        super().__init__("https://dadosabertos.camara.leg.br/api/v2")

    async def get_deputados(self):
        data = await self.fetch_raw_data("/deputados")
        return data['dados']

    async def get_gastos(self, deputado_id: int, ano: int = 2024):
        endpoint = f"/deputados/{deputado_id}/despesas"
        params = {"ano": ano, "ordem": "ASC", "ordenarPor": "dataDocumento"}
        data = await self.fetch_raw_data(endpoint, params=params)
        return data['dados']

    def parse_schema(self, data: dict):
        # Implementação específica se necessário
        return data
