let cart = [];
let isCartOpen = false;  // Adicionado para controlar o estado do carrinho

// Adicionar função showToast no início do arquivo
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');
    
    toast.className = 'toast';
    toast.classList.add(type);
    toast.classList.add('show');
    toastMessage.textContent = message;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    const cartIcon = document.querySelector('.cart-icon');
    const cartPanel = document.querySelector('.cart-panel');
    const closeCart = document.querySelector('.close-cart');
    const addButtons = document.querySelectorAll('.btn-adicionar');
    const btnFinalizar = document.querySelector('.btn-finalizar');
    const modal = document.getElementById('checkoutModal');
    const closeModal = document.querySelector('.close-modal');
    const checkoutForm = document.getElementById('checkoutForm');

    // Fechar carrinho clicando fora dele
    document.addEventListener('click', (e) => {
        if (isCartOpen && !cartPanel.contains(e.target) && !cartIcon.contains(e.target)) {
            closeCartPanel();
        }
    });

    cartIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleCart();
    });

    closeCart.addEventListener('click', () => {
        closeCartPanel();
    });

    cartPanel.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    addButtons.forEach(button => {
        button.addEventListener('click', () => {
            const menuItem = button.closest('.menu-item');
            const nome = menuItem.querySelector('h3').textContent;
            const preco = parseFloat(menuItem.querySelector('.preco').textContent.replace('R$ ', ''));
            
            addToCart({ nome, preco });
            if (!isCartOpen) {
                toggleCart(); // Abre o carrinho ao adicionar um item
            }
        });
    });

    btnFinalizar.addEventListener('click', () => {
        if (cart.length > 0) {
            modal.classList.add('open');
        } else {
            showToast('Adicione itens ao carrinho primeiro!', 'error');
        }
    });

    closeModal.addEventListener('click', () => {
        modal.classList.remove('open');
    });

    checkoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nome = document.getElementById('nome').value;
        const endereco = document.getElementById('endereco').value;
        
        const pedido = {
            cliente: nome,
            endereco: endereco,
            itens: cart,
            total: cart.reduce((sum, item) => sum + (item.preco * item.quantidade), 0),
            data: new Date().toISOString().slice(0, 19).replace('T', ' ') // Formato: YYYY-MM-DD HH:MM:SS
        };
        
        try {
            const response = await fetch('/pedido', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(pedido)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                showToast('Pedido realizado com sucesso!');
                
                // Limpar carrinho e formulário
                cart = [];
                updateCartDisplay();
                checkoutForm.reset();
                
                // Fechar modal e carrinho
                modal.classList.remove('open');
                closeCartPanel();

                // Abrir WhatsApp após delay
                setTimeout(() => {
                    if (data.whatsapp_link) {
                        window.open(data.whatsapp_link, '_blank');
                    }
                }, 1000);
            } else {
                throw new Error(data.message || 'Erro ao realizar pedido');
            }
        } catch (error) {
            console.error('Erro ao enviar pedido:', error);
            showToast(`Erro ao enviar pedido: ${error.message}`, 'error');
        }
    });

    // Fechar modal clicando fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('open');
        }
    });
});

function toggleCart() {
    const cartPanel = document.querySelector('.cart-panel');
    isCartOpen = !isCartOpen;
    cartPanel.classList.toggle('open');
}

function closeCartPanel() {
    const cartPanel = document.querySelector('.cart-panel');
    isCartOpen = false;
    cartPanel.classList.remove('open');
}

function addToCart(item) {
    const existingItem = cart.find(i => i.nome === item.nome);
    
    if (existingItem) {
        existingItem.quantidade += 1;
    } else {
        cart.push({ ...item, quantidade: 1 });
    }
    
    updateCartDisplay();
}

function removeFromCart(nome) {
    cart = cart.filter(item => item.nome !== nome);
    updateCartDisplay();
}

function updateQuantity(nome, delta) {
    const item = cart.find(i => i.nome === nome);
    if (item) {
        item.quantidade += delta;
        if (item.quantidade <= 0) {
            removeFromCart(nome);
        }
    }
    updateCartDisplay();
}

function updateCartDisplay() {
    const cartItems = document.querySelector('.cart-items');
    const cartCount = document.querySelector('.cart-count');
    const totalValue = document.querySelector('.total-value');
    
    cartItems.innerHTML = '';
    let total = 0;
    let count = 0;

    cart.forEach(item => {
        count += item.quantidade;
        total += item.preco * item.quantidade;
        
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <div class="cart-item-info">
                <h4 class="cart-item-title">${item.nome}</h4>
                <span class="cart-item-price">R$ ${item.preco.toFixed(2)}</span>
            </div>
            <div class="cart-item-controls">
                <div class="quantity-control">
                    <button class="btn-quantity" onclick="updateQuantity('${item.nome}', -1)">-</button>
                    <span>${item.quantidade}</span>
                    <button class="btn-quantity" onclick="updateQuantity('${item.nome}', 1)">+</button>
                </div>
                <button class="btn-remove" onclick="removeFromCart('${item.nome}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        cartItems.appendChild(itemElement);
    });

    cartCount.textContent = count;
    totalValue.textContent = `R$ ${total.toFixed(2)}`;
}
