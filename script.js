const elementoTituloPagina = document.getElementById('titulo-pagina');
const botoesMenu = document.querySelectorAll('.menu[data-secao]');
const secoesConteudo = document.querySelectorAll('[data-secao-conteudo]');

const mapasSecao = {
    dashboard: 'Dashboard',
    agendamentos: 'Agendamentos',
    clientes: 'Clientes',
    servicos: 'Serviços',
    produtos: 'Produtos',
    pagamentos: 'Pagamentos',
};

function mostrarSecao(secaoSelecionada) {
    botoesMenu.forEach((botao) => {
        const ativo = botao.dataset.secao === secaoSelecionada;
        botao.classList.toggle('ativo', ativo);
    });

    secoesConteudo.forEach((secao) => {
        const deveMostrar = secao.dataset.secaoConteudo === secaoSelecionada;
        secao.classList.toggle('oculto', !deveMostrar);
    });

    if (elementoTituloPagina) {
        elementoTituloPagina.textContent = mapasSecao[secaoSelecionada] || 'Dashboard';
    }
}

async function buscarDados(url) {
    const resposta = await fetch(url);

    if (!resposta.ok) {
        throw new Error(`Erro ao carregar ${url}`);
    }

    return resposta.json();
}

async function enviarDados(url, metodo, corpo) {
    const resposta = await fetch(url, {
        method: metodo,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(corpo),
    });

    const dadosResposta = await resposta.json();

    if (!resposta.ok) {
        throw new Error(dadosResposta.erro || 'Erro ao salvar dados.');
    }

    return dadosResposta;
}

function formatarDinheiro(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    }).format(Number(valor || 0));
}

function formatarTexto(texto) {
    return texto || '—';
}

function renderizarDashboard(dados) {
    const container = document.getElementById('resumo-dashboard');

    if (!container) {
        return;
    }

    const itens = [
        {
            titulo: 'Agendamentos',
            valor: dados.agendamentos || 0,
            descricao: 'Total no sistema',
            icone: 'ph ph-calendar',
        },
        {
            titulo: 'Clientes',
            valor: dados.clientes || 0,
            descricao: 'Cadastrados',
            icone: 'ph ph-users',
        },
        {
            titulo: 'Serviços',
            valor: dados.servicos || 0,
            descricao: 'Disponíveis',
            icone: 'ph ph-sparkle',
        },
        {
            titulo: 'Receita',
            valor: formatarDinheiro(dados.receita_total),
            descricao: 'Este mês',
            icone: 'ph ph-money',
        },
    ];

    container.innerHTML = itens.map((item) => `
        <div class="card">
            <div class="icone-card">
                <i class="${item.icone}"></i>
            </div>
            <div>
                <h3>${item.titulo}</h3>
                <strong>${item.valor}</strong>
                <p>${item.descricao}</p>
            </div>
        </div>
    `).join('');

    const proximosAgendamentos = document.createElement('div');
    proximosAgendamentos.className = 'painel painel-interno';
    proximosAgendamentos.innerHTML = `
        <div class="cabecalho-painel">
            <h3>Próximos agendamentos</h3>
        </div>
        <div class="lista-itens">
            ${(dados.proximos_agendamentos || []).map((agendamento) => `
                <div class="item">
                    <h4>Agendamento #${agendamento.id_agendamento}</h4>
                    <p><strong>Cliente:</strong> ${agendamento.id_cliente}</p>
                    <p><strong>Data:</strong> ${agendamento.data}</p>
                    <p><strong>Hora:</strong> ${agendamento.hora}</p>
                    <p><strong>Status:</strong> ${agendamento.status}</p>
                </div>
            `).join('') || '<p>Nenhum agendamento disponível.</p>'}
        </div>
    `;

    container.appendChild(proximosAgendamentos);
}

