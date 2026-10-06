/**
 * ====================================================================
 * SMARTSTOCK - LÓGICA MINIMALISTA & ROBUSTA (VANILLA JS)
 * ====================================================================
 */

const STORAGE_KEY = 'smartstock_db_v1';

// Formatação de Datas
function formatarDataISO(data) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const dia = String(data.getDate()).padStart(2, '0');
  return `${ano}-${mes}-${dia}`;
}

function dataRelativa(dias) {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return formatarDataISO(d);
}

function formatarDataExibicao(isoStr) {
  if (!isoStr) return '-';
  const partes = isoStr.split('-');
  if (partes.length !== 3) return isoStr;
  return `${partes[2]}/${partes[1]}/${partes[0]}`;
}

// Dados Padrão (Seed Inicial)
function obterDadosIniciais() {
  return {
    produtos: [
      { id: 1, codigo_sku: 'LAT-001', nome: 'Iogurte Natural 500g', categoria: 'Laticínios', preco: 8.90, estoque_minimo: 15 },
      { id: 2, codigo_sku: 'SUP-002', nome: 'Whey Protein 900g', categoria: 'Suplementos', preco: 159.90, estoque_minimo: 8 },
      { id: 3, codigo_sku: 'BEB-003', nome: 'Suco de Laranja 1L', categoria: 'Bebidas', preco: 12.50, estoque_minimo: 15 },
      { id: 4, codigo_sku: 'FAR-004', nome: 'Vitamina C 10c', categoria: 'Farmácia', preco: 16.00, estoque_minimo: 10 }
    ],
    lotes: [
      { id: 1, produto_id: 1, numero_lote: 'LT-IOG-01A', data_validade: dataRelativa(4), quantidade: 12, status: 'ATIVO' },
      { id: 2, produto_id: 1, numero_lote: 'LT-IOG-01B', data_validade: dataRelativa(22), quantidade: 25, status: 'ATIVO' },
      { id: 3, produto_id: 1, numero_lote: 'LT-IOG-01C', data_validade: dataRelativa(60), quantidade: 40, status: 'ATIVO' },
      { id: 4, produto_id: 2, numero_lote: 'LT-WHEY-21', data_validade: dataRelativa(10), quantidade: 6, status: 'ATIVO' },
      { id: 5, produto_id: 2, numero_lote: 'LT-WHEY-22', data_validade: dataRelativa(180), quantidade: 15, status: 'ATIVO' },
      { id: 6, produto_id: 3, numero_lote: 'LT-SUCO-VENC', data_validade: dataRelativa(-2), quantidade: 8, status: 'ATIVO' },
      { id: 7, produto_id: 3, numero_lote: 'LT-SUCO-OK', data_validade: dataRelativa(25), quantidade: 10, status: 'ATIVO' },
      { id: 8, produto_id: 4, numero_lote: 'LT-VITC-99', data_validade: dataRelativa(90), quantidade: 4, status: 'ATIVO' }
    ],
    vendas: [
      {
        id: 1,
        data_venda: new Date(Date.now() - 3600000 * 3).toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        produto_id: 1,
        produto_nome: 'Iogurte Natural 500g',
        lote_id: 1,
        numero_lote: 'LT-IOG-01A',
        quantidade: 4,
        desconto_percentual: 30,
        preco_unitario: 6.23,
        valor_total: 24.92
      }
    ]
  };
}

function carregarDados() {
  const salvo = localStorage.getItem(STORAGE_KEY);
  if (!salvo) {
    const iniciais = obterDadosIniciais();
    salvarDados(iniciais);
    return iniciais;
  }
  try {
    return JSON.parse(salvo);
  } catch (e) {
    const iniciais = obterDadosIniciais();
    salvarDados(iniciais);
    return iniciais;
  }
}

function salvarDados(dados) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(dados));
}

