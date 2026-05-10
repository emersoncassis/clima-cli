import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Adiciona o diretório pai ao sys.path para que possamos importar main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main


class TestClimaCLI(unittest.TestCase):
    def test_obter_animacao_clima(self):
        # Verifica se o retorno de obter_animacao_clima está entre os frames esperados
        frames_esperados = ["☀️  ", "🌞 ", "☀️  ", "🌤️  "]
        for seg in range(10):
            frame = main.obter_animacao_clima(seg)
            self.assertIn(frame, frames_esperados)
            self.assertEqual(frame, frames_esperados[seg % len(frames_esperados)])

    def test_get_utilidade_publica_sao_paulo(self):
        # Testar para São Paulo (independentemente de maiúsculas/minúsculas e acentos)
        result = main.get_utilidade_publica("São Paulo", {})
        self.assertIn("Rodízio", result)

        result_caps = main.get_utilidade_publica("SAO PAULO", {})
        self.assertIn("Rodízio", result_caps)

    def test_get_utilidade_publica_rio(self):
        # Testar para Rio de Janeiro
        result = main.get_utilidade_publica("Rio de Janeiro", {})
        self.assertIn("Cond. Mar", result)

    def test_get_utilidade_publica_centro_oeste(self):
        # Testar para Goiânia com umidade baixa
        result_seca = main.get_utilidade_publica("Goiânia", {"humidity": "25"})
        self.assertIn("Umidade Crítica", result_seca)

        # Testar para Goiânia com umidade média
        result_media = main.get_utilidade_publica("Goiania", {"humidity": "40"})
        self.assertIn("Umidade Baixa", result_media)

        # Testar para Goiânia com umidade alta
        result_alta = main.get_utilidade_publica("Brasília", {"humidity": "60"})
        self.assertIn("Umidade em níveis aceitáveis", result_alta)

    def test_get_utilidade_publica_default(self):
        # Testar cidade genérica (ex: Belo Horizonte)
        dados = {"FeelsLikeC": "22", "uvIndex": "5"}
        result = main.get_utilidade_publica("Belo Horizonte", dados)
        self.assertIn("Sensação 22°C", result)
        self.assertIn("Índice UV 5", result)

    @patch("requests.get")
    def test_get_utilidade_publica_londres_sucesso(self, mock_get):
        # Configurar mock para retornar status de sucesso da API de Londres (TfL)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Central", "lineStatuses": [{"statusSeverity": 10}]},
            {"name": "Piccadilly", "lineStatuses": [{"statusSeverity": 9}]},
        ]
        mock_get.return_value = mock_response

        result = main.get_utilidade_publica("Londres", {})
        self.assertIn("Piccadilly", result)
        self.assertIn("Tube", result)

    @patch("requests.get")
    def test_get_utilidade_publica_londres_falha(self, mock_get):
        # Configurar mock para lançar uma exceção de conexão
        mock_get.side_effect = Exception("Falha de rede")

        result = main.get_utilidade_publica("London", {})
        self.assertIn("Tube (Status indisponível)", result)

    @patch("requests.get")
    def test_obter_dados_clima(self, mock_get):
        # Configurar mock de resposta para wttr.in
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_condition": [
                {
                    "temp_C": "25",
                    "humidity": "65",
                    "windspeedKmph": "12",
                    "weatherCode": "113",
                    "FeelsLikeC": "26",
                    "uvIndex": "6",
                }
            ]
        }
        mock_get.return_value = mock_response

        clima_info = main.obter_dados_clima("Campinas")

        self.assertEqual(clima_info["temp"], "25")
        self.assertEqual(clima_info["umidade"], "65")
        self.assertEqual(clima_info["vento"], "12")
        self.assertEqual(clima_info["condicao"], "Ensolarado")
        self.assertIn("Sensação 26°C", clima_info["utilidade"])

    def test_get_utilidade_publica_cpbr18(self):
        # Verifica se o retorno de utilidade publica para CPBR18 é personalizado
        result = main.get_utilidade_publica("cpbr18", {})
        self.assertIn("CPBR18", result)

        result_caps = main.get_utilidade_publica("CPBR18", {})
        self.assertIn("CPBR18", result_caps)

        result_campus = main.get_utilidade_publica("Campus Party", {})
        self.assertIn("CPBR18", result_campus)


if __name__ == "__main__":
    unittest.main()
