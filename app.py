from flask import Flask, jsonify, request
import mysql.connector
from dotenv import load_dotenv
import os

# Carrega as informações do arquivo .env
load_dotenv()

# Cria o Flask
app = Flask(__name__)

# Configuração do banco
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Função que faz a conexão com o MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)


# ==========================================================
# ROTA PRINCIPAL
# ==========================================================

@app.route("/")
def inicio():
    return "API do SPA funcionando!"


# ==========================================================
# CLIENTES
# ==========================================================

@app.route("/clientes", methods=["GET"])
def clientes():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/clientes/<int:id>", methods=["GET"])
def buscar_cliente(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM clientes WHERE id_cliente = %s",
        (id,)
    )

    cliente = cursor.fetchone()

    cursor.close()
    conexao.close()

    if cliente:
        return jsonify(cliente)

    return jsonify({"erro": "Cliente não encontrado"}), 404


@app.route("/clientes", methods=["POST"])
def cadastrar_cliente():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO clientes
        (nome, telefone, email, endereco, aceitou_lgpd, data_consentimento)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        dados["nome"],
        dados["telefone"],
        dados["email"],
        dados["endereco"],
        dados["aceitou_lgpd"],
        dados["data_consentimento"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Cliente cadastrado com sucesso!"
    }), 201


@app.route("/clientes/<int:id>", methods=["PUT"])
def atualizar_cliente(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE clientes
        SET nome = %s,
            telefone = %s,
            email = %s,
            endereco = %s,
            aceitou_lgpd = %s,
            data_consentimento = %s
        WHERE id_cliente = %s
    """

    valores = (
        dados["nome"],
        dados["telefone"],
        dados["email"],
        dados["endereco"],
        dados["aceitou_lgpd"],
        dados["data_consentimento"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Cliente atualizado com sucesso!"
    })


@app.route("/clientes/<int:id>", methods=["DELETE"])
def excluir_cliente(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM clientes WHERE id_cliente = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Cliente excluído com sucesso!"
    })



# ==========================================================
# FUNCIONÁRIOS
# ==========================================================

@app.route("/funcionarios", methods=["GET"])
def funcionarios():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM funcionarios")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/funcionarios/<int:id>", methods=["GET"])
def buscar_funcionario(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM funcionarios WHERE id_funcionario = %s",
        (id,)
    )

    funcionario = cursor.fetchone()

    cursor.close()
    conexao.close()

    if funcionario:
        return jsonify(funcionario)

    return jsonify({"erro": "Funcionário não encontrado"}), 404


@app.route("/funcionarios", methods=["POST"])
def cadastrar_funcionario():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO funcionarios
        (nome, telefone, email, cargo)
        VALUES (%s, %s, %s, %s)
    """

    valores = (
        dados["nome"],
        dados["telefone"],
        dados["email"],
        dados["cargo"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Funcionário cadastrado com sucesso!"
    }), 201


@app.route("/funcionarios/<int:id>", methods=["PUT"])
def atualizar_funcionario(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE funcionarios
        SET nome = %s,
            telefone = %s,
            email = %s,
            cargo = %s
        WHERE id_funcionario = %s
    """

    valores = (
        dados["nome"],
        dados["telefone"],
        dados["email"],
        dados["cargo"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Funcionário atualizado com sucesso!"
    })


@app.route("/funcionarios/<int:id>", methods=["DELETE"])
def excluir_funcionario(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM funcionarios WHERE id_funcionario = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Funcionário excluído com sucesso!"
    })



# ==========================================================
# SERVIÇOS
# ==========================================================

@app.route("/servicos", methods=["GET"])
def servicos():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM servicos")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/servicos/<int:id>", methods=["GET"])
def buscar_servico(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM servicos WHERE id_servico = %s",
        (id,)
    )

    servico = cursor.fetchone()

    cursor.close()
    conexao.close()

    if servico:
        return jsonify(servico)

    return jsonify({"erro": "Serviço não encontrado"}), 404


@app.route("/servicos", methods=["POST"])
def cadastrar_servico():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO servicos
        (nome, descricao, valor, duracao)
        VALUES (%s, %s, %s, %s)
    """

    valores = (
        dados["nome"],
        dados["descricao"],
        dados["valor"],
        dados["duracao"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Serviço cadastrado com sucesso!"
    }), 201


@app.route("/servicos/<int:id>", methods=["PUT"])
def atualizar_servico(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE servicos
        SET nome = %s,
            descricao = %s,
            valor = %s,
            duracao = %s
        WHERE id_servico = %s
    """

    valores = (
        dados["nome"],
        dados["descricao"],
        dados["valor"],
        dados["duracao"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Serviço atualizado com sucesso!"
    })


@app.route("/servicos/<int:id>", methods=["DELETE"])
def excluir_servico(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM servicos WHERE id_servico = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Serviço excluído com sucesso!"
    })




# ==========================================================
# AGENDAMENTOS
# ==========================================================

@app.route("/agendamentos", methods=["GET"])
def agendamentos():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM agendamentos")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/agendamentos/<int:id>", methods=["GET"])
def buscar_agendamento(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM agendamentos WHERE id_agendamento = %s",
        (id,)
    )

    agendamento = cursor.fetchone()

    cursor.close()
    conexao.close()

    if agendamento:

        # Converte a hora do MySQL para texto
        if agendamento.get("hora") is not None:
            agendamento["hora"] = str(agendamento["hora"])

        return jsonify(agendamento)

    return jsonify({
        "erro": "Agendamento não encontrado"
    }), 404


@app.route("/agendamentos", methods=["POST"])
def cadastrar_agendamento():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO agendamentos
        (id_cliente, id_funcionario, id_servico, data, hora, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        dados["id_cliente"],
        dados["id_funcionario"],
        dados["id_servico"],
        dados["data"],
        dados["hora"],
        dados["status"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Agendamento cadastrado com sucesso!"
    }), 201


@app.route("/agendamentos/<int:id>", methods=["PUT"])
def atualizar_agendamento(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE agendamentos
        SET id_cliente = %s,
            id_funcionario = %s,
            id_servico = %s,
            data = %s,
            hora = %s,
            status = %s
        WHERE id_agendamento = %s
    """

    valores = (
        dados["id_cliente"],
        dados["id_funcionario"],
        dados["id_servico"],
        dados["data"],
        dados["hora"],
        dados["status"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Agendamento atualizado com sucesso!"
    })


@app.route("/agendamentos/<int:id>", methods=["DELETE"])
def excluir_agendamento(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM agendamentos WHERE id_agendamento = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Agendamento excluído com sucesso!"
    })



# ==========================================================
# PAGAMENTOS
# ==========================================================

@app.route("/pagamentos", methods=["GET"])
def pagamentos():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM pagamentos")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/pagamentos/<int:id>", methods=["GET"])
def buscar_pagamento(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM pagamentos WHERE id_pagamento = %s",
        (id,)
    )

    pagamento = cursor.fetchone()

    cursor.close()
    conexao.close()

    if pagamento:
        return jsonify(pagamento)

    return jsonify({"erro": "Pagamento não encontrado"}), 404


@app.route("/pagamentos", methods=["POST"])
def cadastrar_pagamento():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO pagamentos
        (id_agendamento, valor, forma_pagamento, data_pagamento)
        VALUES (%s, %s, %s, %s)
    """

    valores = (
        dados["id_agendamento"],
        dados["valor"],
        dados["forma_pagamento"],
        dados["data_pagamento"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Pagamento cadastrado com sucesso!"
    }), 201


@app.route("/pagamentos/<int:id>", methods=["PUT"])
def atualizar_pagamento(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE pagamentos
        SET id_agendamento = %s,
            valor = %s,
            forma_pagamento = %s,
            data_pagamento = %s
        WHERE id_pagamento = %s
    """

    valores = (
        dados["id_agendamento"],
        dados["valor"],
        dados["forma_pagamento"],
        dados["data_pagamento"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Pagamento atualizado com sucesso!"
    })


@app.route("/pagamentos/<int:id>", methods=["DELETE"])
def excluir_pagamento(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM pagamentos WHERE id_pagamento = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Pagamento excluído com sucesso!"
    })




