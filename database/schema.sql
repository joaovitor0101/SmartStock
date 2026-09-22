-- ====================================================================
-- SMARTSTOCK V1 - SCHEMA SIMPLIFICADO DO BANCO DE DADOS (SQL)
-- Apenas 3 tabelas fundamentais para facilitar o aprendizado!
-- ====================================================================

-- 1. TABELA DE PRODUTOS
-- Guarda os dados principais de cada produto vendido.
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque_minimo INTEGER NOT NULL DEFAULT 5
);

-- 2. TABELA DE LOTES
-- Permite que um mesmo produto tenha vários lotes com validades diferentes.
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    numero_lote TEXT NOT NULL,
    data_validade DATE NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

-- 3. TABELA DE VENDAS
-- Guarda o histórico de vendas realizadas pelo método FEFO.
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    lote_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    valor_pago REAL NOT NULL,
    desconto_aplicado REAL NOT NULL,
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos (id),
    FOREIGN KEY (lote_id) REFERENCES lotes (id)
);
