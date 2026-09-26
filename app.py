import os
from datetime import date, datetime, time
from decimal import Decimal

import mysql.connector
from flask import Flask, jsonify, request, send_file


def _carregar_variaveis_ambiente():
    if not os.path.exists('.env'):
        return

    with open('.env', 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith('#') or '=' not in linha:
                continue
            chave, valor = linha.split('=', 1)
            os.environ.setdefault(chave.strip(), valor.strip())


_carregar_variaveis_ambiente()

app = Flask(__name__)

TABELAS = {
    'clientes': {'table': 'clientes', 'pk': 'id_cliente'},
    'funcionarios': {'table': 'funcionarios', 'pk': 'id_funcionario'},
    'servicos': {'table': 'servicos', 'pk': 'id_servico'},
    'agendamentos': {'table': 'agendamentos', 'pk': 'id_agendamento'},
    'pagamentos': {'table': 'pagamentos', 'pk': 'id_pagamento'},
    'produtos': {'table': 'produtos', 'pk': 'id_produto'},
}


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'spa_salao'),
        autocommit=True,
        charset='utf8mb4',
    )


def _serializar_valor(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()
    if isinstance(valor, bytes):
        return valor.decode('utf-8')
    return valor


def _serializar_registro(registro):
    if not isinstance(registro, dict):
        return registro
    return {chave: _serializar_valor(valor) for chave, valor in registro.items()}


def _criar_tabelas_se_nao_existirem():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(50),
            telefone VARCHAR(20),
            email VARCHAR(50),
            endereco VARCHAR(50),
            aceitou_lgpd ENUM('sim', 'não') NOT NULL,
            data_consentimento DATE NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(50),
            telefone VARCHAR(20),
            email VARCHAR(50),
            cargo VARCHAR(50)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS servicos (
            id_servico INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(50),
            descricao VARCHAR(100),
            valor DECIMAL(10,2),
            duracao INT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agendamentos (
            id_agendamento INT AUTO_INCREMENT PRIMARY KEY,
            id_cliente INT,
            id_funcionario INT,
            id_servico INT,
            data DATE,
            hora TIME,
            status VARCHAR(30),
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
            FOREIGN KEY (id_funcionario) REFERENCES funcionarios(id_funcionario),
            FOREIGN KEY (id_servico) REFERENCES servicos(id_servico)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
            id_agendamento INT,
            valor DECIMAL(10,2),
            forma_pagamento VARCHAR(30),
            data_pagamento DATE,
            FOREIGN KEY (id_agendamento) REFERENCES agendamentos(id_agendamento)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id_produto INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100),
            categoria VARCHAR(50),
            quantidade INT,
            preco DECIMAL(10,2)
        )
        """
    )

    cursor.close()
    conn.close()


_criar_tabelas_se_nao_existirem()


def _valor_decimal(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def _obter_json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def _listar_entidade(chave):
    config = TABELAS.get(chave)
    if not config:
        return []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM `{config['table']}` ORDER BY `{config['pk']}`")
    registros = [_serializar_registro(item) for item in cursor.fetchall()]
    cursor.close()
    conn.close()
    return registros


def _buscar_entidade(chave, id_valor):
    config = TABELAS.get(chave)
    if not config:
        return None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM `{config['table']}` WHERE `{config['pk']}` = %s", (id_valor,))
    registro = _serializar_registro(cursor.fetchone())
    cursor.close()
    conn.close()
    return registro


def _criar_entidade(chave, dados):
    config = TABELAS.get(chave)
    if not config or not dados:
        return None

    colunas = ', '.join(f'`{campo}`' for campo in dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    valores = list(dados.values())

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"INSERT INTO `{config['table']}` ({colunas}) VALUES ({placeholders})", valores)
    novo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return _buscar_entidade(chave, novo_id)


def _atualizar_entidade(chave, id_valor, dados):
    config = TABELAS.get(chave)
    if not config:
        return None

    if not dados:
        return _buscar_entidade(chave, id_valor)

    campos = list(dados.keys())
    set_clause = ', '.join(f'`{campo}` = %s' for campo in campos)
    valores = [dados[campo] for campo in campos]
    valores.append(id_valor)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"UPDATE `{config['table']}` SET {set_clause} WHERE `{config['pk']}` = %s", valores)
    cursor.close()
    conn.close()
    return _buscar_entidade(chave, id_valor)


def _excluir_entidade(chave, id_valor):
    config = TABELAS.get(chave)
    if not config:
        return False

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"DELETE FROM `{config['table']}` WHERE `{config['pk']}` = %s", (id_valor,))
    removido = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return removido


@app.route("/")
def pagina_inicial():
    return send_file('index.html')


@app.route('/style.css')
def servir_estilo():
    return send_file('style.css')


@app.route('/script.js')
def servir_script():
    return send_file('script.js')


@app.route('/logo.png')
def servir_logo():
    return send_file('logo.png')


@app.route('/spa.png')
def servir_imagem_spa():
    return send_file('spa.png')


@app.route('/api/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT (SELECT COUNT(*) FROM clientes) AS clientes')
    clientes = cursor.fetchone()['clientes']

    cursor.execute('SELECT (SELECT COUNT(*) FROM servicos) AS servicos')
    servicos = cursor.fetchone()['servicos']

    cursor.execute('SELECT (SELECT COUNT(*) FROM agendamentos) AS agendamentos')
    agendamentos = cursor.fetchone()['agendamentos']

    cursor.execute('SELECT (SELECT COUNT(*) FROM produtos) AS produtos')
    produtos = cursor.fetchone()['produtos']

    cursor.execute('SELECT COALESCE(SUM(valor), 0) AS receita_total FROM pagamentos')
    receita_total = float(cursor.fetchone()['receita_total'] or 0)

    cursor.execute("SELECT COUNT(*) AS agendamentos_confirmados FROM agendamentos WHERE LOWER(status) = 'confirmado'")
    agendamentos_confirmados = cursor.fetchone()['agendamentos_confirmados']

    cursor.execute('SELECT * FROM agendamentos ORDER BY id_agendamento LIMIT 3')
    proximos_agendamentos = [_serializar_registro(item) for item in cursor.fetchall()]

    cursor.close()
    conn.close()

    return jsonify({
        'clientes': clientes,
        'servicos': servicos,
        'agendamentos': agendamentos,
        'produtos': produtos,
        'receita_total': round(receita_total, 2),
        'agendamentos_confirmados': agendamentos_confirmados,
        'proximos_agendamentos': proximos_agendamentos,
    })


@app.route('/api/clientes', methods=['GET'])
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    return jsonify(_listar_entidade('clientes'))


@app.route('/api/clientes/<int:id_cliente>', methods=['GET'])
def buscar_cliente_por_id(id_cliente):
    cliente = _buscar_entidade('clientes', id_cliente)
    if not cliente:
        return jsonify({'erro': 'Cliente não encontrado.'}), 404
    return jsonify(cliente)


@app.route('/api/clientes', methods=['POST'])
@app.route('/clientes', methods=['POST'])
def cadastrar_cliente():
    dados = _obter_json()
    cliente = _criar_entidade('clientes', {
        'nome': dados.get('nome', 'Cliente novo'),
        'telefone': dados.get('telefone', ''),
        'email': dados.get('email', ''),
        'endereco': dados.get('endereco', ''),
        'aceitou_lgpd': dados.get('aceitou_lgpd', 'não'),
        'data_consentimento': dados.get('data_consentimento', '2026-09-25'),
    })
    return jsonify({'mensagem': 'Cliente cadastrado com sucesso!', 'cliente': cliente}), 201


@app.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
@app.route('/clientes/<int:id_cliente>', methods=['PUT'])
def atualizar_cliente(id_cliente):
    cliente = _buscar_entidade('clientes', id_cliente)
    if not cliente:
        return jsonify({'erro': 'Cliente não encontrado.'}), 404

    dados = _obter_json()
    cliente_atualizado = _atualizar_entidade('clientes', id_cliente, {
        'nome': dados.get('nome', cliente.get('nome')),
        'telefone': dados.get('telefone', cliente.get('telefone')),
        'email': dados.get('email', cliente.get('email')),
        'endereco': dados.get('endereco', cliente.get('endereco')),
        'aceitou_lgpd': dados.get('aceitou_lgpd', cliente.get('aceitou_lgpd')),
        'data_consentimento': dados.get('data_consentimento', cliente.get('data_consentimento')),
    })
    return jsonify({'mensagem': 'Cliente atualizado com sucesso!', 'cliente': cliente_atualizado})


@app.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
@app.route('/clientes/<int:id_cliente>', methods=['DELETE'])
def excluir_cliente(id_cliente):
    if not _excluir_entidade('clientes', id_cliente):
        return jsonify({'erro': 'Cliente não encontrado.'}), 404
    return jsonify({'mensagem': 'Cliente excluído com sucesso!'})


@app.route('/api/funcionarios', methods=['GET'])
@app.route('/funcionarios', methods=['GET'])
def listar_funcionarios():
    return jsonify(_listar_entidade('funcionarios'))


@app.route('/api/funcionarios/<int:id_funcionario>', methods=['GET'])
def buscar_funcionario_por_id(id_funcionario):
    funcionario = _buscar_entidade('funcionarios', id_funcionario)
    if not funcionario:
        return jsonify({'erro': 'Funcionário não encontrado.'}), 404
    return jsonify(funcionario)


@app.route('/api/funcionarios', methods=['POST'])
@app.route('/funcionarios', methods=['POST'])
def cadastrar_funcionario():
    dados = _obter_json()
    funcionario = _criar_entidade('funcionarios', {
        'nome': dados.get('nome', 'Funcionário novo'),
        'telefone': dados.get('telefone', ''),
        'email': dados.get('email', ''),
        'cargo': dados.get('cargo', ''),
    })
    return jsonify({'mensagem': 'Funcionário cadastrado com sucesso!', 'funcionario': funcionario}), 201


@app.route('/api/funcionarios/<int:id_funcionario>', methods=['PUT'])
@app.route('/funcionarios/<int:id_funcionario>', methods=['PUT'])
def atualizar_funcionario(id_funcionario):
    funcionario = _buscar_entidade('funcionarios', id_funcionario)
    if not funcionario:
        return jsonify({'erro': 'Funcionário não encontrado.'}), 404

    dados = _obter_json()
    funcionario_atualizado = _atualizar_entidade('funcionarios', id_funcionario, {
        'nome': dados.get('nome', funcionario.get('nome')),
        'telefone': dados.get('telefone', funcionario.get('telefone')),
        'email': dados.get('email', funcionario.get('email')),
        'cargo': dados.get('cargo', funcionario.get('cargo')),
    })
    return jsonify({'mensagem': 'Funcionário atualizado com sucesso!', 'funcionario': funcionario_atualizado})


@app.route('/api/funcionarios/<int:id_funcionario>', methods=['DELETE'])
@app.route('/funcionarios/<int:id_funcionario>', methods=['DELETE'])
def excluir_funcionario(id_funcionario):
    if not _excluir_entidade('funcionarios', id_funcionario):
        return jsonify({'erro': 'Funcionário não encontrado.'}), 404
    return jsonify({'mensagem': 'Funcionário excluído com sucesso!'})


@app.route('/api/servicos', methods=['GET'])
@app.route('/servicos', methods=['GET'])
def listar_servicos():
    return jsonify(_listar_entidade('servicos'))


@app.route('/api/servicos/<int:id_servico>', methods=['GET'])
def buscar_servico_por_id(id_servico):
    servico = _buscar_entidade('servicos', id_servico)
    if not servico:
        return jsonify({'erro': 'Serviço não encontrado.'}), 404
    return jsonify(servico)


@app.route('/api/servicos', methods=['POST'])
@app.route('/servicos', methods=['POST'])
def cadastrar_servico():
    dados = _obter_json()
    servico = _criar_entidade('servicos', {
        'nome': dados.get('nome', 'Novo serviço'),
        'descricao': dados.get('descricao', ''),
        'valor': _valor_decimal(dados.get('valor', 0)),
        'duracao': int(dados.get('duracao', 30)),
    })
    return jsonify({'mensagem': 'Serviço cadastrado com sucesso!', 'servico': servico}), 201


@app.route('/api/servicos/<int:id_servico>', methods=['PUT'])
@app.route('/servicos/<int:id_servico>', methods=['PUT'])
def atualizar_servico(id_servico):
    servico = _buscar_entidade('servicos', id_servico)
    if not servico:
        return jsonify({'erro': 'Serviço não encontrado.'}), 404

    dados = _obter_json()
    servico_atualizado = _atualizar_entidade('servicos', id_servico, {
        'nome': dados.get('nome', servico.get('nome')),
        'descricao': dados.get('descricao', servico.get('descricao')),
        'valor': _valor_decimal(dados.get('valor', servico.get('valor'))),
        'duracao': int(dados.get('duracao', servico.get('duracao'))),
    })
    return jsonify({'mensagem': 'Serviço atualizado com sucesso!', 'servico': servico_atualizado})


@app.route('/api/servicos/<int:id_servico>', methods=['DELETE'])
@app.route('/servicos/<int:id_servico>', methods=['DELETE'])
def excluir_servico(id_servico):
    if not _excluir_entidade('servicos', id_servico):
        return jsonify({'erro': 'Serviço não encontrado.'}), 404
    return jsonify({'mensagem': 'Serviço excluído com sucesso!'})


@app.route('/api/agendamentos', methods=['GET'])
@app.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    return jsonify(_listar_entidade('agendamentos'))


@app.route('/api/agendamentos/<int:id_agendamento>', methods=['GET'])
def buscar_agendamento_por_id(id_agendamento):
    agendamento = _buscar_entidade('agendamentos', id_agendamento)
    if not agendamento:
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404
    return jsonify(agendamento)


@app.route('/api/agendamentos', methods=['POST'])
@app.route('/agendamentos', methods=['POST'])
def cadastrar_agendamento():
    dados = _obter_json()
    agendamento = _criar_entidade('agendamentos', {
        'id_cliente': int(dados.get('id_cliente', 0)),
        'id_funcionario': int(dados.get('id_funcionario', 0)),
        'id_servico': int(dados.get('id_servico', 0)),
        'data': dados.get('data', '2026-09-25'),
        'hora': dados.get('hora', '09:00:00'),
        'status': dados.get('status', 'Agendado'),
    })
    return jsonify({'mensagem': 'Agendamento cadastrado com sucesso!', 'agendamento': agendamento}), 201


@app.route('/api/agendamentos/<int:id_agendamento>', methods=['PUT'])
@app.route('/agendamentos/<int:id_agendamento>', methods=['PUT'])
def atualizar_agendamento(id_agendamento):
    agendamento = _buscar_entidade('agendamentos', id_agendamento)
    if not agendamento:
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404

    dados = _obter_json()
    agendamento_atualizado = _atualizar_entidade('agendamentos', id_agendamento, {
        'id_cliente': int(dados.get('id_cliente', agendamento.get('id_cliente'))),
        'id_funcionario': int(dados.get('id_funcionario', agendamento.get('id_funcionario'))),
        'id_servico': int(dados.get('id_servico', agendamento.get('id_servico'))),
        'data': dados.get('data', agendamento.get('data')),
        'hora': dados.get('hora', agendamento.get('hora')),
        'status': dados.get('status', agendamento.get('status')),
    })
    return jsonify({'mensagem': 'Agendamento atualizado com sucesso!', 'agendamento': agendamento_atualizado})


@app.route('/api/agendamentos/<int:id_agendamento>', methods=['DELETE'])
@app.route('/agendamentos/<int:id_agendamento>', methods=['DELETE'])
def excluir_agendamento(id_agendamento):
    if not _excluir_entidade('agendamentos', id_agendamento):
        return jsonify({'erro': 'Agendamento não encontrado.'}), 404
    return jsonify({'mensagem': 'Agendamento excluído com sucesso!'})


@app.route('/api/pagamentos', methods=['GET'])
@app.route('/pagamentos', methods=['GET'])
def listar_pagamentos():
    return jsonify(_listar_entidade('pagamentos'))


@app.route('/api/pagamentos/<int:id_pagamento>', methods=['GET'])
def buscar_pagamento_por_id(id_pagamento):
    pagamento = _buscar_entidade('pagamentos', id_pagamento)
    if not pagamento:
        return jsonify({'erro': 'Pagamento não encontrado.'}), 404
    return jsonify(pagamento)


@app.route('/api/pagamentos', methods=['POST'])
@app.route('/pagamentos', methods=['POST'])
def cadastrar_pagamento():
    dados = _obter_json()
    pagamento = _criar_entidade('pagamentos', {
        'id_agendamento': int(dados.get('id_agendamento', 0)),
        'valor': _valor_decimal(dados.get('valor', 0)),
        'forma_pagamento': dados.get('forma_pagamento', 'Pix'),
        'data_pagamento': dados.get('data_pagamento', '2026-09-25'),
    })
    return jsonify({'mensagem': 'Pagamento cadastrado com sucesso!', 'pagamento': pagamento}), 201


@app.route('/api/pagamentos/<int:id_pagamento>', methods=['PUT'])
@app.route('/pagamentos/<int:id_pagamento>', methods=['PUT'])
def atualizar_pagamento(id_pagamento):
    pagamento = _buscar_entidade('pagamentos', id_pagamento)
    if not pagamento:
        return jsonify({'erro': 'Pagamento não encontrado.'}), 404

    dados = _obter_json()
    pagamento_atualizado = _atualizar_entidade('pagamentos', id_pagamento, {
        'id_agendamento': int(dados.get('id_agendamento', pagamento.get('id_agendamento'))),
        'valor': _valor_decimal(dados.get('valor', pagamento.get('valor'))),
        'forma_pagamento': dados.get('forma_pagamento', pagamento.get('forma_pagamento')),
        'data_pagamento': dados.get('data_pagamento', pagamento.get('data_pagamento')),
    })
    return jsonify({'mensagem': 'Pagamento atualizado com sucesso!', 'pagamento': pagamento_atualizado})


@app.route('/api/pagamentos/<int:id_pagamento>', methods=['DELETE'])
@app.route('/pagamentos/<int:id_pagamento>', methods=['DELETE'])
def excluir_pagamento(id_pagamento):
    if not _excluir_entidade('pagamentos', id_pagamento):
        return jsonify({'erro': 'Pagamento não encontrado.'}), 404
    return jsonify({'mensagem': 'Pagamento excluído com sucesso!'})


@app.route('/api/produtos', methods=['GET'])
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    return jsonify(_listar_entidade('produtos'))


@app.route('/api/produtos/<int:id_produto>', methods=['GET'])
def buscar_produto_por_id(id_produto):
    produto = _buscar_entidade('produtos', id_produto)
    if not produto:
        return jsonify({'erro': 'Produto não encontrado.'}), 404
    return jsonify(produto)


@app.route('/api/produtos', methods=['POST'])
@app.route('/produtos', methods=['POST'])
def cadastrar_produto():
    dados = _obter_json()
    produto = _criar_entidade('produtos', {
        'nome': dados.get('nome', 'Novo produto'),
        'categoria': dados.get('categoria', ''),
        'quantidade': int(dados.get('quantidade', 0)),
        'preco': _valor_decimal(dados.get('preco', 0)),
    })
    return jsonify({'mensagem': 'Produto cadastrado com sucesso!', 'produto': produto}), 201


@app.route('/api/produtos/<int:id_produto>', methods=['PUT'])
@app.route('/produtos/<int:id_produto>', methods=['PUT'])
def atualizar_produto(id_produto):
    produto = _buscar_entidade('produtos', id_produto)
    if not produto:
        return jsonify({'erro': 'Produto não encontrado.'}), 404

    dados = _obter_json()
    produto_atualizado = _atualizar_entidade('produtos', id_produto, {
        'nome': dados.get('nome', produto.get('nome')),
        'categoria': dados.get('categoria', produto.get('categoria')),
        'quantidade': int(dados.get('quantidade', produto.get('quantidade'))),
        'preco': _valor_decimal(dados.get('preco', produto.get('preco'))),
    })
    return jsonify({'mensagem': 'Produto atualizado com sucesso!', 'produto': produto_atualizado})


@app.route('/api/produtos/<int:id_produto>', methods=['DELETE'])
@app.route('/produtos/<int:id_produto>', methods=['DELETE'])
def excluir_produto(id_produto):
    if not _excluir_entidade('produtos', id_produto):
        return jsonify({'erro': 'Produto não encontrado.'}), 404
    return jsonify({'mensagem': 'Produto excluído com sucesso!'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)