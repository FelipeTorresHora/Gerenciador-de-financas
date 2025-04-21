// URL base da sua Sheet2API
const SHEET2_BASE = "https://sheet2api.com/v1/iHLaXYEkR9GG/db-orcamento/P%C3%A1gina3";

// Manipulação do formulário de transação
const transactionForm = document.getElementById('transaction-form');

if (transactionForm) {
  transactionForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const tipo = document.querySelector('input[name="transaction-type"]:checked').value === 'income' ? 'Receita' : 'Despesa';
    const descricao = document.getElementById('description').value;
    const valor = parseFloat(document.getElementById('amount').value);
    const categoria = document.getElementById('category').value;
    const data = document.getElementById('date').value;
    const notas = document.getElementById('notes').value;

    if (!descricao || !valor || !categoria || !data) {
      alert('Por favor, preencha todos os campos obrigatórios');
      return;
    }

    const [ano, mes, dia] = data.split('-');
    const dataFormatada = `${dia}/${mes}/${ano}`;
    const valorFormatado = `R$ ${valor.toFixed(2).replace('.', ',')}`;

    try {
      const res = await fetch(SHEET2_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          Valor: valorFormatado,
          Categoria: categoria,
          Data: dataFormatada,
          Tipo: tipo
        })
      });
      if (!res.ok) throw new Error();
      alert('Transação salva com sucesso!');
      document.getElementById('transaction-modal').classList.add('hidden');
      transactionForm.reset();
      loadTransactions();
    } catch {
      alert('Erro ao salvar transação.');
    }
  });
}

// Busca todas as transações da planilha
async function fetchTransactions() {
  const res = await fetch(SHEET2_BASE);
  if (!res.ok) throw new Error('Erro ao buscar transações');
  return res.json();
}

// Atualiza a tabela de transações
async function loadTransactions() {
  const tbody = document.querySelector('#transaction-table tbody');
  tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Carregando...</td></tr>';

  let rows;
  try {
    rows = await fetchTransactions();
  } catch {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-600">Falha ao carregar</td></tr>';
    return;
  }

  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Nenhuma transação</td></tr>';
    return;
  }

  tbody.innerHTML = '';
  rows.forEach(row => {
    const isIncome    = row.Tipo === 'Receita';
    const valueClass  = isIncome ? 'text-green-600' : 'text-red-600';
    const valuePrefix = isIncome ? '+ ' : '- ';
    const catClass    = isIncome ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';

    tbody.innerHTML += `
      <tr class="hover:bg-gray-50">
        <td class="px-6 py-4"><div class="text-sm font-medium">${row.Descricao||'—'}</div></td>
        <td class="px-6 py-4"><span class="px-2 inline-flex text-xs font-semibold rounded-full ${catClass}">${row.Categoria||'—'}</span></td>
        <td class="px-6 py-4 text-sm text-gray-500">${row.Data}</td>
        <td class="px-6 py-4 text-sm text-right font-medium ${valueClass}">${valuePrefix}${row.Valor}</td>
        <td class="px-6 py-4 text-right text-sm">
          <button class="delete-transaction" data-row="${row.__rowNum__}" data-valor="${row.Valor}" data-categoria="${row.Categoria}" data-data="${row.Data}" data-tipo="${row.Tipo}">
            <i class="fas fa-trash-alt"></i>
          </button>
        </td>
      </tr>`;
  });

  document.querySelectorAll('.delete-transaction').forEach(btn => {
    btn.onclick = async () => {
      if (!confirm('Tem certeza que deseja excluir esta transação?')) return;
      const payload = {
        Valor:     btn.dataset.valor,
        Categoria: btn.dataset.categoria,
        Data:      btn.dataset.data,
        Tipo:      btn.dataset.tipo
      };
      const res = await fetch(`${SHEET2_BASE}/${btn.dataset.row}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert('Transação excluída com sucesso!');
        loadTransactions();
      } else {
        alert('Erro ao excluir transação.');
      }
    };
  });
}

// Inicia a carga de dados quando a página estiver pronta
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('#transaction-table')) {
    loadTransactions();
  }
});

actionSelect.addEventListener('change', (e) => {
    const actionInput = document.getElementById('action-input');
    if (e.target.value === 'delete') {
      addFields.classList.add('hidden');
      deleteField.classList.remove('hidden');
      actionInput.value = 'delete';
    } else {
      deleteField.classList.add('hidden');
      addFields.classList.remove('hidden');
      actionInput.value = 'add';
    }
  });
  