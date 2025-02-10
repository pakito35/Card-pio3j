class WebSocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
    }

    init() {
        this.socket = io();

        this.socket.on('connect', () => {
            console.log('Conectado ao WebSocket');
            this.connected = true;
        });

        this.socket.on('disconnect', () => {
            console.log('Desconectado do WebSocket');
            this.connected = false;
        });

        this.socket.on('new_order', async (order) => {
            console.log('Novo pedido recebido:', order);
            
            // Tocar som de notificação
            playNotificationSound();
            
            // Mostrar notificação toast
            showToast(`Novo pedido #${order.id} recebido!`, 'success');
            
            // Atualizar lista de pedidos
            fetchOrders();
            
            // Imprimir pedido automaticamente
            try {
                await this.printNewOrder(order);
                showToast(`Pedido #${order.id} impresso automaticamente`, 'success');
            } catch (error) {
                console.error('Erro ao imprimir:', error);
                showToast(`Erro ao imprimir pedido #${order.id}`, 'error');
            }
        });
    }

    async printNewOrder(order) {
        const printContent = this.generatePrintContent(order);
        const printWindow = window.open('', `Print_${order.id}`, 'width=600,height=800');
        
        if (!printWindow) {
            throw new Error('Popup bloqueado. Por favor, permita popups para impressão.');
        }

        printWindow.document.write(printContent);
        printWindow.document.close();

        return new Promise((resolve, reject) => {
            printWindow.onload = function() {
                try {
                    printWindow.print();
                    setTimeout(() => {
                        printWindow.close();
                        resolve();
                    }, 1000);
                } catch (error) {
                    reject(error);
                }
            };
        });
    }

    generatePrintContent(order) {
        const items = JSON.parse(order.items);
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Pedido #${order.id}</title>
                <style>
                    @page { size: 80mm auto; margin: 0; }
                    body { 
                        font-family: 'Courier New', monospace;
                        margin: 0;
                        padding: 10px;
                        font-size: 12px;
                        width: 80mm;
                    }
                    .header { text-align: center; margin-bottom: 20px; border-bottom: 1px dashed #000; padding-bottom: 10px; }
                    .header h2 { margin: 0; font-size: 16px; }
                    .info-row { margin: 5px 0; display: flex; justify-content: space-between; }
                    .items { margin: 10px 0; border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding: 10px 0; }
                    .total { text-align: right; font-weight: bold; margin: 10px 0; }
                    .footer { text-align: center; margin-top: 20px; font-size: 10px; border-top: 1px dashed #000; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>COMPROVANTE DE PEDIDO</h2>
                    <p>#${order.id}</p>
                    <p>${order.created_at}</p>
                </div>
                <div class="info-row">
                    <span>Cliente:</span>
                    <span>${order.name}</span>
                </div>
                <div class="info-row">
                    <span>Endereço:</span>
                    <span>${order.address}</span>
                </div>
                <div class="items">
                    ${items.map(item => 
                        `<div class="info-row">
                            <span>${item.name} x${item.quantity}</span>
                            <span>${item.price}</span>
                        </div>`
                    ).join('')}
                </div>
                <div class="total">
                    Total: ${order.total}
                </div>
                <div class="footer">
                    <p>Status: ${order.status}</p>
                    <p>Agradecemos a preferência!</p>
                </div>
                <script>
                    window.onload = () => window.print();
                </script>
            </body>
            </html>
        `;
    }

    isConnected() {
        return this.connected;
    }
}

// Inicializar globalmente
window.wsManager = new WebSocketManager();
document.addEventListener('DOMContentLoaded', () => {
    window.wsManager.init();
});