function renderizarListaClientes(listaClientes) {
    const container = document.getElementById('lista-clientes');
    container.innerHTML = (listaClientes || []).map((cliente) => `
        <div class="item">
            <h4>${cliente.nome}</h4>
            <p><strong>Telefone:</strong> ${formatarTexto(cliente.telefone)}</p>
            <p><strong>Email:</strong> ${formatarTexto(cliente.email)}</p>
            <p><strong>Endereço:</strong> ${formatarTexto(cliente.endereco)}</p>
            <p><strong>LGPD:</strong> ${formatarTexto(cliente.aceitou_lgpd)}</p>
            <div class="acoes">
                <button class="botao-secundario" data-tipo="cliente" data-acao="editar" data-id="${cliente.id_cliente}">Editar</button>
                <button class="botao-perigo" data-tipo="cliente" data-acao="excluir" data-id="${cliente.id_cliente}">Excluir</button>
            </div>
        </div>
    `).join('') || '<p class="mensagem-vazia">Nenhum cliente cadastrado.</p>';
}

function renderizarListaServicos(listaServicos) {
    const container = document.getElementById('lista-servicos');
    container.innerHTML = (listaServicos || []).map((servico) => `
        <div class="item">
            <h4>${servico.nome}</h4>
            <p><strong>Descrição:</strong> ${formatarTexto(servico.descricao)}</p>
            <p><strong>Valor:</strong> ${formatarDinheiro(servico.valor)}</p>
            <p><strong>Duração:</strong> ${servico.duracao} min</p>
            <div class="acoes">
                <button class="botao-secundario" data-tipo="servico" data-acao="editar" data-id="${servico.id_servico}">Editar</button>
                <button class="botao-perigo" data-tipo="servico" data-acao="excluir" data-id="${servico.id_servico}">Excluir</button>
            </div>
        </div>
    `).join('') || '<p class="mensagem-vazia">Nenhum serviço cadastrado.</p>';
}

function renderizarListaAgendamentos(listaAgendamentos) {
    const container = document.getElementById('lista-agendamentos');
    container.innerHTML = (listaAgendamentos || []).map((agendamento) => `
        <div class="item">
            <h4>Agendamento #${agendamento.id_agendamento}</h4>
            <p><strong>Cliente:</strong> ${agendamento.id_cliente}</p>
            <p><strong>Funcionário:</strong> ${agendamento.id_funcionario}</p>
            <p><strong>Serviço:</strong> ${agendamento.id_servico}</p>
            <p><strong>Data:</strong> ${agendamento.data}</p>
            <p><strong>Hora:</strong> ${agendamento.hora}</p>
            <p><strong>Status:</strong> ${agendamento.status}</p>
            <div class="acoes">
                <button class="botao-secundario" data-tipo="agendamento" data-acao="editar" data-id="${agendamento.id_agendamento}">Editar</button>
                <button class="botao-perigo" data-tipo="agendamento" data-acao="excluir" data-id="${agendamento.id_agendamento}">Excluir</button>
            </div>
        </div>
    `).join('') || '<p class="mensagem-vazia">Nenhum agendamento cadastrado.</p>';
}

function renderizarListaProdutos(listaProdutos) {
    const container = document.getElementById('lista-produtos');
    container.innerHTML = (listaProdutos || []).map((produto) => `
        <div class="item">
            <h4>${produto.nome}</h4>
            <p><strong>Categoria:</strong> ${produto.categoria}</p>
            <p><strong>Quantidade:</strong> ${produto.quantidade}</p>
            <p><strong>Preço:</strong> ${formatarDinheiro(produto.preco)}</p>
            <div class="acoes">
                <button class="botao-secundario" data-tipo="produto" data-acao="editar" data-id="${produto.id_produto}">Editar</button>
                <button class="botao-perigo" data-tipo="produto" data-acao="excluir" data-id="${produto.id_produto}">Excluir</button>
            </div>
        </div>
    `).join('') || '<p class="mensagem-vazia">Nenhum produto cadastrado.</p>';
}

