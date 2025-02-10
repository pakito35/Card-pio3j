
import os
import stat
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_permissions():
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'orders.db')
        
        # Define permissões para o diretório
        os.chmod(basedir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logger.info(f"Permissões do diretório atualizadas: {basedir}")
        
        # Define permissões para o banco de dados
        if os.path.exists(db_path):
            os.chmod(db_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            logger.info(f"Permissões do banco atualizadas: {db_path}")
        else:
            logger.warning(f"Banco de dados não encontrado: {db_path}")
            
        logger.info("Permissões corrigidas com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao corrigir permissões: {str(e)}")
        raise

if __name__ == "__main__":
    fix_permissions()