# app.py na raiz do projeto

from App_Barbearia import create_app, iniciar_servico_lembretes
from App_Barbearia import database  # Importe a instância do seu banco (pode se chamar db ou database dependendo do seu código)

# Cria a instância da aplicação que o Flask e o Flask-Migrate irão usar
app = create_app()

if __name__ == '__main__':
    # Cria as tabelas no banco de dados se elas não existirem
    with app.app_context():
        database.create_all()
        
    iniciar_servico_lembretes(app)
    app.run(debug=True)