function renderizarListaPagamentos(listaPagamentos) {
    const container = document.getElementById('lista-pagamentos');
    container.innerHTML = (listaPagamentos || []).map((pagamento) => `
        <div class="item">
            <h4>Pagamento #${pagamento.id_pagamento}</h4>
            <p><strong>Agendamento:</strong> ${pagamento.id_agendamento}</p>
            <p><strong>Valor:</strong> ${formatarDinheiro(pagamento.valor)}</p>
            <p><strong>Forma:</strong> ${pagamento.forma_pagamento}</p>
            <p><strong>Data:</strong> ${pagamento.data_pagamento}</p>
            <div class="acoes">
                <button class="botao-secundario" data-tipo="pagamento" data-acao="editar" data-id="${pagamento.id_pagamento}">Editar</button>
                <button class="botao-perigo" data-tipo="pagamento" data-acao="excluir" data-id="${pagamento.id_pagamento}">Excluir</button>
            </div>
        </div>
    `).join('') || '<p class="mensagem-vazia">Nenhum pagamento registrado.</p>';
}

async function carregarDashboard() {
    try {
        const dados = await buscarDados('/api/dashboard');
        renderizarDashboard(dados);
    } catch (erro) {
        console.error(erro);
    }
}

async function carregarClientes() {
    try {
        const clientes = await buscarDados('/api/clientes');
        renderizarListaClientes(clientes);
    } catch (erro) {
        console.error(erro);
    }
}

async function carregarServicos() {
    try {
        const servicos = await buscarDados('/api/servicos');
        renderizarListaServicos(servicos);
    } catch (erro) {
        console.error(erro);
    }
}

async function carregarAgendamentos() {
    try {
        const agendamentos = await buscarDados('/api/agendamentos');
        renderizarListaAgendamentos(agendamentos);
    } catch (erro) {
        console.error(erro);
    }
}

async function carregarProdutos() {
    try {
        const produtos = await buscarDados('/api/produtos');
        renderizarListaProdutos(produtos);
    } catch (erro) {
        console.error(erro);
    }
}

async function carregarPagamentos() {
    try {
        const pagamentos = await buscarDados('/api/pagamentos');
        renderizarListaPagamentos(pagamentos);
    } catch (erro) {
        console.error(erro);
    }
}

function limparFormulario(formulario) {
    formulario.reset();
    const campoOculto = formulario.querySelector('input[type="hidden"]');
    if (campoOculto) {
        campoOculto.value = '';
    }
    formulario.dataset.modo = 'cadastro';
    formulario.classList.add('oculto');
}

