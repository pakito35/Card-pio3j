from app import app
from database import criar_banco

if __name__ == "__main__":
    criar_banco()
    app.run()
