from functools import wraps
from flask import jsonify

def read_only_db(f):
    """Decorator para controlar o acesso de escrita ao banco de dados"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if "readonly database" in str(e).lower():
                return jsonify({
                    'status': 'error',
                    'message': 'Sistema em modo somente leitura no momento'
                }), 403
            raise e
    return decorated_function

# Importante: garantir que o decorator seja exportado
__all__ = ['read_only_db']
