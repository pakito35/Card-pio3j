from flask import Flask, render_template, jsonify, request, session, Response
from database import criar_banco, salvar_pedido, buscar_pedidos, buscar_novos_pedidos
from decorators import read_only_db
import sqlite3
import json
import time

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar sessions

menu = {
    "Sanduíches": [
        {
            "nome": "MISTO QUENTE",
            "descricao": "Pão, presunto e queijo",
            "preco": 6.00,
            "imagem": "/static/images/misto.jpg"
        },
        {
            "nome": "X-SALADA",
            "descricao": "Pão, presunto, queijo e tomate",
            "preco": 8.00,
            "imagem": "/static/images/x-salada.jpg"
        },
        # ...outros sanduíches...
        {
            "nome": "X-TUDO",
            "descricao": "Pão, hambúrguer, frango, bacon, calabresa, salsicha, ovo, presunto, queijo, milho, batata palha, alface e tomate",
            "preco": 25.00,
            "imagem": "/static/images/x-tudo.jpg"
        }
    ],
    "Bebidas": [
        {
            "nome": "Refrigerante Lata",
            "descricao": "350ml",
            "preco": 5.00,
            "imagem": "/static/images/refri-lata.jpg"
        },
        {
            "nome": "Refrigerante 1L",
            "descricao": "1 Litro",
            "preco": 9.00,
            "imagem": "/static/images/refri-1l.jpg"
        },
        # ...outras bebidas...
    ],
    "Pizzas": [
        {
            "nome": "4 Queijos",
            "descricao": "Massa, molho, mussarela, catupiry, cheddar, orégano e tomate",
            "preco": 59.00,
            "imagem": "/static/images/pizza-4queijos.jpg"
        },
        {
            "nome": "Calabresa",
            "descricao": "Massa, molho, mussarela, calabresa, cebola, orégano e tomate",
            "preco": 59.00,
            "imagem": "/static/images/pizza-calabresa.jpg"
        },
        # ...outras pizzas...
    ],
    "Jantinha": [
        {
            "nome": "Filé com Fritas",
            "descricao": "Arroz branco, filé mignon picado, batata frita, salada",
            "preco": 22.00,
            "imagem": "/static/images/file-fritas.jpg"
        },
        # ...outras jantinhas...
    ],
    "Porções": [
        {
            "nome": "Batata Frita",
            "descricao": "Porção de batata frita crocante",
            "preco": 20.00,
            "imagem": "/static/images/batata-frita.jpg"
        },
        # ...outras porções...
    ],
    "Macarronada": [
        {
            "nome": "Macarronada de Frango",
            "descricao": "Macarrão Espaguete, Molho Branco, Frango, Milho, Queijo e Orégano",
            "preco": 22.00,
            "imagem": "/static/images/macarronada-frango.jpg"
        },
        # ...outras macarronadas...
    ],
    "Panelinha": [
        {
            "nome": "Frango (P)",
            "descricao": "Arroz, creme leite, catupiry, frango, milho, azeitona, queijo, tomate",
            "preco": 45.00,
            "imagem": "/static/images/panelinha-frango.jpg"
        },
        # ...outras panelinhas...
    ],
    "Caldos": [
        {
            "nome": "Caldo de Frango",
            "descricao": "Acompanha: torradas e queijo",
            "preco": 12.00,
            "imagem": "/static/images/caldo-frango.jpg"
        },
        # ...outros caldos...
    ],
    "Açaí": [
        {
            "nome": "Açaí na Tijela 300ml",
            "descricao": "Acompanhamentos: Amendoim, Granola, Tapioca, Leite Condensado, Leite Pó e Banana",
            "preco": 14.00,
            "imagem": "/static/images/acai-tigela.jpg"
        },
        # ...outros açaís...
    ]
}

ultimo_pedido_id = 0

@app.route('/pedidos-stream')
@read_only_db
def pedidos_stream():
    def event_stream():
        global ultimo_pedido_id
        while True:
            try:
                pedidos = buscar_novos_pedidos(ultimo_pedido_id)
                if pedidos:
                    ultimo_pedido_id = max(p['id'] for p in pedidos)
                    yield f"data: {json.dumps(pedidos)}\n\n"
            except Exception as e:
                print(f"Erro no stream: {e}")
            time.sleep(3)

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/')
def index():
    if 'carrinho' not in session:
        session['carrinho'] = []
    return render_template('index.html', menu=menu, session=session)

@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    try:
        data = request.json
        item = {
            'nome': data['nome'],
            'preco': float(data['preco']),
            'quantidade': 1
        }
        
        carrinho = session.get('carrinho', [])
        
        # Verifica se o item já existe no carrinho
        item_existente = next((i for i in carrinho if i['nome'] == item['nome']), None)
        if item_existente:
            item_existente['quantidade'] += 1
        else:
            carrinho.append(item)
        
        session['carrinho'] = carrinho
        return jsonify({
            'status': 'success',
            'message': 'Item adicionado ao carrinho',
            'total_items': len(carrinho)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/carrinho', methods=['GET'])
def ver_carrinho():
    carrinho = session.get('carrinho', [])
    total = sum(item['preco'] * item['quantidade'] for item in carrinho)
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/atualizar_quantidade', methods=['POST'])
def atualizar_quantidade():
    data = request.json
    carrinho = session.get('carrinho', [])
    
    for item in carrinho:
        if item['nome'] == data['nome']:

            item['quantidade'] = int(data['quantidade'])
            break
    
    session['carrinho'] = carrinho
    return jsonify({'status': 'success'})

@app.route('/remover_item', methods=['POST'])
def remover_item():
    data = request.json
    carrinho = session.get('carrinho', [])
    carrinho = [item for item in carrinho if item['nome'] != data['nome']]
    session['carrinho'] = carrinho
    return jsonify({'status': 'success'})

@app.route('/finalizar_pedido', methods=['POST'])
@read_only_db
def finalizar_pedido():
    try:
        carrinho = session.get('carrinho', [])
        if not carrinho:
            return jsonify({'status': 'error', 'message': 'Carrinho vazio'})
        
        dados_cliente = request.json
        pedido_id = salvar_pedido(carrinho, dados_cliente)
        session['carrinho'] = []
        return jsonify({'status': 'success', 'pedido_id': pedido_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin')
@read_only_db
def admin():
    pedidos = buscar_pedidos()
    return render_template('admin.html', pedidos=pedidos)

@app.route('/excluir_pedido/<int:pedido_id>', methods=['DELETE'])
@read_only_db
def excluir_pedido(pedido_id):
    try:
        conn = sqlite3.connect('cardapio.db')
        cursor = conn.cursor()
        
        # Primeiro exclui os itens do pedido
        cursor.execute('DELETE FROM itens_pedido WHERE pedido_id = ?', (pedido_id,))
        # Depois exclui o pedido
        cursor.execute('DELETE FROM pedidos WHERE id = ?', (pedido_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    criar_banco()
    # Modificar para usar configurações de produção
    app.run(host='0.0.0.0', port=8080, debug=False)
