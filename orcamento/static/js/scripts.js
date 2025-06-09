// Função utilitária para ler cookie CSRF
function getCookie(name) {
  const v = document.cookie.match('(^|;)\s*' + name + '\s*=\s*([^;]+)');
  return v ? v[2] : '';
}
const csrftoken = getCookie('csrftoken');

// Elementos do DOM
const form = document.getElementById('transaction-form');
const idInput = document.getElementById('id-input');
const successPopup = document.getElementById('success-popup');

// Função para mostrar o popup de sucesso
function showSuccessPopup() {
  if (successPopup) {
    successPopup.style.display = 'block';
    // Esconder o popup após 3 segundos
    setTimeout(() => {
      successPopup.style.display = 'none';
    }, 3000);
  }
}

// Buscar próximo ID disponível
async function fetchNextId() {
  try {
    const res = await fetch('/save-expense/', {
      headers: { 'X-CSRFToken': csrftoken }
    });
    if (res.ok) {
      const { next_id } = await res.json();
      if (next_id && idInput) {
        idInput.value = next_id;
      }
    } else {
      console.error('Erro ao buscar próximo ID:', res.status);
    }
  } catch (e) {
    console.error('Erro na requisição fetchNextId:', e);
  }
}

// Adicionar listener ao formulário se ele existir na página
if (form) {
  fetchNextId(); // Busca o ID inicial

  form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Previne o comportamento padrão do formulário

    let valor = document.getElementById('amount').value.replace(/[^\d,]/g, '').replace(',', '.');

    const payload = {
      Id: idInput.value,
      Valor: valor,
      Categoria: document.getElementById('category').value,
      Data: document.getElementById('date').value,
      Tipo: document.getElementById('transaction-type').value
    };

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
        showSuccessPopup(); // Mostra o popup de sucesso
        form.reset();
        await fetchNextId();

        const iframe = document.querySelector('iframe');
        if (iframe) {
          iframe.src = iframe.src; // Recarrega o iframe
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
}

// Lógica do menu mobile
const mobileBtn = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');
if (mobileBtn) {
  mobileBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
  });
}