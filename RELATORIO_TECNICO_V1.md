# Relatório Técnico - SmartStock (Versão 1.0)

**Projeto:** Sistema Inteligente de Gestão de Estoque com Validade e FEFO  
**Versão:** 1.0 (V1 - Entrega Inicial Simples)  
**Disciplina / Contexto:** Projeto de Programação e Banco de Dados  

---

## 1. Introdução e Objetivo

O **SmartStock** é um sistema simples desenvolvido para resolver um problema comum no comércio: o controle de produtos que possuem prazo de validade (como alimentos, laticínios, suplementos e remédios).

Quando um estabelecimento não controla bem as validades:
- Produtos vencem nas prateleiras gerando prejuízo financeiro.
- O cliente pode comprar um item vencido por engano.
- Produtos que estão perto de vencer poderiam ser vendidos com desconto, mas acabam sendo jogados fora.

O objetivo desta **Versão 1 (V1)** é entregar uma base inicial funcional e fácil de entender, focando apenas no essencial para irmos aprimorando nas próximas versões.

---

## 2. O que foi Feito na V1 (Escopo Simples)

Para manter o projeto simples e didático, implementamos apenas as seguintes funções na V1:

1. **Cadastro e Listagem de Produtos:** Nome do produto, código SKU, categoria, preço e estoque mínimo.
2. **Controle Individual por Lotes:** Um mesmo produto pode ter vários lotes, cada um com sua data de validade e quantidade.
3. **Regra FEFO (*First Expire, First Out*):** Na hora da venda, o sistema escolhe automaticamente o lote que vai vencer primeiro, evitando que mercadorias fiquem esquecidas no estoque.
4. **Descontos Automáticos por Validade:** Se o lote estiver próximo do vencimento, o sistema calcula um desconto promocional automaticamente:
   - Mais de 30 dias para vencer: Preço normal (0% de desconto).
   - De 15 a 30 dias: 10% de desconto.
   - De 7 a 14 dias: 20% de desconto.
   - Menos de 7 dias: 30% de desconto.
5. **Bloqueio de Produtos Vencidos:** Se a data de validade já passou, o sistema proíbe a venda do lote e permite registrá-lo apenas como perda/descarte.
6. **Alerta de Estoque Mínimo:** Avisa quando a quantidade de um produto está abaixo do limite mínimo para reposição.

---

## 3. Schema Completo do Banco de Dados (SQL)

Abaixo está o script SQL completo utilizado no projeto. Ele cria 6 tabelas relacionais simples com chaves primárias (`PRIMARY KEY`) e chaves estrangeiras (`FOREIGN KEY`):

```sql
-- ====================================================================
-- SISTEMA DE GESTÃO DE ESTOQUE INTELIGENTE (SMARTSTOCK V1)
-- Schema do Banco de Dados Relacional (SQL)
-- ====================================================================

-- 1. TABELA DE CATEGORIAS
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA DE FORNECEDORES
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(150) NOT NULL,
    cnpj VARCHAR(20) UNIQUE,
    contato VARCHAR(100),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABELA DE PRODUTOS
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_sku VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL,
    categoria_id INTEGER NOT NULL,
    fornecedor_id INTEGER,
    fabricante VARCHAR(100),
    unidade_medida VARCHAR(20) NOT NULL DEFAULT 'UN',
    preco_custo_padrao DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    preco_venda_padrao DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    estoque_minimo INTEGER NOT NULL DEFAULT 10,
    estoque_maximo INTEGER NOT NULL DEFAULT 100,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
);

-- 4. TABELA DE LOTES (Controle individual da data de validade)
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    numero_lote VARCHAR(50) NOT NULL,
    data_validade DATE NOT NULL,
    quantidade_inicial INTEGER NOT NULL CHECK (quantidade_inicial >= 0),
    quantidade_atual INTEGER NOT NULL CHECK (quantidade_atual >= 0),
    preco_custo DECIMAL(10, 2) NOT NULL,
    data_entrada DATE NOT NULL,
    numero_nf VARCHAR(50),
    status VARCHAR(30) NOT NULL DEFAULT 'ATIVO', -- 'ATIVO', 'ESGOTADO', 'DESCARTADO'
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

-- 5. TABELA DE REGRAS DE DESCONTO POR VALIDADE
CREATE TABLE IF NOT EXISTS regras_desconto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dias_min INTEGER NOT NULL,
    dias_max INTEGER NOT NULL,
    percentual_desconto DECIMAL(5, 2) NOT NULL,
    descricao VARCHAR(100),
    ativo INTEGER NOT NULL DEFAULT 1
);

-- 6. TABELA DE MOVIMENTAÇÕES (Histórico de Entradas, Vendas e Perdas)
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo VARCHAR(30) NOT NULL, -- 'ENTRADA', 'VENDA_FEFO', 'PERDA'
    produto_id INTEGER NOT NULL,
    lote_id INTEGER,
    quantidade INTEGER NOT NULL,
    valor_unitario_base DECIMAL(10, 2) DEFAULT 0.00,
    desconto_percentual DECIMAL(5, 2) DEFAULT 0.00,
    valor_unitario_final DECIMAL(10, 2) DEFAULT 0.00,
    valor_total DECIMAL(10, 2) DEFAULT 0.00,
    motivo_perda VARCHAR(50),  -- 'VENCIDO', 'DANIFICADO', 'EXTRAVIADO', 'DESCARTADO'
    observacao TEXT,
    data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

-- Índices para deixar as buscas mais rápidas
CREATE INDEX IF NOT EXISTS idx_lotes_validade ON lotes (produto_id, data_validade, quantidade_atual);
CREATE INDEX IF NOT EXISTS idx_produtos_sku ON produtos (codigo_sku);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes (data_movimentacao);
```

