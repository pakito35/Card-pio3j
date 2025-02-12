from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from database import check_database, salvar_pedido, get_pedidos, deletar_pedido
import json
import time
import sqlite3
from threading import Thread, Lock

app = Flask(__name__)

# Verificar e inicializar o banco de dados
if not check_database():
    print("Houve um problema ao criar o banco de dados!")
    exit(1)

# Dados do cardápio
menu = {
    'pratos_principais': [
        {'nome': 'Feijoada', 'preco': 45.90, 'descricao': 'Feijoada completa com arroz, couve e farofa'},
        {'nome': 'Picanha', 'preco': 89.90, 'descricao': 'Picanha grelhada com arroz, feijão e vinagrete'},
        {'nome': 'Salmão', 'preco': 68.90, 'descricao': 'Filé de salmão grelhado com legumes'}
    ],
    'sobremesas': [
        {'nome': 'Pudim', 'preco': 12.90, 'descricao': 'Pudim de leite condensado'},
        {'nome': 'Mousse', 'preco': 10.90, 'descricao': 'Mousse de chocolate'}
    ],
    'bebidas': [
        {'nome': 'Refrigerante', 'preco': 6.90, 'descricao': 'Lata 350ml'},
        {'nome': 'Suco Natural', 'preco': 8.90, 'descricao': 'Diversos sabores'}
    ]
}

# Variável global para armazenar o último ID de pedido
ultimo_pedido_id = 0
pedido_lock = Lock()

def get_ultimo_pedido_id():
    conn = sqlite3.connect('restaurant.db')
    c = conn.cursor()
    c.execute('SELECT MAX(id) FROM pedidos')
    max_id = c.fetchone()[0] or 0
    conn.close()
    return max_id

def check_novos_pedidos():
    global ultimo_pedido_id
    while True:
        with pedido_lock:
            atual_id = get_ultimo_pedido_id()
            if atual_id > ultimo_pedido_id:
                ultimo_pedido_id = atual_id
                return True
        time.sleep(0.5)  # Reduzido de 1 segundo para 0.5 segundos

@app.route('/stream')
def stream():
    def event_stream():
        global ultimo_pedido_id
        if ultimo_pedido_id == 0:
            ultimo_pedido_id = get_ultimo_pedido_id()
            
        while True:
            try:
                if check_novos_pedidos():
                    pedidos = get_pedidos()
                    if pedidos:
                        novo_pedido = next((p for p in pedidos if p['id'] == ultimo_pedido_id), None)
                        if novo_pedido:
                            yield f"data: {json.dumps(novo_pedido)}\n\n"
                time.sleep(0.5)  # Reduzido de 1 segundo para 0.5 segundos
            except Exception as e:
                print(f"Erro no stream: {e}")
                time.sleep(0.5)  # Reduzido aqui também

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/')
def home():
    return render_template('menu.html', menu=menu)

@app.route('/pedido', methods=['POST'])
def fazer_pedido():
    data = request.json
    
    if salvar_pedido(
        cliente=data['cliente'],
        endereco=data['endereco'],
        itens=data['itens'],
        total=data['total']
    ):
        return jsonify({'status': 'success', 'message': 'Pedido salvo com sucesso!'})
    else:
        return jsonify({'status': 'error', 'message': 'Erro ao salvar pedido'}), 500

@app.route('/pedido/<int:pedido_id>', methods=['DELETE'])
def excluir_pedido(pedido_id):
    if deletar_pedido(pedido_id):
        return jsonify({'status': 'success', 'message': 'Pedido excluído com sucesso!'})
    else:
        return jsonify({'status': 'error', 'message': 'Erro ao excluir pedido'}), 500

@app.route('/pedidos')
def listar_pedidos():
    return jsonify(get_pedidos())

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/pedidos-lista')
def pedidos_lista():
    return render_template('pedidos.html')

# Remover rota específica para sons já que o arquivo está na pasta static raiz
# @app.route('/static/sounds/<path:filename>')
# def serve_sound(filename):
#     return send_from_directory('static/sounds', filename)

@app.route('/imprimir_pedido/<int:pedido_id>')
def imprimir_pedido(pedido_id):
    try:
        pedidos = get_pedidos()
        pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
        if pedido:
            # Formatar a data do pedido
            from datetime import datetime
            data = datetime.strptime(pedido['data'], '%Y-%m-%d %H:%M:%S')
            pedido['data'] = data.strftime('%d/%m/%Y %H:%M')
            
            return render_template('print_pedido.html', pedido=pedido)
        return 'Pedido não encontrado', 404
    except Exception as e:
        print(f"Erro ao gerar impressão: {e}")
        return 'Erro ao gerar impressão', 500

if __name__ == '__main__':
    app.run(debug=True)
