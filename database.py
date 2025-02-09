import sqlite3
from datetime import datetime

def criar_banco():
    conn = sqlite3.connect('cardapio.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TIMESTAMP NOT NULL,
        valor_total DECIMAL(10,2) NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        produto TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes_pedido (
        pedido_id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        endereco TEXT NOT NULL,
        telefone TEXT NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def salvar_pedido(items_carrinho, dados_cliente):
    conn = sqlite3.connect('cardapio.db')
    cursor = conn.cursor()
    
    valor_total = sum(item['preco'] * item['quantidade'] for item in items_carrinho)
    
    cursor.execute('INSERT INTO pedidos (data, valor_total) VALUES (?, ?)',
                  (datetime.now(), valor_total))
    pedido_id = cursor.lastrowid
    
    for item in items_carrinho:
        cursor.execute('''
        INSERT INTO itens_pedido (pedido_id, produto, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?)
        ''', (pedido_id, item['nome'], item['quantidade'], item['preco']))
    
    cursor.execute('''
    INSERT INTO clientes_pedido (pedido_id, nome, endereco, telefone)
    VALUES (?, ?, ?, ?)
    ''', (pedido_id, dados_cliente['nome'], dados_cliente['endereco'], dados_cliente['telefone']))
    
    conn.commit()
    conn.close()
    return pedido_id

def buscar_pedidos():
    conn = sqlite3.connect('cardapio.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        p.id,
        p.data,
        p.valor_total,
        GROUP_CONCAT(
            i.quantidade || 'x ' || i.produto || ' (R$ ' || 
            printf('%.2f', i.preco_unitario) || ')'
            , ' | '
        ) as items_list
    FROM pedidos p
    LEFT JOIN itens_pedido i ON p.id = i.pedido_id
    GROUP BY p.id
    ORDER BY p.data DESC
    ''')
    
    pedidos = cursor.fetchall()
    conn.close()
    return [dict(row) for row in pedidos]

def buscar_novos_pedidos(ultimo_id):
    conn = sqlite3.connect('cardapio.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT 
        p.id,
        p.data,
        p.valor_total,
        GROUP_CONCAT(
            i.quantidade || 'x ' || i.produto || ' (R$ ' || 
            printf('%.2f', i.preco_unitario) || ')'
            , ' | '
        ) as items_list
    FROM pedidos p
    LEFT JOIN itens_pedido i ON p.id = i.pedido_id
    WHERE p.id > ?
    GROUP BY p.id
    ORDER BY p.data DESC
    ''', (ultimo_id,))
    
    pedidos = cursor.fetchall()
    conn.close()
    return [dict(row) for row in pedidos]
