drop database if exists spa_salao;
create database spa_salao;
use spa_salao;
drop table if exists clientes;

create table clientes (
id_cliente int auto_increment primary key,
nome varchar (50),
telefone varchar(20),
email varchar(50),
endereco varchar(50),
aceitou_lgpd enum('sim','não') not null,
data_consentimento date not null 

);




create table funcionarios(
id_funcionario int auto_increment primary key,
nome varchar(50),
telefone varchar(20),
email varchar(50),
cargo varchar(50)

);
describe funcionarios;

create table servicos(
id_servico int auto_increment primary key,
nome varchar(50),
descricao varchar (100),
valor decimal (10,2),
duracao int

);
describe servicos;

CREATE TABLE agendamentos (
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
);
use spa_salao;
CREATE TABLE pagamentos (
    id_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    id_agendamento INT,
    valor DECIMAL(10,2),
    forma_pagamento VARCHAR(30),
    data_pagamento DATE,

    FOREIGN KEY (id_agendamento) REFERENCES agendamentos(id_agendamento)
);

CREATE TABLE produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    categoria VARCHAR(50),
    quantidade INT,
    preco DECIMAL(10,2)
);
#conferir tabelas


INSERT INTO clientes
(nome, telefone, email, endereco,aceitou_lgpd,data_consentimento )
VALUES
('myria','3592090','kakagh@gmail.com','contagem','sim', "2023-02-02"),
('Maria Silva', '11999999', 'maria@gmail.com', 'betim','não','2024-02-01'),
('Ana Souza', '11988888', 'ana@gmail.com', 'ibirite','sim','2025-05-01'),
('João Santos', '1197772', 'joao@gmail.com', 'belo horizonte','sim','2026-08-02'),
('Carla Oliveira', '11966666', 'carla@gmail.com', 'montes claro','não','2026-02-01');

select * from funcionarios;

INSERT INTO funcionarios (nome, telefone, email, cargo) VALUES
('Ana Souza', '11988881111', 'ana@gmail.com', 'Cabeleireira'),
('Carla Oliveira', '11988882222', 'carla@gmail.com', 'Manicure'),
('Juliana Santos', '11988883333', 'juliana@gmail.com', 'Esteticista'),
('Marcos Lima', '11988884444', 'marcos@gmail.com', 'Massagista'),
('Fernanda Alves', '11988885555', 'fernanda@gmail.com', 'Maquiadora');

INSERT INTO servicos (nome, descricao, valor, duracao) VALUES
('Corte Feminino', 'Corte e finalização dos cabelos', 80.00, 60),
('Manicure', 'Cuidados e esmaltação das unhas', 60.00, 45),
('Limpeza de Pele', 'Limpeza profunda do rosto', 100.00, 60),
('Massagem Relaxante', 'Massagem para relaxamento corporal', 120.00, 60),
('Maquiagem', 'Maquiagem social', 150.00, 90),
('Massagem terapeutica','massagem para relaxamento','120.00','60'),
('Massagem Com Pedras Quente','massagem relaxamento','200.00','60'),
('Drenagem Linfática','massagem','150.00','60'),
('Spa Pés e Mãos','cuidados','100.00','60'),
('Aromaterapia','cuidados','80.00','30');

INSERT INTO agendamentos
(id_cliente, id_funcionario, id_servico, data, hora, status) VALUES
(1, 1, 1, '2026-08-15', '09:00:00', 'Agendado'),
(2, 2, 2, '2026-08-15', '10:00:00', 'Agendado'),
(3, 3, 3, '2026-08-16', '13:00:00', 'Confirmado'),
(4, 4, 4, '2026-08-16', '15:00:00', 'Agendado'),
(5, 5, 5, '2026-08-17', '14:00:00', 'Confirmado');

INSERT INTO pagamentos
(id_agendamento, valor, forma_pagamento, data_pagamento) VALUES
(1, 80.00, 'Pix', '2026-08-15'),
(2, 40.00, 'Cartao', '2026-08-15'),
(3, 100.00, 'Dinheiro', '2026-08-16'),
(4, 120.00, 'Pix', '2026-08-16'),
(5, 150.00, 'Cartao', '2026-08-17');

INSERT INTO produtos
(nome, categoria, quantidade, preco) VALUES
('Shampoo Profissional', 'Cabelo', 30, 35.00),
('Condicionador Profissional', 'Cabelo', 30, 40.00),
('Esmalte Vermelho', 'Unhas', 30, 12.00),
('Creme Facial', 'Estetica', 30, 55.00),
('Mascara Facial', 'Estetica', 30, 45.00),
('Oleo Massagem','Cuidados','30','40.00'),
('Loções De Massagem','Cuidados','35','35.00'),
('Velas de Massagem','Estetica','40','50.00'),
('Esfoliantes Corporal','Cuidados','30','30.00'),
('Toalhas Quentes','Cuidados','30','25.00'),
('Pedras Quente','cuidados','30','80.00'),
('Aromatizador','estetica','30','40.00'),
('Hidratante corporal','Cuidados','30','30.00');

select * from  servicos;
