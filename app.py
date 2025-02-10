from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import os
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit
import stat

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Caminho absoluto para o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'orders.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Garante que o diretório tem permissões corretas
try:
    if not os.path.exists(basedir):
        os.makedirs(basedir, mode=0o777)
    
    # Define permissões para o arquivo do banco de dados
    if os.path.exists(db_path):
        os.chmod(db_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
    
    # Define permissões para o diretório
    os.chmod(basedir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
    
    logger.info(f"Permissões definidas com sucesso para {db_path}")
except Exception as e:
    logger.error(f"Erro ao definir permissões: {str(e)}")

logger.debug(f"Caminho do banco de dados: {db_path}")

db = SQLAlchemy(app)

def create_database():
    try:
        with app.app_context():
            db.create_all()
            logger.debug("Banco de dados criado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {str(e)}")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Novo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.template_filter('fromjson')
def fromjson(value):
    return json.loads(value)

@app.route('/')
def home():
    return redirect(url_for('menu'))

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        return redirect(url_for('menu'))
    menu_categories = {
        'Sanduíches': [
            {'name': 'MISTO QUENTE', 'price': 'R$ 6,00', 'description': ''},
            {'name': 'X-SALADA', 'price': 'R$ 8,00', 'description': 'Pão, presunto, queijo e tomate'},
            {'name': 'X-BURGER', 'price': 'R$ 12,00', 'description': 'Pão, hambúrguer, presunto, queijo, alface e tomate'},
            {'name': 'X-BACON', 'price': 'R$ 18,00', 'description': 'Pão, hambúrguer, bacon, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-EGG', 'price': 'R$ 13,00', 'description': 'Pão, hambúrguer, ovo, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-CALABRESA', 'price': 'R$ 15,00', 'description': 'Pão, hambúrguer, calabresa, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-FRANGO COM CATUPIRY', 'price': 'R$ 18,00', 'description': 'Pão, filé de frango, catupiry, alface, presunto, queijo, tomate, milho, batata palha, maionese'},
            {'name': 'X-BIG DOG', 'price': 'R$ 12,00', 'description': 'Pão, carne moída, salsicha, milho, batata palha, alface e tomate'},
            {'name': 'X-A MODA DA CASA', 'price': 'R$ 22,00', 'description': 'Pão, hambúrguer, bacon, calabresa, ovo, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-CALABRESA ACEBOLADA', 'price': 'R$ 16,00', 'description': 'Pão, hambúrguer, calabresa, cebola, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-CREMOSO', 'price': 'R$ 15,00', 'description': 'Pão, hambúrguer, catupiry, chedar, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-3J', 'price': 'R$ 20,00', 'description': 'Pão, carne de sol, cebola, calabresa, ovo, pimenta, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-NORDESTINO', 'price': 'R$ 20,00', 'description': 'Pão, carne de sol, banana, bacon, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-TUDO', 'price': 'R$ 25,00', 'description': 'Pão, hambúrguer, frango, bacon, calabresa, salsicha, ovo, presunto, queijo, milho, batata palha, alface e tomate'},
            {'name': 'X-LIGHT', 'price': 'R$ 10,00', 'description': 'Pão, filé de frango, presunto, queijo, alface e tomate'}
        ],
        'Bebidas': [
            {'name': 'Refrigerante Lata', 'price': 'R$ 5,00', 'description': ''},
            {'name': 'Refrigerante 1L', 'price': 'R$ 9,00', 'description': ''},
            {'name': 'Refrigerante 2L', 'price': 'R$ 15,00', 'description': ''},
            {'name': 'Suco na Jarra (1,2L)', 'price': 'R$ 16,00', 'description': ''},
            {'name': 'Suco (Copo 400ml)', 'price': 'R$ 6,00', 'description': ''}
        ],
        'Pizzas': [
            {'name': '4 Queijos', 'price': '', 'description': 'Massa, molho, mussarela, catupiry, cheddar, orégano e tomate'},
            {'name': 'Calabresa', 'price': '', 'description': 'Massa, molho, mussarela, calabresa, cebola, orégano e tomate'},
            {'name': 'Bacon', 'price': '', 'description': 'Massa, molho, mussarela, bacon, milho, orégano e tomate'},
            {'name': 'Carne de Sol', 'price': '', 'description': 'Massa, molho, mussarela, carne de sol, catupiry, azeitona, cebola, orégano e tomate'},
            {'name': 'Frango com Catupiry', 'price': '', 'description': 'Massa, molho, mussarela, frango, catupiry, milho, orégano e tomate'},
            {'name': 'Mexicana', 'price': '', 'description': 'Massa, molho, mussarela, carne de sol, cheddar, banana, pimenta, cheddar, orégano e tomate'},
            {'name': 'A Moda da Casa', 'price': '', 'description': 'Massa, molho, mussarela, carne de sol, calabresa, bacon, azeitona, milho, orégano e tomate'},
            {'name': 'Portuguesa', 'price': '', 'description': 'Massa, molho, mussarela, calabresa, ovo, milho, cebola, orégano e tomate'},
            {'name': 'Baiana', 'price': '', 'description': 'Massa, molho, mussarela, calabresa ralada, pimenta, milho, azeitona, orégano e tomate'},
            {'name': '3 Carnes', 'price': '', 'description': 'Massa, molho, mussarela, lombo, calabresa, bacon, milho, azeitona, orégano e tomate'},
            {'name': 'Strogonoff de Frango', 'price': '', 'description': 'Massa, molho, strogonoff de frango, mussarela, batata palha, tomate e orégano'},
            {'name': 'Crocante', 'price': '', 'description': 'Massa, molho, Mussarela, Carne de sol, bacon, chedar, batata palha, milho, tomate e orégano'},
            {'name': 'Fran Bacon', 'price': '', 'description': 'Massa, molho, Mussarela, frango, bacon, chedar, milho, tomate e orégano'},
            {'name': 'Do Cheff', 'price': '', 'description': 'Massa, molho, Mussarela, carne de sol, bacon, banana, azeitona, milho, tomate e orégano'},
            {'name': 'Turbinada', 'price': '', 'description': 'Massa, molho, Mussarela, Catupiry, chedar, bacon, milho, tomate e orégano'},
            {'name': 'Banana com Canela (Pizza Doce)', 'price': 'R$ 59,00 (GG-12 Fatias), R$ 50,00 (G-10 Fatias)', 'description': 'Massa, creme de leite, mussarela, banana, leite condensado e canela'},
            {'name': 'Banana com Nutella', 'price': 'R$ 40,00 (M-6 Fatias)', 'description': 'Massa, creme de leite, Mussarela, banana, nutella'}
        ],
        'Pratos': [
            {'name': 'Filé com Fritas', 'price': 'R$ 22,00', 'description': 'Arroz branco, filé mignon picado, batata frita, salada'},
            {'name': 'Strogonoff', 'price': 'R$ 22,00', 'description': 'Arroz branco, strogonoff de frango, batata palha'},
            {'name': 'Arroz Carreteiro', 'price': 'R$ 20,00', 'description': 'Arroz com carne de sol, bacon, calabresa e salada'},
            {'name': 'Batata Frita', 'price': 'R$ 20,00', 'description': ''},
            {'name': 'Batata Frita Especial', 'price': 'R$ 26,00', 'description': 'Batata, bacon, cheddar, queijo e orégano'},
            {'name': 'Calabresa Acebolada', 'price': 'Inteira R$ 28,00, Meia R$ 18,00', 'description': ''},
            {'name': 'Filé na Chapa', 'price': 'Inteira R$ 82,00, Meia R$ 55,00', 'description': 'Arroz, farofa, salada filé Mignon picado, cebola, tomate, azeitona e queijo'},
            {'name': 'Iscas de Peixe', 'price': 'Inteira R$ 75,00, Meia R$ 48,00', 'description': 'Arroz, farofa, salada, filé de Tilápia picado, empanado e frito'},
            {'name': 'Macarronada de Frango', 'price': 'R$ 22,00', 'description': 'Macarrão Espaguete, Molho Branco, Frango, Milho, Queijo e Orégano'},
            {'name': 'Macarronada de Carne', 'price': 'R$ 22,00', 'description': 'Macarrão Espaguete, Molho Vermelho, Carne Moída, Milho, Queijo e Orégano'},
            {'name': 'Macarronada a Moda', 'price': 'R$ 25,00', 'description': 'Macarrão Espaguete, Molho Rosê, Frango, Bacon, Milho, Azeitona, Queijo e Orégano'},
            {'name': 'Panelinha de Frango', 'price': 'P R$ 45,00, M R$ 65,00, G R$ 85,00', 'description': 'Arroz, creme leite, catupiry, frango, milho, azeitona, queijo, tomate'},
            {'name': 'Panelinha de Carne de Sol', 'price': 'P R$ 45,00, M R$ 65,00, G R$ 85,00', 'description': 'Arroz, creme leite, catupiry, Carne de sol, bacon, milho, azeitona, queijo, banana frita'},
            {'name': 'Panelinha de Camarão', 'price': 'P R$ 55,00, M R$ 70,00, G R$ 90,00', 'description': 'Arroz, creme leite, catupiry, camarão, milho, queijo, tomate'}
        ],
        'Caldos': [
            {'name': 'Caldo de Frango', 'price': 'R$ 12,00', 'description': 'Acompanha: torradas e queijo'},
            {'name': 'Caldo de Carne', 'price': 'R$ 12,00', 'description': 'Acompanha: torradas e queijo'}
        ],
        'Açaí': [
            {'name': 'Açaí na Tijela', 'price': '300ml R$ 14,00, 500ml R$ 18,00', 'description': 'Acompanhamentos separados: Amendoim, Granola, Tapioca, Leite Condensado, Leite Pó e Banana'},
            {'name': 'Açaí Kids na Tigela', 'price': '300ml R$ 15,00', 'description': 'Disquete, Tubete, nutella, Jujuba, Leite pó, leite condensado, morango'},
            {'name': 'Açaí no Copo', 'price': '300ml R$ 13,00, 400ml R$ 14,00, 500ml R$ 15,00', 'description': 'Acompanhamento: Amendoim, Granola, Tapioca, Leite Condensado, Leite Pó e Banana'}
        ]
    }
    return render_template('menu.html', categories=menu_categories)

@app.route('/order', methods=['POST'])
def order():
    try:
        data = request.get_json()
        logger.debug(f"Dados recebidos no servidor: {data}")
        
        if not data:
            return jsonify({'error': "Dados do pedido não fornecidos"}), 400
        
        # Validação dos dados
        required_fields = ['name', 'address', 'items', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f"Campo obrigatório ausente: {field}"}), 400
        
        try:
            # Valida o formato do JSON de items
            items = json.loads(data['items']) if isinstance(data['items'], str) else data['items']
            # Converte items para string JSON se não for
            items_json = json.dumps(items) if not isinstance(data['items'], str) else data['items']
            
            # Converte total para float
            total = float(str(data['total']).replace('R$', '').replace(',', '.').strip())
            
            # Criar pedido
            new_order = Order(
                name=data['name'],
                address=data['address'],
                items=items_json,
                total=total,
                status='Novo',
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_order)
            db.session.commit()
            
            # Emite evento com dados formatados
            order_data = {
                'id': new_order.id,
                'name': new_order.name,
                'address': new_order.address,
                'items': items_json,
                'total': f"R$ {total:.2f}",
                'status': new_order.status,
                'created_at': new_order.created_at.strftime('%d/%m/%Y %H:%M')
            }
            socketio.emit('new_order', order_data)
            
            return jsonify({
                'message': 'Pedido realizado com sucesso!',
                'order_id': new_order.id
            })
            
        except json.JSONDecodeError:
            return jsonify({'error': "Formato inválido dos itens do pedido"}), 400
        except ValueError as e:
            return jsonify({'error': f"Erro ao converter dados: {str(e)}"}), 400
            
    except Exception as e:
        logger.error(f"Erro ao processar pedido: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': "Erro interno do servidor"}), 500

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    try:
        data = request.get_json()
        status = data.get('status')
        if not status:
            return jsonify({'error': 'Status não fornecido'}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Pedido não encontrado'}), 404

        order.status = status
        db.session.commit()
        return jsonify({'message': 'Status atualizado com sucesso'})
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Pedido não encontrado'}), 404

        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Pedido excluído com sucesso'})
    except Exception as e:
        logger.error(f"Erro ao excluir pedido: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin():
    try:
        with app.app_context():
            orders = Order.query.order_by(Order.id.desc()).all()
            logger.debug(f"Pedidos encontrados: {len(orders)}")
            return render_template('admin.html', orders=orders)
    except Exception as e:
        logger.error(f"Erro ao buscar pedidos: {str(e)}")
        return render_template('admin.html', orders=[], error=str(e))

@app.route('/admin/orders', methods=['GET'])
def get_orders():
    try:
        orders = Order.query.order_by(Order.id.desc()).all()
        orders_list = []
        for order in orders:
            orders_list.append({
                'id': order.id,
                'created_at': order.created_at.strftime('%d/%m/%Y %H:%M'),
                'name': order.name,
                'address': order.address,
                'items': order.items,  # já em string JSON
                'total': f"R$ {order.total:.2f}",
                'status': order.status
            })
        return jsonify(orders_list)
    except Exception as e:
        logger.error(f"Erro ao buscar pedidos: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Inicialização do banco de dados com tratamento de erros
def init_db():
    try:
        with app.app_context():
            db.create_all()
            # Define permissões após criar o banco
            os.chmod(db_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise

# Inicializa o banco de dados
init_db()

if __name__ == '__main__':
    socketio.run(app, debug=True)
