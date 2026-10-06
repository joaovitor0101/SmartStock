# Relatório Técnico - SmartStock (Versão 2.0)

**Projeto:** Sistema Inteligente de Gestão de Estoque com Validade e FEFO  
**Versão:** 2.0 (V2 - Evolução de Arquitetura, Portabilidade e Interface Minimalista)  
**Disciplina / Contexto:** Projeto de Programação e Banco de Dados  

---

## 1. Introdução e Contexto da Evolução (V1 → V2)

Na **Versão 1.0 (V1)**, o **SmartStock** comprovou com sucesso a viabilidade do mini-mundo: controlar produtos perecíveis de forma inteligente, aplicando a regra **FEFO (*First Expire, First Out*)**, descontos progressivos por proximidade de validade e bloqueio rígido de mercadorias vencidas.

Entretanto, a implementação da V1 baseava-se em um backend local em Python com o microframework Flask, necessitando de:
- Instalação e configuração de ambiente Python (`requirements.txt`).
- Inicialização de servidor local em terminal (`app.py` na porta 5000).
- Recarregamento completo da página web a cada requisição (*server-side rendering*).
- Interface com sobrecarga de textos didáticos e notas explicativas.

A **Versão 2.0 (V2)** surge como uma evolução natural e substancial do projeto. O objetivo central da V2 foi **reestruturar toda a arquitetura tecnológica para tecnologias nativas da web (HTML5, Vanilla CSS3 e Vanilla JavaScript)**, eliminando a dependência de servidores e compiladores locais, ao mesmo tempo em que a interface foi refinada para um padrão **minimalista, limpo e profissional**.

---

## 2. Mudanças Tecnológicas: Transição da Stack

A tabela abaixo sintetiza a transição tecnológica realizada entre a V1 e a V2:

| Componente | Versão 1.0 (Anterior) | Versão 2.0 (Atual) | Motivo da Mudança |
| :--- | :--- | :--- | :--- |
| **Linguagem Principal** | Python 3 | **JavaScript Puro (ES6+)** | Execução nativa no motor do navegador sem necessidade de interpretador local. |
| **Framework Web** | Flask (Python) | **Nenhum (Vanilla Web)** | Eliminação de dependências externas e simplificação estrutural. |
| **Camada Visual** | Templates Jinja2 + CSS Básico | **HTML5 Semântico + CSS3 Moderno** | Design minimalista, responsivo, sem recarregamento de página. |
| **Persistência de Dados** | SQLite via arquivo `.db` | **LocalStorage Estruturado + SQL Schema** | Portabilidade total: o sistema roda em qualquer máquina mantendo os dados salvos. |
| **Execução do Projeto** | Servidor local (`py app.py`) | **Abertura direta do arquivo (`index.html`)** | Zero atrito de configuração para apresentação e uso. |

---

## 3. Como Avançamos na V2 (Melhorias e Inovações)

### 3.1. Arquitetura 100% Client-Side e Reativa
Toda a lógica de negócios antes processada no servidor Python agora opera diretamente no cliente através de funções puras em JavaScript:
- **Sem recarregamento de página:** Inclusões de lotes, produtos e confirmação de vendas atualizam instantaneamente a tela (conceito de *Single Page Application*).
- **Feedback instantâneo:** Notificações discretas (*Toasts*) informam o sucesso ou motivo de bloqueio de qualquer ação sem interromper a navegação.
- **Pré-visualização Dinâmica da Venda:** Ao selecionar um produto no formulário de venda, o sistema calcula em tempo real qual lote será consumido pela regra FEFO, o desconto aplicável e o preço unitário final antes mesmo de o usuário clicar em confirmar.

### 3.2. Redesenho Minimalista da Interface (UI/UX)
Na V1, a interface possuía avisos longos e explicações textuais sobre como os algoritmos funcionavam. Na V2, adotou-se o princípio do **design minimalista focado em usabilidade**:
- **Eliminação de ruídos visuais:** Remoção de menções a nomes de linguagens, notas prolixas e jargões teóricos.
- **Navegação por Abas (*Tabs*):** As tabelas de dados foram organizadas em abas dedicadas (**Lotes**, **Produtos** e **Histórico de Vendas**), economizando espaço em tela e evitando rolagens exaustivas.
- **Barra de Indicadores Compactos (KPIs):** Cinco cartões discretos no topo fornecem a visão executiva do estoque:
  1. *Estoque Total Vendável* (unidades válidas no prazo);
  2. *Itens com Desconto Ativo* (lotes com 10%, 20% ou 30% OFF);
  3. *Lotes Vencidos* (bloqueados para saída comercial);
  4. *Alerta de Reposição* (produtos que atingiram ou caíram abaixo do estoque mínimo);
  5. *Total Faturado em Vendas* (receita financeira acumulada).

### 3.3. Gestão Completa do Ciclo de Vida do Lote
Além da venda por FEFO, a V2 introduziu a **Ação Rápida de Descarte**:
- Lotes vencidos não apenas são bloqueados para venda, mas contam com um botão direto de `Descartar`, permitindo registrar a baixa de perda e zerar a quantidade do lote sem misturá-lo aos itens comerciais.

### 3.4. Portabilidade, Backup e Recuperação de Dados
A persistência no `localStorage` foi blindada com ferramentas auxiliares acessíveis no cabeçalho:
- **Restaurar Dados Padrão:** Botão que reinicializa a base com produtos e lotes didáticos (incluindo lotes vencidos e lotes em faixas de desconto), permitindo demonstrações limpas a qualquer momento.
- **Exportar Backup (JSON):** Baixa um arquivo `.json` com todo o estado atual de produtos, lotes e histórico.
- **Importar Backup:** Permite carregar dados previamente salvos em qualquer máquina ou navegador.

