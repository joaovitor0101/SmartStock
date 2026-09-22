-- ====================================================================
-- SMARTSTOCK V1 - SCRIPT DE DADOS INICIAIS (SEED)
-- Utiliza datas dinâmicas do SQLite (date('now', ...)) para que
-- as regras de FEFO e descontos funcionem perfeitamente em qualquer momento!
-- ====================================================================

-- Categorias
INSERT OR IGNORE INTO categorias (id, nome, descricao) VALUES
(1, 'Laticínios', 'Iogurtes, queijos frescos, leites pasteurizados e derivados'),
(2, 'Suplementos', 'Proteínas, aminoácidos, creatinas e vitaminas'),
(3, 'Farmácia e Medicamentos', 'Analgésicos, colírios, xaropes e primeiros socorros'),
(4, 'Bebidas e Sucos', 'Sucos naturais, refrigerantes e chás gelados');

-- Fornecedores
INSERT OR IGNORE INTO fornecedores (id, nome, cnpj, contato) VALUES
(1, 'Laticínios do Vale Ltda', '12.345.678/0001-90', 'vendas@laticiniosdovale.com.br'),
(2, 'NutriMax Distribuidora', '98.765.432/0001-10', 'contato@nutrimax.com.br'),
(3, 'PharmaClean Suprimentos', '45.123.789/0001-55', 'suporte@pharmaclean.com.br');

-- Regras de Desconto por Validade (Conforme Mini-Mundo)
-- > 30 dias: preço normal (0% desconto)
-- 15 a 30 dias: 10% de desconto
-- 7 a 14 dias: 20% de desconto
-- 1 a 6 dias: 30% de desconto
INSERT OR IGNORE INTO regras_desconto (id, dias_min, dias_max, percentual_desconto, descricao, ativo) VALUES
(1, 15, 30, 10.0, 'Desconto Amarelo: 15 a 30 dias para vencer', 1),
(2, 7, 14, 20.0, 'Desconto Laranja: 7 a 14 dias para vencer', 1),
(3, 1, 6, 30.0, 'Desconto Crítico: menos de 7 dias para vencer', 1);

-- Produtos Base
-- Produto 1: Iogurte Natural 500g (Estoque Mínimo: 15)
INSERT OR IGNORE INTO produtos (id, codigo_sku, nome, categoria_id, fornecedor_id, fabricante, unidade_medida, preco_custo_padrao, preco_venda_padrao, estoque_minimo, estoque_maximo) VALUES
(1, 'LAT-001', 'Iogurte Natural Integral 500g', 1, 1, 'Vale Lácteo', 'UN', 4.50, 8.90, 15, 100),
-- Produto 2: Whey Protein 900g Baunilha (Estoque Mínimo: 8)
(2, 'SUP-002', 'Whey Protein Isolado 900g Baunilha', 2, 2, 'NutriMax Lab', 'UN', 85.00, 159.90, 8, 50),
-- Produto 3: Suco de Laranja Integral 1L (Estoque Mínimo: 20)
(3, 'BEB-003', 'Suco de Laranja Integral Pasteurizado 1L', 4, 1, 'Pomar Fresco', 'UN', 6.00, 12.50, 20, 80),
-- Produto 4: Vitamina C Efervescente 10 comp (Estoque Mínimo: 10)
(4, 'FAR-004', 'Vitamina C 1g Efervescente 10c', 3, 3, 'BioPharma', 'UN', 7.20, 16.00, 10, 60);

-- Lotes com diferentes validades para testar o FEFO e os descontos automáticos!
-- Lotes do Iogurte (Produto 1):
-- Lote A: Vence em 4 dias (Desconto Crítico 30%) - O FEFO DEVE ESCOLHER ESTE PRIMEIRO!
INSERT OR IGNORE INTO lotes (id, produto_id, numero_lote, data_validade, quantidade_inicial, quantidade_atual, preco_custo, data_entrada, numero_nf, status) VALUES
(1, 1, 'LT-IOG-01A', date('now', '+4 days'), 20, 12, 4.50, date('now', '-10 days'), 'NF-10291', 'ATIVO'),
-- Lote B: Vence em 22 dias (Desconto Amarelo 10%)
(2, 1, 'LT-IOG-01B', date('now', '+22 days'), 30, 25, 4.50, date('now', '-3 days'), 'NF-10440', 'ATIVO'),
-- Lote C: Vence em 60 dias (Preço Normal 0%)
(3, 1, 'LT-IOG-01C', date('now', '+60 days'), 40, 40, 4.50, date('now', '-1 days'), 'NF-10512', 'ATIVO');

-- Lotes do Whey Protein (Produto 2):
-- Lote A: Vence em 10 dias (Desconto Laranja 20%)
INSERT OR IGNORE INTO lotes (id, produto_id, numero_lote, data_validade, quantidade_inicial, quantidade_atual, preco_custo, data_entrada, numero_nf, status) VALUES
(4, 2, 'LT-WHEY-21', date('now', '+10 days'), 10, 6, 85.00, date('now', '-40 days'), 'NF-08812', 'ATIVO'),
-- Lote B: Vence em 180 dias (Normal)
(5, 2, 'LT-WHEY-22', date('now', '+180 days'), 15, 15, 85.00, date('now', '-5 days'), 'NF-10499', 'ATIVO');

-- Lotes do Suco de Laranja (Produto 3) - Teste de LOTE VENCIDO (deve ser bloqueado para venda!)
INSERT OR IGNORE INTO lotes (id, produto_id, numero_lote, data_validade, quantidade_inicial, quantidade_atual, preco_custo, data_entrada, numero_nf, status) VALUES
(6, 3, 'LT-SUCO-VENC', date('now', '-2 days'), 15, 8, 6.00, date('now', '-30 days'), 'NF-07711', 'ATIVO'),
-- Lote Válido do Suco: Vence em 25 dias (Desconto 10%)
(7, 3, 'LT-SUCO-B', date('now', '+25 days'), 20, 10, 6.00, date('now', '-2 days'), 'NF-10520', 'ATIVO');

-- Produto 4 (Vitamina C) - Teste de ESTOQUE BAIXO:
-- Quantidade total (4) < Estoque Mínimo (10) -> Dispara Alerta de Reposição!
INSERT OR IGNORE INTO lotes (id, produto_id, numero_lote, data_validade, quantidade_inicial, quantidade_atual, preco_custo, data_entrada, numero_nf, status) VALUES
(8, 4, 'LT-VITC-99', date('now', '+90 days'), 10, 4, 7.20, date('now', '-15 days'), 'NF-09923', 'ATIVO');

-- Movimentações Iniciais de Amostra
INSERT OR IGNORE INTO movimentacoes (id, tipo, produto_id, lote_id, quantidade, valor_unitario_base, desconto_percentual, valor_unitario_final, valor_total, observacao) VALUES
(1, 'ENTRADA', 1, 1, 20, 4.50, 0, 4.50, 90.00, 'Entrada de lote inicial'),
(2, 'ENTRADA', 1, 2, 30, 4.50, 0, 4.50, 135.00, 'Entrada de lote inicial'),
(3, 'VENDA_FEFO', 1, 1, 8, 8.90, 30.0, 6.23, 49.84, 'Venda teste com desconto FEFO');