// Regras de Validade e Descontos
function calcularDiasRestantes(dataValidadeStr) {
  if (!dataValidadeStr) return 0;
  const [ano, mes, dia] = dataValidadeStr.split('-').map(Number);
  const dataValidade = new Date(ano, mes - 1, dia);
  const hoje = new Date();
  const hojeSemHora = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
  return Math.round((dataValidade.getTime() - hojeSemHora.getTime()) / (1000 * 60 * 60 * 24));
}

function calcularValidadeEDesconto(dataValidadeStr, precoBase) {
  const dias = calcularDiasRestantes(dataValidadeStr);
  const preco = Number(precoBase) || 0;

  if (dias < 0) {
    return {
      dias,
      status: 'Vencido',
      classe: 'badge-vencido',
      podeVender: false,
      desconto: 0,
      precoFinal: preco
    };
  } else if (dias <= 6) {
    const desconto = 30.0;
    return {
      dias,
      status: '-30%',
      classe: 'badge-critico',
      podeVender: true,
      desconto,
      precoFinal: +(preco * 0.70).toFixed(2)
    };
  } else if (dias <= 14) {
    const desconto = 20.0;
    return {
      dias,
      status: '-20%',
      classe: 'badge-atencao',
      podeVender: true,
      desconto,
      precoFinal: +(preco * 0.80).toFixed(2)
    };
  } else if (dias <= 30) {
    const desconto = 10.0;
    return {
      dias,
      status: '-10%',
      classe: 'badge-promocao',
      podeVender: true,
      desconto,
      precoFinal: +(preco * 0.90).toFixed(2)
    };
  } else {
    return {
      dias,
      status: 'Normal',
      classe: 'badge-normal',
      podeVender: true,
      desconto: 0,
      precoFinal: preco
    };
  }
}

// Operação de Venda
function realizarVenda(produtoId, quantidadeDesejada) {
  const dados = carregarDados();
  const produto = dados.produtos.find(p => p.id === produtoId);

  if (!produto) {
    mostrarToast('Produto inválido.', 'erro');
    return false;
  }

  if (quantidadeDesejada <= 0) {
    mostrarToast('Quantidade deve ser maior que zero.', 'erro');
    return false;
  }

  // Seleciona lotes válidos e ordena pela validade mais próxima
  const lotesValidos = dados.lotes
    .filter(l => l.produto_id === produtoId && l.status === 'ATIVO' && l.quantidade > 0 && calcularDiasRestantes(l.data_validade) >= 0)
    .sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));

  const totalDisponivel = lotesValidos.reduce((total, l) => total + l.quantidade, 0);

  if (totalDisponivel < quantidadeDesejada) {
    mostrarToast(`Estoque insuficiente no prazo (disponível: ${totalDisponivel} un).`, 'erro');
    return false;
  }

  let restante = quantidadeDesejada;
  let valorTotalVenda = 0;
  const horaFormatada = new Date().toLocaleDateString('pt-BR') + ' ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

  for (const lote of lotesValidos) {
    if (restante <= 0) break;

    const qtdDesteLote = Math.min(lote.quantidade, restante);
    const info = calcularValidadeEDesconto(lote.data_validade, produto.preco);
    const subtotal = +(qtdDesteLote * info.precoFinal).toFixed(2);

    valorTotalVenda += subtotal;
    lote.quantidade -= qtdDesteLote;

    dados.vendas.unshift({
      id: Date.now() + Math.floor(Math.random() * 1000),
      data_venda: horaFormatada,
      produto_id: produto.id,
      produto_nome: produto.nome,
      lote_id: lote.id,
      numero_lote: lote.numero_lote,
      quantidade: qtdDesteLote,
      desconto_percentual: info.desconto,
      preco_unitario: info.precoFinal,
      valor_total: subtotal
    });

    restante -= qtdDesteLote;
  }

  salvarDados(dados);
  atualizarInterface();
  mostrarToast(`Venda confirmada: R$ ${valorTotalVenda.toFixed(2)}`, 'sucesso');
  return true;
}

