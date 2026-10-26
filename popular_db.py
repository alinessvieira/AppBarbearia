from datetime import datetime, timezone
from App_Barbearia import create_app
from App_Barbearia import database
from App_Barbearia.models import Usuario, Post, Servico

app = create_app()

def popular_banco():
    # Garante que o contexto da aplicação e as tabelas sejam criados antes de inserir dados
    with app.app_context():
        print("Verificando as tabelas no banco de dados...")
        database.create_all()
        
        print("Iniciando a inserção e atualização de dados fictícios...")

        # 1. Adicionando serviços (apenas se não existirem)
        servicos_dados = [
            ("Corte Degradê + Barba", 45.0),
            ("Corte Social Clássico", 35.0),
            ("Sobrancelha na Navalha", 15.0), # Exemplo de um serviço novo
        ]
        
        servicos_objetos = []
        for nome, valor in servicos_dados:
            # Verifica se o serviço já existe pelo nome
            servico_existente = Servico.query.filter_by(nome=nome).first()
            
            if not servico_existente:
                novo_servico = Servico(nome=nome, valor=valor)
                database.session.add(novo_servico)
                servicos_objetos.append(novo_servico)
                print(f"-> Serviço '{nome}' adicionado.")
            else:
                servicos_objetos.append(servico_existente) # Guarda para usar no agendamento depois se precisar

        # 2. Adicionando o barbeiro (apenas se não existir)
        email_barbeiro = "carlos.barbeiro@cortefacil.com.br"
        barbeiro = Usuario.query.filter_by(email=email_barbeiro).first()
        
        if not barbeiro:
            barbeiro = Usuario(
                username="Carlos Tesoura",
                email=email_barbeiro,
                senha="12345678",
                role="barbeiro",
                data_criacao=datetime.now(timezone.utc)
            )
            database.session.add(barbeiro)
            print("-> Barbeiro 'Carlos Tesoura' adicionado.")

        # 3. Lista de clientes
        clientes_dados = [
            ("Ana Clara", "ana.clara@email.com"),
            ("Bruno Souza", "bruno.souza@email.com"),
            ("Carlos Mendes", "carlos.mendes@email.com"),
            ("Daniela Alves", "daniela.alves@email.com"),
            ("Eduardo Costa", "eduardo.costa@email.com"),
            ("Fernanda Lima", "fernanda.lima@email.com"),
            ("Gabriel Silva", "gabriel.silva@email.com"),
            ("Helena Rocha", "helena.rocha@email.com"),
            ("Igor Martins", "igor.martins@email.com"),
            ("Juliana Ferreira", "juliana.ferreira@email.com"),
            ("Kleber Santos", "kleber.santos@email.com"),
            ("Larissa Gomes", "larissa.gomes@email.com"),
            ("Marcos Vinícius", "marcos.vinicius@email.com"),
            ("Natália Ribeiro", "natalia.ribeiro@email.com"),
            ("Otávio Augusto", "otavio.augusto@email.com"),
            ("Paula Fernandes", "paula.fernandes@email.com"),
            ("Quintino Barros", "quintino.barros@email.com"),
            ("Rafael Castro", "rafael.castro@email.com"),
            ("Sara Dias", "sara.dias@email.com"),
            ("Tiago Nogueira", "tiago.nogueira@email.com"),
            # Você pode adicionar novos clientes aqui no futuro, e o script só vai inserir os novos!
            ("Zeca Pagodinho", "zeca@email.com") 
        ]

        clientes_novos = []
        for nome, email in clientes_dados:
            # Verifica se o cliente já existe pelo e-mail
            cliente_existente = Usuario.query.filter_by(email=email).first()
            
            if not cliente_existente:
                novo_cliente = Usuario(
                    username=nome,
                    email=email,
                    senha="12345678",
                    role="cliente",
                    data_criacao=datetime.now(timezone.utc)
                )
                database.session.add(novo_cliente)
                clientes_novos.append(novo_cliente) # Guarda na lista de novos para usar no post
                print(f"-> Cliente '{nome}' adicionado.")

        # Salva tudo o que foi pendurado no banco (se não houver nada novo, o commit não faz nada, o que é ótimo)
        database.session.commit()

        # 4. Criando um post/agendamento de exemplo (só se criamos um cliente novo hoje)
        if clientes_novos and servicos_objetos:
            cliente_exemplo = clientes_novos[0]
            servico_exemplo = servicos_objetos[0]
            
            # Verifica se esse post específico já foi criado para evitar erro de duplicação
            post_existente = Post.query.filter_by(username=cliente_exemplo.username, hora="14:00").first()
            
            if not post_existente:
                post1 = Post(
                    username=cliente_exemplo.username,
                    cell="(19) 99999-9999",
                    servico=servico_exemplo.nome,
                    valor=servico_exemplo.valor,
                    hora="14:00",
                    data=datetime.now(timezone.utc).date(),
                    id_usuario=barbeiro.id,
                    avaliacao=5
                )
                database.session.add(post1)
                database.session.commit()
                print("-> Agendamento de exemplo criado com sucesso!")

        print("\nProcesso concluído com sucesso! Banco pronto e atualizado.")

if __name__ == "__main__":
    popular_banco()