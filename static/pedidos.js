document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('detailsModal');
    const closeModal = document.querySelector('.close-modal');

    // Carregar pedidos iniciais
    carregarPedidos();

    // Atualizar pedidos a cada 15 segundos (reduzido de 30)
    setInterval(carregarPedidos, 15000);

    // Iniciar SSE para atualizações em tempo real
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = async function(event) {
        try {
            const novoPedido = JSON.parse(event.data);
            playNotificationSound().catch(e => console.error('Erro no som:', e));
            showToast(`Novo pedido recebido de ${novoPedido.cliente}!`);
            await atualizarTabelaPedidos();
        } catch (error) {
            console.error('Erro ao processar novo pedido:', error);
        }
    };

    // Fechar modal
    closeModal.addEventListener('click', () => {
        modal.classList.remove('open');
    });

    // Fechar modal clicando fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('open');
        }
    });

    // Restaurar estado do auto-print
    const autoPrint = document.getElementById('autoPrint');
    autoPrint.checked = localStorage.getItem('autoPrint') === 'true';

    // Salvar preferência de auto-print
    autoPrint.addEventListener('change', (e) => {
        localStorage.setItem('autoPrint', e.target.checked);
    });

    // Modificar o eventSource.onmessage
    eventSource.onmessage = async function(event) {
        try {
            const novoPedido = JSON.parse(event.data);
            playNotificationSound().catch(e => console.error('Erro no som:', e));
            showToast(`Novo pedido recebido de ${novoPedido.cliente}!`);
            
            // Verificar se auto-print está ativado
            if (document.getElementById('autoPrint').checked) {
                imprimirPedidoAutomatico(novoPedido.id);
            }
            
            await atualizarTabelaPedidos();
        } catch (error) {
            console.error('Erro ao processar novo pedido:', error);
        }
    };
});

