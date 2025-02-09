document.addEventListener('DOMContentLoaded', function() {
    const btnsAdicionar = document.querySelectorAll('.pedir-button');
    
    btnsAdicionar.forEach(btn => {
        btn.addEventListener('click', async function() {
            const menuItem = this.closest('.menu-item');
            const nome = menuItem.querySelector('h3').textContent;
            const preco = parseFloat(menuItem.querySelector('.preco').textContent.replace('R$ ', ''));
            
            try {
                const response = await fetch('/adicionar_ao_carrinho', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ nome, preco })
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    // Atualiza o contador do carrinho
                    const contador = document.querySelector('.carrinho-contador');
                    const atual = parseInt(contador.textContent);
                    contador.textContent = atual + 1;
                    
                    // Mostra o toast de sucesso
                    toast.show(`${nome} adicionado ao carrinho!`);
                    
                    // Animação do ícone do carrinho
                    const carrinhoIcon = document.querySelector('.carrinho-icon');
                    carrinhoIcon.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        carrinhoIcon.style.transform = 'scale(1)';
                    }, 200);
                }
            } catch (error) {
                console.error('Erro ao adicionar item:', error);
                toast.show('Erro ao adicionar item ao carrinho', 'error');
            }
        });
    });
});
