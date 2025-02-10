let cart = [];
let cartCount = 0;
let cartSubtotal = 0;
let toastContainer;

function createToastContainer() {
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'success', duration = 3000) {
    createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-in-out forwards';
        setTimeout(() => {
            toastContainer.removeChild(toast);
            if (toastContainer.children.length === 0) {
                document.body.removeChild(toastContainer);
                toastContainer = null;
            }
        }, 300);
    }, duration);
}

function toggleCart() {
    const cartModal = document.getElementById('cart-modal');
    cartModal.style.display = cartModal.style.display === 'none' ? 'block' : 'none';
}

function addToCart(name, price) {
    const item = cart.find(item => item.name === name);
    if (item) {
        item.quantity += 1;
    } else {
        cart.push({ name, price, quantity: 1 });
    }
    cartCount += 1;
    cartSubtotal += parseFloat(price.replace('R$', '').replace(',', '.'));
    updateCart();
}

function updateCart() {
    document.getElementById('cart-count').innerText = cartCount;
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = '';
    cart.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            ${item.name} - ${item.price} x ${item.quantity}
            <div class="quantity-controls">
                <button onclick="decreaseQuantity('${item.name}')">-</button>
                <span>${item.quantity}</span>
                <button onclick="increaseQuantity('${item.name}')">+</button>
            </div>
            <button onclick="removeFromCart('${item.name}')">Remover</button>
        `;
        cartItems.appendChild(li);
    });
    document.getElementById('cart-subtotal').innerText = `Subtotal: R$ ${cartSubtotal.toFixed(2).replace('.', ',')}`;
}

function increaseQuantity(name) {
    const item = cart.find(item => item.name === name);
    if (item) {
        item.quantity += 1;
        cartCount += 1;
        cartSubtotal += parseFloat(item.price.replace('R$', '').replace(',', '.'));
        updateCart();
    }
}

function decreaseQuantity(name) {
    const item = cart.find(item => item.name === name);
    if (item && item.quantity > 1) {
        item.quantity -= 1;
        cartCount -= 1;
        cartSubtotal -= parseFloat(item.price.replace('R$', '').replace(',', '.'));
        updateCart();
    }
}

function removeFromCart(name) {
    const item = cart.find(item => item.name === name);
    if (item) {
        cartCount -= item.quantity;
        cartSubtotal -= parseFloat(item.price.replace('R$', '').replace(',', '.')) * item.quantity;
        cart = cart.filter(item => item.name !== name);
        updateCart();
    }
}

function showCheckoutModal() {
    const checkoutModal = document.getElementById('checkout-modal');
    checkoutModal.style.display = 'block';
}

function closeCheckoutModal() {
    const checkoutModal = document.getElementById('checkout-modal');
    checkoutModal.style.display = 'none';
}

function checkout() {
    const form = document.getElementById('checkout-form');
    if (!form) {
        console.error('Formulário não encontrado');
        return;
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        if (cart.length === 0) {
            showToast('Adicione itens ao carrinho antes de finalizar o pedido', 'error');
            return;
        }

        const name = document.getElementById('name').value;
        const address = document.getElementById('address').value;

        if (!name || !address) {
            showToast('Por favor, preencha todos os campos', 'error');
            return;
        }

        const orderData = {
            name: name,
            address: address,
            items: JSON.stringify(cart),
            total: cartSubtotal
        };

        fetch('/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(orderData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            showToast(`Pedido #${data.order_id} realizado com sucesso!`);
            
            // Formatar mensagem do WhatsApp
            let mensagem = `*Novo Pedido #${data.order_id}*\n\n`;
            mensagem += `*Cliente:* ${document.getElementById('name').value}\n`;
            mensagem += `*Endereço:* ${document.getElementById('address').value}\n\n`;
            mensagem += `*Itens do Pedido:*\n`;
            
            cart.forEach(item => {
                mensagem += `▪ ${item.name} (${item.price}) x${item.quantity}\n`;
            });
            
            mensagem += `\n*Total: R$ ${cartSubtotal.toFixed(2)}*`;
            
            // Limpar carrinho
            cart = [];
            cartCount = 0;
            cartSubtotal = 0;
            updateCart();
            closeCheckoutModal();

            // Redirecionar para WhatsApp com a mensagem
            setTimeout(() => {
                const whatsappUrl = `https://wa.me/63991293427?text=${encodeURIComponent(mensagem)}`;
                window.location.href = whatsappUrl;
            }, 2000);
        })
        .catch(error => {
            console.error('Erro:', error);
            showToast('Erro ao realizar o pedido: ' + error.message, 'error');
        });
    });
}

function updateStatus(orderId, newStatus) {
    fetch(`/update_status/${orderId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Erro ao atualizar status: ' + data.error, 'error');
        } else {
            showToast('Status atualizado com sucesso!', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Erro ao atualizar status', 'error');
    });
}

// Nova função: ao fazer um "peido", redireciona para o WhatsApp
function fazerPeido() {
    window.location.href = "https://wa.me/63991293427";
}

// Exemplo de acionamento via clique em um botão com id "fart-button"
// document.getElementById('fart-button').addEventListener('click', fazerPeido);

// Inicializa o checkout quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    checkout();
});
