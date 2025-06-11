// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    fetchNextId();

    const transactionForm = document.getElementById('transaction-form');
    if (transactionForm) {
        transactionForm.addEventListener('submit', handleFormSubmit);
    }
});

async function fetchNextId() {
    try {
        const response = await fetch('/save-expense/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const idInput = document.getElementById('id-input');
            if (idInput) {
                idInput.value = data.next_id;
            }
        }
    } catch (error) {
        console.error('Erro ao obter próximo ID:', error);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault(); 
    const form = event.target;
    const formData = new FormData(form);

    const valor = formData.get('Valor');
    const categoria = formData.get('Categoria');
    const data = formData.get('Data');
    const tipo = formData.get('Tipo');
    
    if (!valor || !categoria || !data || !tipo) {
        showPopup('Todos os campos são obrigatórios!', 'error');
        return;
    }

    const valorRegex = /^\d+([,\.]\d{1,2})?$/;
    if (!valorRegex.test(valor.replace('R$', '').trim())) {
        showPopup('Formato inválido para o valor! Use formato como: 100,00', 'error');
        return;
    }

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const postData = {
            'Id': formData.get('Id'),
            'Valor': valor,
            'Categoria': categoria,
            'Data': data,
            'Tipo': tipo
        };

        const response = await fetch('/save-expense/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(postData)
        });

        const result = await response.json();

        if (response.ok) {
            
            showPopup(result.message || 'Transação salva com sucesso!', 'success');
            
            form.reset();
            
            const idInput = document.getElementById('id-input');
            if (idInput && result.next_id) {
                idInput.value = result.next_id;
            }
            
            const iframe = document.querySelector('iframe');
            if (iframe) {
                iframe.src = iframe.src;
            }
            
        } else {
            showPopup(result.message || 'Erro ao salvar transação', 'error');
        }

    } catch (error) {
        console.error('Erro na requisição:', error);
        showPopup('Erro de conexão. Tente novamente.', 'error');
    }
}


function showPopup(message, type = 'success') {
    const existingPopup = document.getElementById('custom-popup');
    if (existingPopup) {
        existingPopup.remove();
    }


    const popup = document.createElement('div');
    popup.id = 'custom-popup';
    popup.className = `fixed top-5 right-5 py-3 px-6 rounded-lg shadow-lg text-white font-medium z-50 transform transition-all duration-300 ease-in-out`;

    if (type === 'success') {
        popup.classList.add('bg-green-500');
    } else if (type === 'error') {
        popup.classList.add('bg-red-500');
    } else {
        popup.classList.add('bg-blue-500');
    }
    
    popup.textContent = message;
    

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.style.transform = 'translateX(0)';
        popup.style.opacity = '1';
    }, 10);
    

    setTimeout(() => {
        popup.style.transform = 'translateX(100%)';
        popup.style.opacity = '0';
        setTimeout(() => {
            if (popup.parentNode) {
                popup.parentNode.removeChild(popup);
            }
        }, 300);
    }, 4000);
}

document.addEventListener('DOMContentLoaded', function() {
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); 
            
            if (value.length > 0) {
                if (value.length > 2) {
                    value = value.slice(0, -2) + ',' + value.slice(-2);
                }
                
                value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
            }
            
            e.target.value = value;
        });
        
        const dateInput = document.getElementById('date');
        if (dateInput && !dateInput.value) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        }
    }
});