# ==========================================================
# PRODUTOS
# ==========================================================

@app.route("/produtos", methods=["GET"])
def produtos():

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados)


@app.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):

    conexao = get_db_connection()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM produtos WHERE id_produto = %s",
        (id,)
    )

    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    if produto:
        return jsonify(produto)

    return jsonify({"erro": "Produto não encontrado"}), 404


@app.route("/produtos", methods=["POST"])
def cadastrar_produto():

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO produtos
        (nome, categoria, quantidade, preco)
        VALUES (%s, %s, %s, %s)
    """

    valores = (
        dados["nome"],
        dados["categoria"],
        dados["quantidade"],
        dados["preco"]
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Produto cadastrado com sucesso!"
    }), 201


@app.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):

    dados = request.json

    conexao = get_db_connection()
    cursor = conexao.cursor()

    sql = """
        UPDATE produtos
        SET nome = %s,
            categoria = %s,
            quantidade = %s,
            preco = %s
        WHERE id_produto = %s
    """

    valores = (
        dados["nome"],
        dados["categoria"],
        dados["quantidade"],
        dados["preco"],
        id
    )

    cursor.execute(sql, valores)
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Produto atualizado com sucesso!"
    })


@app.route("/produtos/<int:id>", methods=["DELETE"])
def excluir_produto(id):

    conexao = get_db_connection()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id_produto = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Produto excluído com sucesso!"
    })


# ==========================================================
# INICIA O SERVIDOR
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)