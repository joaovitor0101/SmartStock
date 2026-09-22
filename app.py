"""
====================================================================
SMARTSTOCK V1 - SISTEMA SIMPLES DE GESTÃO DE ESTOQUE COM FEFO
Código limpo e didático feito em Python + Flask para iniciantes.
====================================================================
"""
import sqlite3
from datetime import datetime, date
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "smartstock-v1-chave-secreta"

# Caminhos do banco de dados e do schema SQL
PASTA_BANCO = Path(__file__).resolve().parent / "database"
ARQUIVO_BANCO = PASTA_BANCO / "smartstock.db"
ARQUIVO_SCHEMA = PASTA_BANCO / "schema.sql"

def conectar_banco():
    """Conecta ao banco de dados SQLite e permite acessar colunas pelo nome."""
    conn = sqlite3.connect(str(ARQUIVO_BANCO))
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    """Cria as tabelas e adiciona alguns produtos de teste se o banco for novo."""
    PASTA_BANCO.mkdir(exist_ok=True)
    with conectar_banco() as conn:
        with open(ARQUIVO_SCHEMA, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        
        # Se a tabela de produtos estiver vazia, insere alguns dados de exemplo
        produtos_existentes = conn.execute("SELECT COUNT(*) as total FROM produtos").fetchone()["total"]
        if produtos_existentes == 0:
            # 1. Produtos de teste
            conn.execute("INSERT INTO produtos (id, nome, preco, estoque_minimo) VALUES (1, 'Iogurte Natural 500g', 8.00, 10)")
            conn.execute("INSERT INTO produtos (id, nome, preco, estoque_minimo) VALUES (2, 'Whey Protein 900g', 120.00, 5)")
            conn.execute("INSERT INTO produtos (id, nome, preco, estoque_minimo) VALUES (3, 'Suco de Uva 1L', 12.00, 15)")

            # 2. Lotes de teste (com datas dinâmicas para testar FEFO, desconto e bloqueio)
            # Iogurte: Lote 1 vence em 4 dias (Desconto de 30% - FEFO escolhe este primeiro!)
            conn.execute("INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (1, 'LT-IOG-01', date('now', '+4 days'), 8)")
            # Iogurte: Lote 2 vence em 25 dias (Desconto de 10%)
            conn.execute("INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (1, 'LT-IOG-02', date('now', '+25 days'), 15)")
            
            # Whey: Vence em 60 dias (Preço normal)
            conn.execute("INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (2, 'LT-WHEY-10', date('now', '+60 days'), 10)")
            
            # Suco: Lote VENCIDO há 2 dias (Bloqueado para venda!)
            conn.execute("INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (3, 'LT-SUCO-VENC', date('now', '-2 days'), 6)")
            # Suco: Lote Válido
            conn.execute("INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (3, 'LT-SUCO-OK', date('now', '+20 days'), 4)")

            conn.commit()

# ====================================================================
# LÓGICA DE NEGÓCIO: VALIDADE, DESCONTOS E FEFO
# ====================================================================

def calcular_validade_e_desconto(data_validade_str, preco_base):
    """
    Calcula quantos dias faltam para o vencimento e aplica o desconto automático:
    - Vencido (< 0 dias): Bloqueia a venda.
    - Menos de 7 dias: 30% de desconto.
    - De 7 a 14 dias: 20% de desconto.
    - De 15 a 30 dias: 10% de desconto.
    - Mais de 30 dias: Sem desconto (Preço normal).
    """
    data_val = datetime.strptime(str(data_validade_str).strip(), "%Y-%m-%d").date()
    dias_restantes = (data_val - date.today()).days

    if dias_restantes < 0:
        return {
            "dias": dias_restantes,
            "status": "Vencido (Bloqueado)",
            "cor": "vermelho",
            "pode_vender": False,
            "desconto": 0,
            "preco_final": preco_base
        }
    elif dias_restantes <= 6:
        desconto = 30.0
        cor = "laranja"
        status = f"Crítico ({dias_restantes}d) - 30% OFF"
    elif dias_restantes <= 14:
        desconto = 20.0
        cor = "amarelo"
        status = f"Atenção ({dias_restantes}d) - 20% OFF"
    elif dias_restantes <= 30:
        desconto = 10.0
        cor = "azul"
        status = f"Promoção ({dias_restantes}d) - 10% OFF"
    else:
        desconto = 0.0
        cor = "verde"
        status = f"No Prazo ({dias_restantes}d)"

    preco_final = round(preco_base * (1.0 - (desconto / 100.0)), 2)
    return {
        "dias": dias_restantes,
        "status": status,
        "cor": cor,
        "pode_vender": True,
        "desconto": desconto,
        "preco_final": preco_final
    }

# ====================================================================
# ROTAS DA APLICAÇÃO WEB
# ====================================================================

@app.route("/")
def index():
    """Página inicial simples: lista produtos, lotes com FEFO e últimas vendas."""
    with conectar_banco() as conn:
        # 1. Carrega produtos e calcula estoque total
        produtos_db = conn.execute("SELECT * FROM produtos ORDER BY nome ASC").fetchall()
        produtos = []
        for p in produtos_db:
            # Soma unidades dos lotes deste produto
            soma_qtd = conn.execute("""
                SELECT COALESCE(SUM(quantidade), 0) as total 
                FROM lotes WHERE produto_id = ? AND data_validade >= date('now')
            """, (p["id"],)).fetchone()["total"]
            
            p_dict = dict(p)
            p_dict["estoque_atual"] = soma_qtd
            p_dict["precisa_repor"] = soma_qtd <= p["estoque_minimo"]
            produtos.append(p_dict)

        # 2. Carrega todos os lotes com informações de validade e desconto
        lotes_db = conn.execute("""
            SELECT l.*, p.nome as produto_nome, p.preco as preco_base
            FROM lotes l
            JOIN produtos p ON l.produto_id = p.id
            ORDER BY l.data_validade ASC
        """).fetchall()

        lotes = []
        for l in lotes_db:
            l_dict = dict(l)
            info = calcular_validade_e_desconto(l["data_validade"], l["preco_base"])
            l_dict.update(info)
            lotes.append(l_dict)

        # 3. Carrega últimas vendas
        vendas = conn.execute("""
            SELECT v.*, p.nome as produto_nome, l.numero_lote
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            JOIN lotes l ON v.lote_id = l.id
            ORDER BY v.data_venda DESC LIMIT 10
        """).fetchall()

    return render_template("index.html", produtos=produtos, lotes=lotes, vendas=vendas)

@app.route("/cadastrar_produto", methods=["POST"])
def cadastrar_produto():
    """Cadastra um novo produto."""
    nome = request.form.get("nome")
    preco = float(request.form.get("preco", 0))
    estoque_minimo = int(request.form.get("estoque_minimo", 5))

    with conectar_banco() as conn:
        conn.execute(
            "INSERT INTO produtos (nome, preco, estoque_minimo) VALUES (?, ?, ?)",
            (nome, preco, estoque_minimo)
        )
        conn.commit()

    flash(f"Produto '{nome}' cadastrado com sucesso!", "sucesso")
    return redirect(url_for("index"))

@app.route("/cadastrar_lote", methods=["POST"])
def cadastrar_lote():
    """Adiciona um lote novo para um produto."""
    produto_id = int(request.form.get("produto_id"))
    numero_lote = request.form.get("numero_lote")
    data_validade = request.form.get("data_validade")
    quantidade = int(request.form.get("quantidade", 0))

    with conectar_banco() as conn:
        conn.execute(
            "INSERT INTO lotes (produto_id, numero_lote, data_validade, quantidade) VALUES (?, ?, ?, ?)",
            (produto_id, numero_lote, data_validade, quantidade)
        )
        conn.commit()

    flash(f"Lote '{numero_lote}' cadastrado com sucesso!", "sucesso")
    return redirect(url_for("index"))

@app.route("/vender", methods=["POST"])
def vender():
    """
    Realiza a venda aplicando o algoritmo FEFO:
    1. Busca os lotes válidos ordenados pela validade mais próxima.
    2. Ignora e bloqueia qualquer lote vencido.
    3. Abate a quantidade dos lotes que vencem primeiro.
    """
    produto_id = int(request.form.get("produto_id"))
    quantidade_desejada = int(request.form.get("quantidade", 1))

    with conectar_banco() as conn:
        # Busca o produto
        produto = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("index"))

        # ALGORITMO FEFO:
        # Pega somente lotes com data_validade >= hoje e quantidade > 0, ordenados pela validade mais antiga primeiro!
        lotes_validos = conn.execute("""
            SELECT * FROM lotes 
            WHERE produto_id = ? AND data_validade >= date('now') AND quantidade > 0
            ORDER BY data_validade ASC
        """, (produto_id,)).fetchall()

        total_disponivel = sum(l["quantidade"] for l in lotes_validos)
        if total_disponivel < quantidade_desejada:
            flash(f"Estoque insuficiente no prazo! Disponível para venda: {total_disponivel} un. (Lotes vencidos são bloqueados)", "erro")
            return redirect(url_for("index"))

        # Executa a saída FEFO
        qtd_restante = quantidade_desejada
        lotes_utilizados = []
        valor_total_pago = 0.0

        for lote in lotes_validos:
            if qtd_restante <= 0:
                break
            
            # Pega o que puder deste lote
            qtd_deste_lote = min(lote["quantidade"], qtd_restante)
            info = calcular_validade_e_desconto(lote["data_validade"], produto["preco"])
            valor_final_unitario = info["preco_final"]
            subtotal = round(qtd_deste_lote * valor_final_unitario, 2)
            valor_total_pago += subtotal

            # Atualiza a quantidade restante no lote
            conn.execute(
                "UPDATE lotes SET quantidade = quantidade - ? WHERE id = ?",
                (qtd_deste_lote, lote["id"])
            )

            # Registra a venda
            conn.execute("""
                INSERT INTO vendas (produto_id, lote_id, quantidade, valor_pago, desconto_aplicado)
                VALUES (?, ?, ?, ?, ?)
            """, (produto_id, lote["id"], qtd_deste_lote, subtotal, info["desconto"]))

            lotes_utilizados.append(f"{qtd_deste_lote} un do Lote {lote['numero_lote']} (-{info['desconto']}% desc)")
            qtd_restante -= qtd_deste_lote

        conn.commit()

    flash(f"Venda FEFO concluída com sucesso! Total: R$ {valor_total_pago:.2f}. Saída: {', '.join(lotes_utilizados)}", "sucesso")
    return redirect(url_for("index"))

if __name__ == "__main__":
    inicializar_banco()
    print("[*] SmartStock V1 (Modo Simples) iniciado!")
    print("[*] Abra seu navegador em: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