async function carregarPedidos() {
    try {
        const response = await fetch('/pedidos');
        const pedidos = await response.json();
        
        const tbody = document.getElementById('pedidos-tbody');
        tbody.innerHTML = '';

        if (!pedidos.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Nenhum pedido encontrado</td></tr>';
            return;
        }

        pedidos.forEach(pedido => {
            const tr = criarLinhaPedido(pedido);
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Erro ao carregar pedidos:', error);
        showToast('Erro ao carregar pedidos', 'error');
    }
}

async function atualizarTabelaPedidos() {
    try {
        const response = await fetch('/pedidos');
        const pedidos = await response.json();
        
        const tbody = document.getElementById('pedidos-tbody');
        const pedidosAtuais = tbody.getElementsByClassName('pedido-row');
        
        // Verificar se há novos pedidos ou alterações
        pedidos.forEach(pedido => {
            const pedidoExistente = document.getElementById(`pedido-${pedido.id}`);
            if (!pedidoExistente) {
                // Novo pedido - adicionar com animação
                const tr = criarLinhaPedido(pedido);
                tr.style.animation = 'slideIn 0.5s ease-out';
                tbody.insertBefore(tr, tbody.firstChild);
            }
        });

        // Remover pedidos que não existem mais
        Array.from(pedidosAtuais).forEach(row => {
            const id = parseInt(row.getAttribute('data-id'));
            if (!pedidos.find(p => p.id === id)) {
                row.style.animation = 'slideOut 0.5s ease-out';
                setTimeout(() => row.remove(), 500);
            }
        });
    } catch (error) {
        console.error('Erro ao atualizar pedidos:', error);
        showToast('Erro ao atualizar pedidos', 'error');
    }
}

function criarLinhaPedido(pedido) {
    const tr = document.createElement('tr');
    tr.id = `pedido-${pedido.id}`;
    tr.className = 'pedido-row';
    tr.setAttribute('data-id', pedido.id);
    
    tr.innerHTML = `
        <td>#${pedido.id}</td>
        <td>${pedido.cliente}</td>
        <td>${pedido.endereco}</td>
        <td>R$ ${pedido.total.toFixed(2)}</td>
        <td>${formatarData(pedido.data)}</td>
        <td>
            <button class="btn-ver-detalhes" onclick="verDetalhesPedido(${JSON.stringify(pedido).replace(/"/g, '&quot;')})">
                <i class="fas fa-eye"></i> Ver Detalhes
            </button>
            <button class="btn-excluir" onclick="deletarPedido(${pedido.id})">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    return tr;
}

function verDetalhesPedido(pedido) {
    const modal = document.getElementById('detailsModal');
    const detalhes = document.getElementById('pedido-detalhes');
    
    let itensHtml = pedido.itens.map(item => `
        <div class="pedido-item">
            <strong>${item.nome}</strong>
            <p>Quantidade: ${item.quantidade}</p>
            <p>Preço: R$ ${item.preco.toFixed(2)}</p>
        </div>
    `).join('');

    detalhes.innerHTML = `
        <div class="pedido-info">
            <p><strong>Cliente:</strong> ${pedido.cliente}</p>
            <p><strong>Endereço:</strong> ${pedido.endereco}</p>
            <p><strong>Data:</strong> ${formatarData(pedido.data)}</p>
            <p><strong>Total:</strong> R$ ${pedido.total.toFixed(2)}</p>
        </div>
        <div class="pedido-acoes">
            <button class="btn-excluir" onclick="deletarPedido(${pedido.id})">
                <i class="fas fa-trash"></i> Excluir Pedido
            </button>
            <button class="btn-imprimir" onclick="imprimirPedido(${pedido.id})">
                <i class="fas fa-print"></i> Imprimir
            </button>
        </div>
        <h4>Itens do Pedido:</h4>
        ${itensHtml}
    `;
    
    modal.classList.add('open');
}

function imprimirPedido(pedidoId) {
    const width = 800;
    const height = 600;
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;
    
    const printWindow = window.open(
        `/imprimir_pedido/${pedidoId}`,
        'ImprimirPedido',
        `width=${width},height=${height},left=${left},top=${top}`
    );

    // Fechar janela após impressão (opcional)
    if (printWindow) {
        printWindow.onafterprint = function() {
            printWindow.close();
        };
    }
}

async function deletarPedido(pedidoId) {
    if (!confirm('Tem certeza que deseja excluir este pedido?')) {
        return;
    }

    try {
        const response = await fetch(`/pedido/${pedidoId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showToast('Pedido excluído com sucesso!');
            carregarPedidos();
            
            const modal = document.getElementById('detailsModal');
            modal.classList.remove('open');
        } else {
            showToast('Erro ao excluir pedido: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro ao excluir pedido', 'error');
    }
}

function formatarData(dataString) {
    try {
        const data = new Date(dataString);
        return data.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        console.error('Erro ao formatar data:', e);
        return dataString;
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `admin-toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-bell"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Corrigir a função de notificação sonora
async function playNotificationSound() {
    try {
        // Caminho corrigido para o arquivo de som
        const audio = new Audio('/static/notification.mp3'); // Removido 'sounds/' do caminho
        audio.volume = 0.5;
        console.log('Tentando tocar som de notificação...');
        await audio.play();
        console.log('Som de notificação tocado com sucesso!');
    } catch (error) {
        console.error('Erro ao tocar som:', error);
    }
}

// Adicionar nova função para impressão automática
async function imprimirPedidoAutomatico(pedidoId) {
    try {
        const printWindow = window.open(
            `/imprimir_pedido/${pedidoId}`,
            'ImprimirPedido',
            'width=0,height=0,left=0,top=0'
        );

        if (printWindow) {
            // Fechar janela após impressão
            printWindow.onafterprint = function() {
                printWindow.close();
            };
        }
    } catch (error) {
        console.error('Erro na impressão automática:', error);
        showToast('Erro ao imprimir pedido', 'error');
    }
}

// Adicionar estilos para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-20px); }
    }
    
    .pedido-row {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);
