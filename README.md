# Sistema de Pedidos para Lanchonete

Sistema web para gerenciamento de pedidos com cardápio digital, painel administrativo e impressão automática de pedidos.

## Funcionalidades

- ✅ Cardápio digital interativo
- ✅ Carrinho de compras
- ✅ Envio de pedidos via WhatsApp
- ✅ Painel administrativo
- ✅ Impressão automática de pedidos
- ✅ Notificações em tempo real
- ✅ Gerenciamento de status dos pedidos
- ✅ WebSocket para atualizações instantâneas

## Requisitos

- Python 3.8+
- Flask
- SQLite
- Navegador moderno com JavaScript habilitado

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd <pasta-do-projeto>
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicialize o banco de dados:
```bash
flask shell
from app import db
db.create_all()
exit()
```

5. Execute o servidor:
```bash
python app.py
```

6. Acesse no navegador:
- Cardápio: http://localhost:5000
- Painel Admin: http://localhost:5000/admin

## Estrutura do Projeto

```
.
├── app.py              # Aplicação principal Flask
├── requirements.txt    # Dependências do projeto
├── static/            
│   ├── styles.css     # Estilos CSS
│   ├── scripts.js     # Scripts do cardápio
│   ├── print-manager.js    # Gerenciador de impressão
│   └── websocket-manager.js # Gerenciador WebSocket
├── templates/
│   ├── menu.html      # Template do cardápio
│   └── admin.html     # Template do painel admin
└── orders.db          # Banco de dados SQLite
```

## Configuração

1. Configuração do WhatsApp:
- Edite o número no arquivo `scripts.js`:
```javascript
const whatsappNumber = "seu-numero-aqui";
```

2. Configuração da impressora:
- Verifique se o navegador tem permissão para impressão
- Permita popups no navegador para impressão automática

## Tecnologias

- Backend: Flask, SQLAlchemy, Flask-SocketIO
- Frontend: HTML5, CSS3, JavaScript
- Banco de dados: SQLite
- Comunicação: WebSocket
- Impressão: Web Print API

## Contribuição

1. Faça um Fork
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## Suporte

Para reportar bugs ou solicitar funcionalidades, abra uma issue no repositório.
