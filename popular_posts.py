from datetime import date, timedelta
from App_Barbearia import create_app
from App_Barbearia import database
from App_Barbearia.models import Usuario, Post, Servico

app = create_app()

def popular_agendamentos():
    with app.app_context():
        print("Iniciando o cadastro dinâmico de agendamentos e avaliações fictícias...")

        # 1. Buscando o barbeiro
        barbeiro = Usuario.query.filter_by(role="barbeiro").first()
        if not barbeiro:
            print("Erro: Nenhum usuário com a role 'barbeiro' foi encontrado no banco.")
            return

        # 2. Buscando serviços cadastrados
        servicos = Servico.query.all()
        if not servicos:
            print("Erro: Nenhum serviço cadastrado na tabela 'servico'.")
            return

        # 3. Buscando clientes cadastrados para vincular aos posts
        clientes = Usuario.query.filter_by(role="cliente").all()
        if not clientes:
            print("Erro: Nenhum cliente cadastrado. Execute o povoamento de usuários primeiro.")
            return

        # 4. Definindo a grade de horários
        horarios = [
            "08:00", "09:00", "10:00", "11:00", 
            "12:00", "13:00", "14:00", "15:00", "16:00"
        ]

        # Vamos criar dados para 5 dias: anteontem (-2), ontem (-1), hoje (0), amanhã (1) e depois de amanhã (2)
        dias_offset = [-2, -1, 0, 1, 2]
        agendamentos_criados = 0

        for offset in dias_offset:
            # Calcula a data alvo somando ou subtraindo dias da data de hoje
            data_alvo = date.today() + timedelta(days=offset)

            for i, hora in enumerate(horarios):
                # Pega clientes e serviços de forma sequencial e cíclica para variar os dados
                cliente = clientes[i % len(clientes)]
                servico = servicos[i % len(servicos)]

                # Verifica se já existe agendamento nesse dia e horário para não duplicar
                agendamento_existente = Post.query.filter_by(data=data_alvo, hora=hora).first()

                if not agendamento_existente:
                    # Lógica para simular o mundo real:
                    # Dias no passado ganham avaliação 5. Dias futuros ficam sem avaliação (None).
                    avaliacao_simulada = 5 if offset < 0 else None
                    
                    # Lembretes só fazem sentido se o agendamento já passou ou está muito próximo
                    lembrete_24h = True if offset <= 1 else False
                    lembrete_2h = True if offset <= 0 else False

                    novo_agendamento = Post(
                        username=cliente.username,
                        cell="(19) 99999-0000",
                        servico=servico.nome,
                        valor=servico.valor,
                        hora=hora,
                        data=data_alvo,
                        id_usuario=barbeiro.id,
                        avaliacao=avaliacao_simulada,
                        lembrete_24h_enviado=lembrete_24h,
                        lembrete_2h_enviado=lembrete_2h
                    )
                    database.session.add(novo_agendamento)
                    agendamentos_criados += 1

        # Comita (salva) tudo de uma vez no banco
        if agendamentos_criados > 0:
            database.session.commit()
            print(f"Sucesso! {agendamentos_criados} agendamentos gerados.")
        else:
            print("Nenhum agendamento novo foi criado. Os horários já estavam preenchidos.")
            
        print("Agora vocês já podem testar os dashboards, relatórios e avaliações no app!")

if __name__ == "__main__":
    popular_agendamentos()