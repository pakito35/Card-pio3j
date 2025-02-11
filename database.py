import sqlite3
import os
from datetime import datetime

def check_database():
    """Verifica se o banco de dados existe e cria se necessário"""
    db_exists = os.path.exists('restaurant.db')
    if not db_exists:
        print("Banco de dados não encontrado. Criando novo banco de dados...")
        init_db()
        return False
    return True

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()
        
        print("Criando tabelas...")
        
        # Criar tabela de pedidos
        c.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                endereco TEXT NOT NULL,
                total REAL NOT NULL,
                data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de itens do pedido
        c.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            )
        ''')
        
        conn.commit()
        print("Banco de dados criado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False
    finally:
        conn.close()

def salvar_pedido(cliente, endereco, itens, total):
    conn = sqlite3.connect('restaurant.db')
    c = conn.cursor()
    
    try:
        # Inserir pedido
        c.execute('''
            INSERT INTO pedidos (cliente, endereco, total)
            VALUES (?, ?, ?)
        ''', (cliente, endereco, total))
        
        pedido_id = c.lastrowid
        
        # Inserir itens do pedido
        for item in itens:
            c.execute('''
                INSERT INTO itens_pedido (pedido_id, nome, preco, quantidade)
                VALUES (?, ?, ?, ?)
            ''', (pedido_id, item['nome'], item['preco'], item['quantidade']))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao salvar pedido: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_pedidos():
    conn = sqlite3.connect('restaurant.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM pedidos ORDER BY data_pedido DESC
    ''')
    pedidos = c.fetchall()
    
    resultado = []
    for pedido in pedidos:
        c.execute('SELECT * FROM itens_pedido WHERE pedido_id = ?', (pedido[0],))
        itens = c.fetchall()
        
        resultado.append({
            'id': pedido[0],
            'cliente': pedido[1],
            'endereco': pedido[2],
            'total': pedido[3],
            'data': pedido[4],
            'itens': [{
                'nome': item[2],
                'preco': item[3],
                'quantidade': item[4]
            } for item in itens]
        })
    
    conn.close()
    return resultado

def deletar_pedido(pedido_id):
    conn = sqlite3.connect('restaurant.db')
    c = conn.cursor()
    
    try:
        # Deletar itens do pedido primeiro (devido à chave estrangeira)
        c.execute('DELETE FROM itens_pedido WHERE pedido_id = ?', (pedido_id,))
        
        # Deletar o pedido
        c.execute('DELETE FROM pedidos WHERE id = ?', (pedido_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar pedido: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