---

## 4. O Schema do Banco de Dados Relacional (SQL)

Mesmo com a aplicação rodando de forma independente no navegador, **a modelagem do banco de dados relacional foi rigorosamente mantida e documentada**. 

O sistema possui uma estrutura relacional normalizada com 3 tabelas fundamentais conectadas por integridade referencial (`FOREIGN KEY`), cujos dados são refletidos estruturadamente no modelo da aplicação:

```sql
-- ====================================================================
-- SMARTSTOCK V2 - SCHEMA DO BANCO DE DADOS RELACIONAL (SQL)
-- ====================================================================

-- 1. TABELA DE PRODUTOS
-- Cadastra as informações básicas do item comercializado e seu limite de segurança.
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_sku VARCHAR(50) UNIQUE,
    nome TEXT NOT NULL,
    categoria TEXT DEFAULT 'Geral',
    preco REAL NOT NULL,
    estoque_minimo INTEGER NOT NULL DEFAULT 5
);

-- 2. TABELA DE LOTES (Controle individual de validade por entrada)
-- Permite que o mesmo produto tenha múltiplos prazos de validade e saldos independentes.
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    numero_lote TEXT NOT NULL,
    data_validade DATE NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    status VARCHAR(20) DEFAULT 'ATIVO', -- 'ATIVO', 'DESCARTADO'
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

-- 3. TABELA DE VENDAS (Auditoria e rastreabilidade da saída FEFO)
-- Registra cada movimentação de saída com o lote consumido e o desconto concedido.
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
```

> **Acesso no Sistema:** No cabeçalho da aplicação existe o botão **"Schema SQL"**, que abre um modal com o código DDL completo e a opção de copiar a query para a área de transferência.

---

## 5. Lógica de Negócio em JavaScript (Equivalência com a V1)

A lógica central foi transcrita de forma modular no arquivo `js/app.js`:

1. **Cálculo da Validade e Desconto (`calcularValidadeEDesconto`):**
   $$\text{dias} = \text{data\_validade} - \text{data\_atual}$$
   - $\text{dias} < 0$: Marcado como **Vencido** e venda terminantemente proibida.
   - $0 \le \text{dias} \le 6$: Desconto Crítico de **30% OFF**.
   - $7 \le \text{dias} \le 14$: Desconto de Atenção de **20% OFF**.
   - $15 \le \text{dias} \le 30$: Desconto Promocional de **10% OFF**.
   - $\text{dias} > 30$: Preço normal (**0% de desconto**).

2. **Algoritmo de Saída FEFO (`realizarVenda`):**
   - Filtra apenas os lotes do produto que possuem saldo positivo (`quantidade > 0`), status ativo e data de validade não vencida (`dias >= 0`).
   - Aplica a ordenação ascendente pela data de validade:
     ```javascript
     lotesValidos.sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));
     ```
   - Consome a quantidade solicitada começando obrigatoriamente pelo primeiro lote da lista (o mais próximo do vencimento).
   - Se o lote prioritário não cobrir toda a demanda, o algoritmo consome seu saldo restante e passa para o lote seguinte, aplicando os descontos proporcionais a cada lote consumido.

3. **Alerta de Reposição de Estoque (`atualizarKPIs`):**
   - Calcula a soma das quantidades válidas de cada produto. Caso o saldo vendável seja menor ou igual a `estoque_minimo`, ativa a sinalização visual de reposição e incrementa o contador da barra superior.

---

## 6. Como Executar a Versão 2.0

A execução do projeto na V2 foi simplificada ao máximo:

1. **Nenhum comando de terminal ou instalação de pacotes é necessário.**
2. Localize o arquivo `index.html` na raiz do projeto.
3. Dê um duplo clique no arquivo para abri-lo em qualquer navegador moderno (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari ou Opera).

O sistema carrega os dados automaticamente do armazenamento local e já está pronto para uso.

---

## 7. Comparativo Geral: V1 vs. V2

| Aspecto | Versão 1.0 (V1) | Versão 2.0 (V2) |
| :--- | :--- | :--- |
| **Dependências** | Python 3, Flask, Werkzeug | **Zero dependências externas** |
| **Instalação** | Obrigatória (`pip install -r requirements.txt`) | **Desnecessária (Plug & Play)** |
| **Inicialização** | Linha de comando (`py app.py`) | **Duplo clique em `index.html`** |
| **Atualização Visual** | Recarregamento de página a cada POST | **Reativa e instantânea via DOM / JS** |
| **Estilo da Interface** | Didático com textos explicativos longos | **Minimalista, profissional e focado em ações** |
| **Navegação** | Tabelas sequenciais empilhadas | **Abas temáticas com busca e filtros rápidos** |
| **Portabilidade** | Dependente do ambiente da máquina | **100% portável para qualquer dispositivo** |
| **Backup de Dados** | Apenas cópia manual do arquivo `.db` | **Exportação e importação nativa em JSON** |

---

## 8. Conclusão

A **Versão 2.0 do SmartStock** consolidou um salto qualitativo significativo: preservou integralmente as regras de negócio de FEFO, validade e controle relacional de dados concebidas na V1, mas substituiu a complexidade de um servidor Python por uma solução elegante, autônoma e minimalista em **HTML5, CSS3 e JavaScript**.

O resultado é um software ágil, visualmente refinado, de manutenção simples e pronto para ser executado e avaliado em qualquer ambiente sem atritos operacionais.
