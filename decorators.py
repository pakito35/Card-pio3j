from functools import wraps
from flask import g, abort
import sqlite3

def read_only_db(f):
    """Decorator para controlar o acesso de escrita ao banco de dados"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Abre conexão em modo somente leitura
            g.db = sqlite3.connect('file:cardapio.db?mode=ro', uri=True)
            g.db.row_factory = sqlite3.Row
            result = f(*args, **kwargs)
            return result
        except sqlite3.OperationalError as e:
            if "readonly" in str(e):
                abort(403, description="Operação de escrita não permitida no modo somente leitura")
            raise
        finally:
            if hasattr(g, 'db'):
                g.db.close()
    return decorated_function

# Importante: garantir que o decorator seja exportado
__all__ = ['read_only_db']