// Cadastro de Produto
function cadastrarProduto(nome, preco, estoqueMinimo, categoria) {
  if (!nome || !nome.trim()) {
    mostrarToast('Nome obrigatório.', 'erro');
    return false;
  }
  const precoNum = parseFloat(preco);
  if (!precoNum || precoNum <= 0) {
    mostrarToast('Preço inválido.', 'erro');
    return false;
  }

  const dados = carregarDados();
  const novoId = dados.produtos.length > 0 ? Math.max(...dados.produtos.map(p => p.id)) + 1 : 1;

  dados.produtos.push({
    id: novoId,
    codigo_sku: `PRD-${String(novoId).padStart(3, '0')}`,
    nome: nome.trim(),
    categoria: (categoria || 'Geral').trim(),
    preco: precoNum,
    estoque_minimo: parseInt(estoqueMinimo, 10) || 5
  });

  salvarDados(dados);
  atualizarInterface();
  mostrarToast('Produto cadastrado.', 'sucesso');
  return true;
}

// Cadastro de Lote
function cadastrarLote(produtoId, numeroLote, dataValidade, quantidade) {
  if (!produtoId || !numeroLote || !dataValidade || quantidade <= 0) {
    mostrarToast('Preencha os dados do lote corretamente.', 'erro');
    return false;
  }

  const dados = carregarDados();
  const novoId = dados.lotes.length > 0 ? Math.max(...dados.lotes.map(l => l.id)) + 1 : 1;

  dados.lotes.push({
    id: novoId,
    produto_id: parseInt(produtoId, 10),
    numero_lote: numeroLote.trim(),
    data_validade: dataValidade,
    quantidade: parseInt(quantidade, 10),
    status: 'ATIVO'
  });

  salvarDados(dados);
  atualizarInterface();
  mostrarToast('Lote cadastrado.', 'sucesso');
  return true;
}

function descartarLote(loteId) {
  const dados = carregarDados();
  const lote = dados.lotes.find(l => l.id === loteId);
  if (!lote) return;

  lote.quantidade = 0;
  lote.status = 'DESCARTADO';

  salvarDados(dados);
  atualizarInterface();
  mostrarToast(`Lote ${lote.numero_lote} descartado.`, 'info');
}

function excluirProduto(produtoId) {
  if (!confirm('Excluir este produto e seus lotes?')) return;
  const dados = carregarDados();
  dados.produtos = dados.produtos.filter(p => p.id !== produtoId);
  dados.lotes = dados.lotes.filter(l => l.produto_id !== produtoId);
  salvarDados(dados);
  atualizarInterface();
  mostrarToast('Produto removido.', 'info');
}

function excluirLote(loteId) {
  if (!confirm('Excluir este lote?')) return;
  const dados = carregarDados();
  dados.lotes = dados.lotes.filter(l => l.id !== loteId);
  salvarDados(dados);
  atualizarInterface();
  mostrarToast('Lote removido.', 'info');
}

// Renderização e Atualização da Interface
function atualizarInterface() {
  const dados = carregarDados();
  atualizarKPIs(dados);
  atualizarSelects(dados);
  renderizarLotes(dados);
  renderizarProdutos(dados);
  renderizarVendas(dados);
  atualizarPreview();
}