function preencherFormulario(tipo, item) {
    const formulario = document.getElementById(`formulario-${tipo}`);
    if (!formulario) {
        return;
    }

    const campos = formulario.querySelectorAll('[name]');
    campos.forEach((campo) => {
        const valor = item?.[campo.name];
        campo.value = valor !== undefined && valor !== null ? valor : '';
    });

    const campoOculto = formulario.querySelector('input[type="hidden"]');
    if (campoOculto) {
        campoOculto.value = item?.[campoOculto.name] ?? '';
    }

    formulario.dataset.modo = 'edicao';
    formulario.classList.remove('oculto');
    formulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function inicializarFormulario(evento) {
    evento.preventDefault();

    const formulario = evento.currentTarget;
    const tipo = formulario.dataset.tipo;
    const campoId = formulario.dataset.chaveId;
    const dadosFormulario = Object.fromEntries(
        [...new FormData(formulario).entries()].filter(([nome]) => nome !== campoId)
    );
    const modoEdicao = formulario.dataset.modo === 'edicao';
    const campoOculto = formulario.querySelector('input[type="hidden"]');
    const id = campoOculto ? campoOculto.value : '';
    const url = modoEdicao ? `/api/${tipo}s/${id}` : `/api/${tipo}s`;
    const metodo = modoEdicao ? 'PUT' : 'POST';

    try {
        await enviarDados(url, metodo, dadosFormulario);
    } catch (erro) {
        window.alert(erro.message);
        return;
    }

    limparFormulario(formulario);
    carregarClientes();
    carregarServicos();
    carregarAgendamentos();
    carregarProdutos();
    carregarPagamentos();
    carregarDashboard();
}

function configurarBotoesFormulario() {
    document.getElementById('botao-novo-cliente')?.addEventListener('click', () => {
        const formulario = document.getElementById('formulario-cliente');
        limparFormulario(formulario);
        formulario.classList.remove('oculto');
    });

    document.getElementById('botao-novo-servico')?.addEventListener('click', () => {
        const formulario = document.getElementById('formulario-servico');
        limparFormulario(formulario);
        formulario.classList.remove('oculto');
    });

    document.getElementById('botao-novo-agendamento')?.addEventListener('click', () => {
        const formulario = document.getElementById('formulario-agendamento');
        limparFormulario(formulario);
        formulario.classList.remove('oculto');
    });

    document.getElementById('botao-novo-produto')?.addEventListener('click', () => {
        const formulario = document.getElementById('formulario-produto');
        limparFormulario(formulario);
        formulario.classList.remove('oculto');
    });

    document.getElementById('botao-novo-pagamento')?.addEventListener('click', () => {
        const formulario = document.getElementById('formulario-pagamento');
        limparFormulario(formulario);
        formulario.classList.remove('oculto');
    });
}

async function confirmarExclusao(url, tipo) {
    const resposta = window.confirm(`Deseja excluir este ${tipo}?`);
    if (!resposta) {
        return;
    }

    await fetch(url, { method: 'DELETE' });
    carregarClientes();
    carregarServicos();
    carregarAgendamentos();
    carregarProdutos();
    carregarPagamentos();
    carregarDashboard();
}

async function abrirEdicao(tipo, id) {
    const dados = await buscarDados(`/api/${tipo}s`);
    const identificador = `id_${tipo}`;
    const item = dados.find((elemento) => Number(elemento[identificador]) === Number(id));

    if (!item) {
        return;
    }

    preencherFormulario(tipo, item);
}

document.addEventListener('click', async (evento) => {
    const botao = evento.target.closest('button[data-acao]');

    if (!botao) {
        return;
    }

    const { tipo, acao, id } = botao.dataset;

    if (acao === 'excluir') {
        await confirmarExclusao(`/api/${tipo}s/${id}`, tipo);
        return;
    }

    if (acao === 'editar') {
        await abrirEdicao(tipo, id);
    }
});

botoesMenu.forEach((botao) => {
    botao.addEventListener('click', () => {
        const secao = botao.dataset.secao;
        mostrarSecao(secao);
        if (secao === 'dashboard') {
            carregarDashboard();
        }
        if (secao === 'clientes') {
            carregarClientes();
        }
        if (secao === 'servicos') {
            carregarServicos();
        }
        if (secao === 'agendamentos') {
            carregarAgendamentos();
        }
        if (secao === 'produtos') {
            carregarProdutos();
        }
        if (secao === 'pagamentos') {
            carregarPagamentos();
        }
    });
});

document.querySelector('.botao-principal[data-secao="agendamentos"]')?.addEventListener('click', () => {
    mostrarSecao('agendamentos');
    carregarAgendamentos();
});

document.getElementById('formulario-cliente')?.addEventListener('submit', inicializarFormulario);
document.getElementById('formulario-servico')?.addEventListener('submit', inicializarFormulario);
document.getElementById('formulario-agendamento')?.addEventListener('submit', inicializarFormulario);
document.getElementById('formulario-produto')?.addEventListener('submit', inicializarFormulario);
document.getElementById('formulario-pagamento')?.addEventListener('submit', inicializarFormulario);

configurarBotoesFormulario();
mostrarSecao('dashboard');
carregarDashboard();
carregarClientes();
carregarServicos();
carregarAgendamentos();
carregarProdutos();
carregarPagamentos();
