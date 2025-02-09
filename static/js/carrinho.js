document.addEventListener('DOMContentLoaded', function() {
    // Manipulação de quantidade
    document.querySelectorAll('.qtd-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.qtd-input');
            let valor = parseInt(input.value);
            
            if (this.classList.contains('mais')) {
                valor++;
            } else if (valor > 1) {
                valor--;
            }
            
            input.value = valor;
            atualizarQuantidade(
                this.closest('.carrinho-item').dataset.nome,
                valor
            );
        });
    });

    // Remover item
    document.querySelectorAll('.remover-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const item = this.closest('.carrinho-item');
            removerItem(item.dataset.nome);
        });
    });

    // Remover a função finalizarPedido antiga
    document.querySelector('.finalizar-btn')?.addEventListener('click', abrirFormularioCliente);
});

async function atualizarQuantidade(nome, quantidade) {
    try {
        const response = await fetch('/atualizar_quantidade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome, quantidade })
        });
        if (response.ok) {
            location.reload();
        }
    } catch (error) {
        console.error('Erro ao atualizar quantidade:', error);
    }
}

async function removerItem(nome) {
    try {
        const response = await fetch('/remover_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nome })
        });
        if (response.ok) {
            toast.show(`${nome} removido do carrinho`);
            location.reload();
        }
    } catch (error) {
        console.error('Erro ao remover item:', error);
        toast.show('Erro ao remover item', 'error');
    }
}

// Manter apenas a versão com o formulário
function abrirFormularioCliente() {
    document.getElementById('modal-cliente').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modal-cliente').style.display = 'none';
}

document.getElementById('form-cliente').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const dadosCliente = {
        nome: document.getElementById('nome').value,
        endereco: document.getElementById('endereco').value,
        telefone: document.getElementById('telefone').value
    };
    
    try {
        const response = await fetch('/finalizar_pedido', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosCliente)
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            fecharModal();
            toast.show('Pedido finalizado com sucesso!');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            toast.show(data.message || 'Erro ao finalizar pedido', 'error');
        }
    } catch (error) {
        console.error('Erro ao finalizar pedido:', error);
        toast.show('Erro ao finalizar pedido', 'error');
    }
});

// Fechar modal quando clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('modal-cliente');
    if (event.target === modal) {
        fecharModal();
    }
}
