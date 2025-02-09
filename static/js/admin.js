function imprimirPedido(pedidoId, pedidoElement) {
    const conteudo = pedidoElement.cloneNode(true);
    
    // Remove o botão de impressão do clone
    const btnImprimir = conteudo.querySelector('.imprimir-btn');
    btnImprimir.remove();
    
    // Cria uma nova janela para impressão
    const janela = window.open('', '', 'height=600,width=800');
    janela.document.write('<html><head><title>Pedido #' + pedidoId + '</title>');
    
    // Adiciona estilos para impressão
    janela.document.write(`
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
            }
            .pedido-card {
                border: 1px solid #ccc;
                padding: 20px;
                border-radius: 8px;
            }
            .pedido-header {
                border-bottom: 1px solid #ccc;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }
            .pedido-id {
                font-size: 1.2em;
                font-weight: bold;
            }
            .pedido-data {
                color: #666;
            }
            .pedido-items {
                margin: 15px 0;
            }
            .pedido-item {
                padding: 5px 0;
                border-bottom: 1px solid #eee;
            }
            .pedido-total {
                font-weight: bold;
                font-size: 1.2em;
                text-align: right;
            }
            @media print {
                body {
                    padding: 0;
                }
                .pedido-card {
                    border: none;
                }
            }
        </style>
    `);
    
    janela.document.write('</head><body>');
    janela.document.write(conteudo.outerHTML);
    janela.document.write('</body></html>');
    janela.document.close();
    
    // Aguarda o carregamento do conteúdo
    janela.onload = function() {
        janela.print();
        setTimeout(function() {
            janela.close();
        }, 100);
    };
}

async function excluirPedido(pedidoId, elemento) {
    if (confirm('Tem certeza que deseja excluir este pedido?')) {
        try {
            const response = await fetch(`/excluir_pedido/${pedidoId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                elemento.remove();
                toast.show('Pedido excluído com sucesso!');
                
                // Se não houver mais pedidos, mostra mensagem
                const pedidosList = document.querySelector('.pedidos-list');
                if (!pedidosList.querySelector('.pedido-card')) {
                    pedidosList.innerHTML = '<p class="no-pedidos">Nenhum pedido realizado ainda.</p>';
                }
            } else {
                toast.show('Erro ao excluir pedido', 'error');
            }
        } catch (error) {
            console.error('Erro ao excluir pedido:', error);
            toast.show('Erro ao excluir pedido', 'error');
        }
    }
}

// Função para adicionar novo pedido à lista
function adicionarNovoPedido(pedido) {
    const pedidosList = document.querySelector('.pedidos-list');
    const noPedidos = document.querySelector('.no-pedidos');
    
    if (noPedidos) {
        noPedidos.remove();
    }

    const pedidoHtml = `
        <div class="pedido-card" data-id="${pedido.id}">
            <div class="pedido-header">
                <span class="pedido-id">Pedido #${pedido.id}</span>
                <span class="pedido-data">${pedido.data}</span>
            </div>
            <div class="pedido-items">
                ${pedido.items_list ? pedido.items_list.split(' | ').map(item => 
                    `<div class="pedido-item">${item}</div>`
                ).join('') : '<div class="pedido-item">Sem itens</div>'}
            </div>
            <div class="pedido-footer">
                <span class="pedido-total">Total: R$ ${parseFloat(pedido.valor_total).toFixed(2)}</span>
                <div class="pedido-acoes">
                    <button class="imprimir-btn" onclick="imprimirPedido(${pedido.id}, this.closest('.pedido-card'))">
                        <i class="fas fa-print"></i> Imprimir
                    </button>
                    <button class="excluir-btn" onclick="excluirPedido(${pedido.id}, this.closest('.pedido-card'))">
                        <i class="fas fa-trash"></i> Excluir
                    </button>
                </div>
            </div>
        </div>
    `;
    
    pedidosList.insertAdjacentHTML('afterbegin', pedidoHtml);
    
    // Toca um som e mostra notificação
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.play();
    
    // Adiciona efeito de destaque ao novo pedido
    const novoPedido = pedidosList.querySelector(`[data-id="${pedido.id}"]`);
    novoPedido.style.animation = 'novoPedido 2s ease-out';
    
    toast.show('Novo pedido recebido!');
}

// Inicializa o EventSource para receber atualizações em tempo real
const eventSource = new EventSource('/pedidos-stream');
eventSource.onmessage = function(event) {
    try {
        const pedidos = JSON.parse(event.data);
        pedidos.forEach(pedido => {
            // Verifica se o pedido já existe na página
            if (!document.querySelector(`.pedido-card[data-id="${pedido.id}"]`)) {
                adicionarNovoPedido(pedido);
            }
        });
    } catch (error) {
        console.error('Erro ao processar novo pedido:', error);
    }
};
