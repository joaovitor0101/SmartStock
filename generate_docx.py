"""
Script para gerar o Relatório Técnico da V1 Simplificada em formato Word (.docx)
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from pathlib import Path

def set_cell_background(cell, fill_hex):
    """Define a cor de fundo de uma célula."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Ajusta o padding interno da célula."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def build_docx():
    doc = docx.Document()

    # Configuração de Margens
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    COLOR_PRIMARY = RGBColor(14, 116, 144)   # Azul petróleo moderno
    COLOR_SECONDARY = RGBColor(71, 85, 105)  # Cinza elegante

    # TÍTULO
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title.add_run("Relatório Técnico - SmartStock (V1)")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub.add_run("Sistema Inteligente de Gestão de Estoque com Validade & FEFO\nEntrega Inicial Simples (Versão 1.0)")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_SECONDARY

    doc.add_paragraph()

    # Metadados
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = True
    
    meta_data = [
        ("Projeto:", "SmartStock - Gestão de Perecíveis", "Versão:", "1.0 (V1 Simplificada)"),
        ("Tecnologias:", "Python 3.12, SQLite, HTML5, CSS3", "Status:", "Funcional e Pronto para Uso")
    ]
    for row_idx, data in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        row.cells[0].paragraphs[0].add_run(f"{data[0]} ").bold = True
        row.cells[0].paragraphs[0].add_run(data[1])
        row.cells[1].paragraphs[0].add_run(f"{data[2]} ").bold = True
        row.cells[1].paragraphs[0].add_run(data[3])
        for c in row.cells:
            set_cell_background(c, "F1F5F9")
            set_cell_margins(c, top=80, bottom=80, left=120, right=120)

    doc.add_paragraph()

    def add_section_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        return h

    # 1. INTRODUÇÃO
    add_section_heading("1. Introdução e Objetivo")
    doc.add_paragraph(
        "O SmartStock é um sistema desenvolvido para resolver um problema comum em supermercados, "
        "farmácias e lojas de alimentos: o controle de produtos que possuem prazo de validade."
    )
    doc.add_paragraph("Quando um comércio não realiza esse controle de maneira individual por lote:", style='List Bullet')
    doc.add_paragraph("Produtos vencem nas prateleiras gerando perda financeira direta.", style='List Bullet 2')
    doc.add_paragraph("Clientes correm o risco de adquirir itens fora da validade.", style='List Bullet 2')
    doc.add_paragraph("Mercadorias próximas de vencer poderiam ser vendidas em promoção com desconto, mas acabam sendo descartadas.", style='List Bullet 2')
    doc.add_paragraph(
        "O objetivo desta Versão 1 (V1) é entregar uma solução simples, didática e funcional, focando apenas "
        "nas regras essenciais para que o sistema possa ser aperfeiçoado gradualmente nas próximas etapas."
    )

    # 2. O QUE FOI FEITO NA V1
    add_section_heading("2. O que foi Feito na V1 (Escopo Simples)")
    doc.add_paragraph("Para manter o projeto leve e fácil de entender para quem está começando na programação, implementamos:")

    itens_v1 = [
        ("Cadastro e Listagem de Produtos: ", "Controle de nome, preço e limite de estoque mínimo."),
        ("Controle Individual por Lotes: ", "Um mesmo produto pode ter múltiplos lotes, cada um com sua quantidade e data de validade."),
        ("Saída Inteligente FEFO (First Expire, First Out): ", "Ao realizar uma venda, o sistema busca e consome automaticamente o lote que vai vencer primeiro."),
        ("Descontos Automáticos por Validade: ", "Calcula desconto automático conforme os dias restantes (>30d: 0%, 15-30d: 10%, 7-14d: 20%, <7d: 30%)."),
        ("Bloqueio de Produtos Vencidos: ", "Impede a venda caso a data de validade do lote já tenha passado."),
        ("Alerta de Reposição de Estoque: ", "Avisa quando o estoque total do produto atinge ou fica abaixo do estoque mínimo.")
    ]
    for tit, desc in itens_v1:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(tit).bold = True
        p.add_run(desc)

    # 3. SCHEMA COMPLETO DO BANCO DE DADOS (SQL)
    add_section_heading("3. Schema Completo do Banco de Dados (SQL)")
    doc.add_paragraph(
        "O banco de dados foi estruturado em SQL simples e relacional com apenas 3 tabelas fundamentais "
        "ligadas por chaves estrangeiras (FOREIGN KEY):"
    )

    schema_sql = """-- ====================================================================
-- SMARTSTOCK V1 - SCHEMA DO BANCO DE DADOS (SQL)
-- Apenas 3 tabelas essenciais para o mini-mundo:
-- ====================================================================

-- 1. TABELA DE PRODUTOS
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque_minimo INTEGER NOT NULL DEFAULT 5
);

-- 2. TABELA DE LOTES (Controle de Validade por Lote)
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    numero_lote TEXT NOT NULL,
    data_validade DATE NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

-- 3. TABELA DE VENDAS (Histórico de Saídas FEFO)
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
);"""

    tbl_code = doc.add_table(rows=1, cols=1)
    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_code = tbl_code.rows[0].cells[0]
    set_cell_background(c_code, "F8FAFC")
    set_cell_margins(c_code, top=140, bottom=140, left=180, right=180)

    p_code = c_code.paragraphs[0]
    p_code.paragraph_format.line_spacing = 1.0
    r_code = p_code.add_run(schema_sql)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph()

    # 4. COMO A LÓGICA FUNCIONA
    add_section_heading("4. Como a Lógica Funciona (Python)")
    doc.add_paragraph("A inteligência do sistema foi escrita em um único arquivo (app.py) de forma direta e comentada:")

    doc.add_paragraph("1. Cálculo de Dias: Subtrai a data de validade pela data de hoje. Se for menor que 0, bloqueia a venda. Se for entre 1 e 30 dias, calcula o novo preço com o desconto correspondente.", style='List Bullet')
    doc.add_paragraph("2. Algoritmo FEFO: Executa um comando SQL ordenando os lotes por data de validade mais próxima (ORDER BY data_validade ASC) e consome os itens desse lote mais antigo primeiro.", style='List Bullet')
    doc.add_paragraph("3. Alerta de Reposição: Compara a quantidade total disponível com o estoque mínimo. Se for menor ou igual, exibe o alerta amarelo na tela.", style='List Bullet')

    # 5. COMO EXECUTAR
    add_section_heading("5. Como Executar o Projeto")
    doc.add_paragraph("Para rodar o projeto localmente com apenas 2 passos:")
    doc.add_paragraph("1. Iniciar o servidor no terminal: py app.py", style='List Number')
    doc.add_paragraph("2. Acessar no navegador: http://127.0.0.1:5000", style='List Number')
    doc.add_paragraph("O banco de dados SQLite é gerado automaticamente na primeira execução com produtos de teste.")

    # 6. PRÓXIMOS PASSOS
    add_section_heading("6. Próximos Upgrades Planejados (Para as Próximas Versões)")
    doc.add_paragraph("Como a V1 foi mantida simples e direta, os recursos avançados ficaram organizados para as próximas versões:")
    doc.add_paragraph("V2: Sistema de login com usuários e senhas (permissões de administrador e vendedor).", style='List Bullet')
    doc.add_paragraph("V3: Cadastro de fornecedores externos e cálculo automático de sugestão de compras.", style='List Bullet')
    doc.add_paragraph("V4: Relatórios gerenciais com gráficos de vendas e exportação em PDF e Excel.", style='List Bullet')

    # 7. CONCLUSÃO
    add_section_heading("7. Conclusão")
    doc.add_paragraph(
        "A V1 do SmartStock entrega o núcleo funcional solicitado para o mini-mundo: foco em validade, "
        "saída FEFO e descontos inteligentes para evitar desperdício, mantendo o código conciso, limpo e didático."
    )

    output_path = Path(__file__).resolve().parent / "RELATORIO_TECNICO_V1.docx"
    doc.save(str(output_path))
    print(f"[+] Relatório Word gerado com sucesso em: {output_path}")

if __name__ == "__main__":
    build_docx()
