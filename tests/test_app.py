# Arquivo de testes da aplicação Flask.
# Ele valida as rotas principais e garante que a API responda corretamente.
import unittest

# Importa a instância da aplicação para ser testada.
from app import app


# Classe de testes para verificar o comportamento das rotas da aplicação.
class TestAppSpa(unittest.TestCase):
    # Cria um cliente de teste do Flask em cada teste.
    def setUp(self):
        self.cliente = app.test_client()

    # Verifica se a página inicial carrega e exibe o dashboard.
    def test_rota_principal_carrega_dashboard(self):
        resposta = self.cliente.get('/')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b'Dashboard', resposta.data)

    # Verifica se o endpoint de dashboard retorna um JSON válido.
    def test_endpoint_dashboard_retorna_json(self):
        resposta = self.cliente.get('/api/dashboard')
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b'agendamentos', resposta.data)
        self.assertIn(b'clientes', resposta.data)

    # Verifica se a API de serviços responde com uma lista em JSON.
    def test_endpoint_servicos_retorna_json(self):
        resposta = self.cliente.get('/api/servicos')
        self.assertEqual(resposta.status_code, 200)
        self.assertIsInstance(resposta.get_json(), list)


# Permite executar os testes diretamente com Python.
if __name__ == '__main__':
    unittest.main()