---

## 4. Como a Lógica Funciona (Lógica em Python)

A lógica do sistema foi escrita em Python de maneira direta:

1. **Cálculo de Dias Restantes:**  
   O sistema subtrai a data de validade do lote pela data de hoje:  
   $$\text{dias} = \text{data\_validade} - \text{hoje}$$
   - Se for menor que 0: o lote é marcado como **VENCIDO** e a venda é travada.
   - Se for maior ou igual a 0: o sistema verifica se cai em alguma regra de desconto promocional.

2. **Como Funciona o FEFO na Venda:**  
   Quando o usuário solicita a venda de $X$ unidades de um produto:
   - O sistema busca os lotes com quantidade disponível que não estejam vencidos.
   - Ordena os lotes pela data de validade mais próxima (**quem vence antes sai primeiro**).
   - Se o primeiro lote não tiver unidades suficientes, o sistema consome o restante do próximo lote da fila.
   - Calcula o valor total e o desconto de cada lote e dá baixa no estoque.

3. **Alerta de Estoque Mínimo:**  
   Soma todas as unidades válidas do produto. Se a quantidade total for menor ou igual ao estoque mínimo definido, a tela exibe um aviso amarelo recomendando comprar mais mercadoria.

---

## 5. Como Executar o Projeto

Para rodar o projeto localmente:

1. **Instalar dependências (apenas Flask):**
   ```powershell
   py -m pip install -r requirements.txt
   ```

2. **Iniciar o servidor:**
   ```powershell
   py app.py
   ```

3. **Acessar no navegador:**
   Abra: `http://127.0.0.1:5000`

O banco de dados SQLite já é criado e preenchido automaticamente com produtos e lotes de teste na primeira vez que você inicia o programa.

---

## 6. Próximos Upgrades Planejados (Para as Próximas Versões)

Como esta é a versão V1 (início dos estudos), deixamos as seguintes melhorias para os próximos passos:
- **Upgrades da V2:** Sistema de login com níveis de acesso (Admin, Vendedor, Estoquista).
- **Upgrades da V3:** Módulo de compras com cálculo automático da quantidade a pedir ao fornecedor.
- **Upgrades da V4:** Relatórios com gráficos (mais vendidos, curva de perdas) e exportação em PDF e Excel.
- **Upgrades da V5:** Descontos combinados por quantidade comprada no atacado.

---

## 7. Conclusão

A V1 do **SmartStock** entrega com sucesso o que foi proposto no mini-mundo: o controle inteligente de estoque com foco em datas de validade, aplicação prática do FEFO e descontos para reduzir desperdício, mantendo o código simples, limpo e pronto para novos aperfeiçoamentos.