function atualizarKPIs(dados) {
  let estoqueTotal = 0;
  let comDesconto = 0;
  let vencidos = 0;
  let repor = 0;
  let totalVendas = 0;

  const estoquePorProduto = {};
  dados.produtos.forEach(p => { estoquePorProduto[p.id] = 0; });

  dados.lotes.forEach(l => {
    if (l.status !== 'ATIVO') return;
    const dias = calcularDiasRestantes(l.data_validade);
    if (dias < 0) {
      if (l.quantidade > 0) vencidos++;
    } else {
      estoqueTotal += l.quantidade;
      if (estoquePorProduto[l.produto_id] !== undefined) {
        estoquePorProduto[l.produto_id] += l.quantidade;
      }
      if (dias <= 30 && l.quantidade > 0) {
        comDesconto++;
      }
    }
  });

  dados.produtos.forEach(p => {
    if ((estoquePorProduto[p.id] || 0) <= p.estoque_minimo) repor++;
  });

  dados.vendas.forEach(v => {
    totalVendas += v.valor_total || 0;
  });

  document.getElementById('kpi-estoque-val').textContent = estoqueTotal;
  document.getElementById('kpi-desconto-val').textContent = comDesconto;
  document.getElementById('kpi-vencidos-val').textContent = vencidos;
  document.getElementById('kpi-repor-val').textContent = repor;
  document.getElementById('kpi-vendas-val').textContent = `R$ ${totalVendas.toFixed(2)}`;
}

function atualizarSelects(dados) {
  const selVenda = document.getElementById('venda-produto-id');
  const selLote = document.getElementById('lote-produto-id');

  const prevVenda = selVenda.value;
  const prevLote = selLote.value;

  selVenda.innerHTML = '';
  selLote.innerHTML = '';

  if (dados.produtos.length === 0) {
    selVenda.innerHTML = '<option value="">Nenhum produto</option>';
    selLote.innerHTML = '<option value="">Nenhum produto</option>';
    return;
  }

  dados.produtos.forEach(p => {
    const saldo = dados.lotes
      .filter(l => l.produto_id === p.id && l.status === 'ATIVO' && l.quantidade > 0 && calcularDiasRestantes(l.data_validade) >= 0)
      .reduce((s, l) => s + l.quantidade, 0);

    const optV = document.createElement('option');
    optV.value = p.id;
    optV.textContent = `${p.nome} (Saldo: ${saldo})`;
    selVenda.appendChild(optV);

    const optL = document.createElement('option');
    optL.value = p.id;
    optL.textContent = p.nome;
    selLote.appendChild(optL);
  });

  if (prevVenda && dados.produtos.some(p => p.id == prevVenda)) selVenda.value = prevVenda;
  if (prevLote && dados.produtos.some(p => p.id == prevLote)) selLote.value = prevLote;
}

