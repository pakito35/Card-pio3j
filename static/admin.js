document.addEventListener('DOMContentLoaded', () => {
    // Carregar dashboard inicial
    atualizarDashboard();

    // Iniciar SSE
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = function(event) {
        const novoPedido = JSON.parse(event.data);
        showToast(`Novo pedido recebido de ${novoPedido.cliente}!`);
        atualizarDashboard();
    };
});

// Manter apenas as funções relacionadas ao dashboard
async function atualizarDashboard() {
    try {
        const response = await fetch('/pedidos');
        const pedidos = await response.json();
        
        // Atualizar cards do dashboard
        document.querySelector('.total-pedidos').textContent = pedidos.length;
        
        const faturamentoTotal = pedidos.reduce((total, pedido) => total + pedido.total, 0);
        document.querySelector('.faturamento-total').textContent = `R$ ${faturamentoTotal.toFixed(2)}`;
        
        const hoje = new Date().toISOString().split('T')[0];
        const pedidosHoje = pedidos.filter(pedido => pedido.data.startsWith(hoje)).length;
        document.querySelector('.pedidos-hoje').textContent = pedidosHoje;
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
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