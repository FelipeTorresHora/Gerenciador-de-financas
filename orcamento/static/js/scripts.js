// Função utilitária para ler cookie CSRF
function getCookie(name) {
  const v = document.cookie.match('(^|;)\s*' + name + '\s*=\s*([^;]+)');
  return v ? v[2] : '';
}
const csrftoken = getCookie('csrftoken');

// Elementos do formulário
const form = document.getElementById('transaction-form');
const idInput = document.getElementById('id-input');

// Buscar próximo ID
async function fetchNextId() {
  try {
      const res = await fetch('/save-expense/', {
          headers: { 'X-CSRFToken': csrftoken }
      });
      if (res.ok) {
          const { next_id } = await res.json();
          idInput.value = next_id;
      } else {
          console.error('Erro ao buscar próximo ID:', res.status);
      }
  } catch (e) {
      console.error('Erro na requisição fetchNextId:', e);
  }
}
fetchNextId();

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Formatar Valor como número (ex.: "100,00" → "100.00")
  let valor = document.getElementById('amount').value;
  valor = valor.replace(/[^\d,]/g, '').replace(',', '.');

  const payload = {
      Valor: valor,
      Categoria: document.getElementById('category').value,
      Data: document.getElementById('date').value,
      Tipo: document.getElementById('transaction-type').value
  };

  console.log('Payload enviado:', payload);

  try {
      const res = await fetch('/save-expense/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
          },
          body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok) {
          alert(data.message);
          form.reset();
          await fetchNextId();
          // Recarregar o iframe da tabela
          const iframe = document.querySelector('iframe');
          if (iframe) {
              iframe.contentWindow.location.reload();
          }
      } else {
          alert(`Erro: ${data.message}`);
          console.error('Erro na resposta:', data);
      }
  } catch (e) {
      console.error('Erro na requisição POST:', e);
      alert('Erro ao salvar transação. Verifique a conexão ou tente novamente.');
  }
});