function renderizarLotes(dados) {
  const tbody = document.getElementById('tabela-lotes-body');
  const filtro = document.getElementById('filtro-lote-status')?.value || 'todos';
  const busca = (document.getElementById('busca-lote')?.value || '').toLowerCase();

  const lotesOrdenados = [...dados.lotes].sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));
  tbody.innerHTML = '';

  const filtrados = lotesOrdenados.filter(l => {
    const prod = dados.produtos.find(p => p.id === l.produto_id) || { nome: '' };
    const match = prod.nome.toLowerCase().includes(busca) || l.numero_lote.toLowerCase().includes(busca);
    if (!match) return false;

    const dias = calcularDiasRestantes(l.data_validade);
    if (filtro === 'vencidos') return dias < 0;
    if (filtro === 'promocao') return dias >= 0 && dias <= 30;
    if (filtro === 'normal') return dias > 30;
    if (filtro === 'ativos') return l.quantidade > 0;
    return true;
  });

  if (filtrados.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-cell">Nenhum lote encontrado</td></tr>';
    return;
  }

  filtrados.forEach(l => {
    const prod = dados.produtos.find(p => p.id === l.produto_id) || { nome: '-', preco: 0 };
    const info = calcularValidadeEDesconto(l.data_validade, prod.preco);

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${prod.nome}</strong></td>
      <td><span class="code-tag">${l.numero_lote}</span></td>
      <td>${formatarDataExibicao(l.data_validade)}</td>
      <td>${info.dias < 0 ? `<span style="color:#ef4444;">Venceu</span>` : `${info.dias}d`}</td>
      <td><strong>${l.quantidade}</strong></td>
      <td>R$ ${prod.preco.toFixed(2)}</td>
      <td><strong>R$ ${info.precoFinal.toFixed(2)}</strong></td>
      <td><span class="badge ${info.classe}">${info.status}</span></td>
      <td>
        <div style="display: flex; gap: 4px;">
          ${info.dias < 0 && l.quantidade > 0 
            ? `<button class="btn-xs btn-xs-danger" onclick="descartarLote(${l.id})">Descartar</button>` 
            : ''}
          <button class="btn-xs" onclick="excluirLote(${l.id})">Excluir</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderizarProdutos(dados) {
  const tbody = document.getElementById('tabela-produtos-body');
  tbody.innerHTML = '';

  if (dados.produtos.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-cell">Nenhum produto cadastrado</td></tr>';
    return;
  }

  dados.produtos.forEach(p => {
    const saldo = dados.lotes
      .filter(l => l.produto_id === p.id && l.status === 'ATIVO' && l.quantidade > 0 && calcularDiasRestantes(l.data_validade) >= 0)
      .reduce((s, l) => s + l.quantidade, 0);

    const precisaRepor = saldo <= p.estoque_minimo;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${p.nome}</strong></td>
      <td><span class="code-tag">${p.categoria}</span></td>
      <td>R$ ${p.preco.toFixed(2)}</td>
      <td>${p.estoque_minimo}</td>
      <td><strong>${saldo}</strong></td>
      <td>
        ${precisaRepor 
          ? `<span class="badge badge-critico">Repor</span>` 
          : `<span class="badge badge-normal">OK</span>`}
      </td>
      <td>
        <button class="btn-xs" onclick="excluirProduto(${p.id})">Excluir</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderizarVendas(dados) {
  const tbody = document.getElementById('tabela-vendas-body');
  tbody.innerHTML = '';

  if (!dados.vendas || dados.vendas.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-cell">Nenhuma venda registrada</td></tr>';
    return;
  }

  dados.vendas.slice(0, 20).forEach(v => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="color: var(--text-muted);">${v.data_venda}</td>
      <td><strong>${v.produto_nome}</strong></td>
      <td><span class="code-tag">${v.numero_lote}</span></td>
      <td>${v.quantidade}</td>
      <td>${v.desconto_percentual > 0 ? `<span class="badge badge-critico">-${v.desconto_percentual}%</span>` : `<span class="badge badge-normal">0%</span>`}</td>
      <td><strong>R$ ${v.valor_total.toFixed(2)}</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

function atualizarPreview() {
  const sel = document.getElementById('venda-produto-id');
  const preview = document.getElementById('fefo-preview');
  if (!sel || !preview) return;

  const pId = parseInt(sel.value, 10);
  if (!pId) {
    preview.textContent = 'Selecione um produto';
    return;
  }

  const dados = carregarDados();
  const produto = dados.produtos.find(p => p.id === pId);
  if (!produto) return;

  const lotesValidos = dados.lotes
    .filter(l => l.produto_id === pId && l.status === 'ATIVO' && l.quantidade > 0 && calcularDiasRestantes(l.data_validade) >= 0)
    .sort((a, b) => new Date(a.data_validade) - new Date(b.data_validade));

  if (lotesValidos.length === 0) {
    preview.innerHTML = '<span style="color:#ef4444;">Sem estoque no prazo</span>';
    return;
  }

  const lote = lotesValidos[0];
  const info = calcularValidadeEDesconto(lote.data_validade, produto.preco);

  preview.innerHTML = `Lote prioritário: <strong>${lote.numero_lote}</strong> · R$ ${info.precoFinal.toFixed(2)} (${info.desconto > 0 ? '-' + info.desconto + '%' : 'preço base'})`;
}

// Notificações Toast
function mostrarToast(mensagem, tipo = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${tipo}`;
  toast.textContent = mensagem;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// Listeners e Inicialização
document.addEventListener('DOMContentLoaded', () => {
  atualizarInterface();

  // Abas
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      document.getElementById(targetId)?.classList.add('active');

      const filterBar = document.getElementById('lotes-filter-bar');
      if (filterBar) {
        filterBar.style.display = targetId === 'tab-lotes' ? 'flex' : 'none';
      }
    });
  });

  // Formulário Venda
  document.getElementById('form-venda')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const pId = parseInt(document.getElementById('venda-produto-id').value, 10);
    const qtd = parseInt(document.getElementById('venda-quantidade').value, 10);
    realizarVenda(pId, qtd);
  });

  document.getElementById('venda-produto-id')?.addEventListener('change', atualizarPreview);
  document.getElementById('venda-quantidade')?.addEventListener('input', atualizarPreview);

  // Formulário Lote
  const inputValidade = document.getElementById('lote-data-validade');
  if (inputValidade) inputValidade.value = dataRelativa(30);

  document.getElementById('form-lote')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const pId = document.getElementById('lote-produto-id').value;
    const num = document.getElementById('lote-numero').value;
    const val = document.getElementById('lote-data-validade').value;
    const qtd = document.getElementById('lote-quantidade').value;

    if (cadastrarLote(pId, num, val, qtd)) {
      document.getElementById('form-lote').reset();
      if (inputValidade) inputValidade.value = dataRelativa(30);
    }
  });

  // Formulário Produto
  document.getElementById('form-produto')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const nome = document.getElementById('produto-nome').value;
    const cat = document.getElementById('produto-categoria').value;
    const preco = document.getElementById('produto-preco').value;
    const min = document.getElementById('produto-minimo').value;

    if (cadastrarProduto(nome, preco, min, cat)) {
      document.getElementById('form-produto').reset();
      document.getElementById('produto-categoria').value = 'Geral';
      document.getElementById('produto-minimo').value = '5';
    }
  });

  // Filtros
  document.getElementById('filtro-lote-status')?.addEventListener('change', () => renderizarLotes(carregarDados()));
  document.getElementById('busca-lote')?.addEventListener('input', () => renderizarLotes(carregarDados()));

  // Ações de Cabeçalho
  document.getElementById('btn-reset-seed')?.addEventListener('click', () => {
    if (confirm('Restaurar dados padrão de exemplo?')) {
      salvarDados(obterDadosIniciais());
      atualizarInterface();
      mostrarToast('Dados restaurados.', 'sucesso');
    }
  });

  document.getElementById('btn-exportar-json')?.addEventListener('click', () => {
    const dados = carregarDados();
    const blob = new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `smartstock_backup_${formatarDataISO(new Date())}.json`;
    a.click();
    URL.revokeObjectURL(url);
    mostrarToast('Backup exportado.', 'sucesso');
  });

  document.getElementById('btn-importar-json')?.addEventListener('click', () => {
    document.getElementById('input-import-file')?.click();
  });

  document.getElementById('input-import-file')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const importado = JSON.parse(event.target.result);
        if (importado.produtos && importado.lotes) {
          salvarDados(importado);
          atualizarInterface();
          mostrarToast('Dados importados.', 'sucesso');
        } else {
          mostrarToast('Arquivo de backup inválido.', 'erro');
        }
      } catch (err) {
        mostrarToast('Erro ao ler arquivo JSON.', 'erro');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  });

  // Modal Schema
  const modal = document.getElementById('modal-schema');
  document.getElementById('btn-ver-schema')?.addEventListener('click', () => modal?.classList.add('active'));
  document.getElementById('modal-close-btn')?.addEventListener('click', () => modal?.classList.remove('active'));
  modal?.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });

  document.getElementById('btn-copiar-sql')?.addEventListener('click', () => {
    const code = document.getElementById('sql-code-element').innerText;
    navigator.clipboard.writeText(code).then(() => mostrarToast('SQL copiado.', 'sucesso'));
  });
});
