from datetime import date, timedelta
from App_Barbearia import create_app, database
from App_Barbearia.models import Usuario, Post, Servico

app = create_app()

def popular_retroativos():
    with app.app_context():
        print("Iniciando a inserção de agendamentos retroativos...")

        # 1. Busca o barbeiro responsável para associar aos atendimentos
        barbeiro = Usuario.query.filter_by(role="barbeiro").first()
        if not barbeiro:
            print("Erro: Nenhum barbeiro encontrado no banco. Cadastre um barbeiro primeiro.")
            return

        # 2. Busca os serviços disponíveis
        servicos = Servico.query.all()
        if not servicos:
            print("Erro: Nenhum serviço encontrado no banco. Cadastre os serviços primeiro.")
            return

        # 3. Lista dos clientes com diferentes dias no passado para enriquecer os testes
        # O campo 'dias_atras' subtrai da data de hoje, garantindo que seja sempre no passado.
        atendimentos_config = [
            {"nome": "Gabriel Silva",   "dias_atras": 3,  "hora": "09:00", "nota": 5},
            {"nome": "Helena Rocha",    "dias_atras": 5,  "hora": "10:00", "nota": 5},
            {"nome": "Igor Martins",    "dias_atras": 8,  "hora": "11:00", "nota": 4},
            {"nome": "Juliana Ferreira","dias_atras": 12, "hora": "14:00", "nota": 5},
            {"nome": "Larissa Gomes",   "dias_atras": 16, "hora": "15:00", "nota": 4},
            {"nome": "Marcos Vinícius", "dias_atras": 20, "hora": "16:00", "nota": 5},
            {"nome": "Natália Ribeiro", "dias_atras": 25, "hora": "08:00", "nota": 5},
            {"nome": "Otávio Augusto",  "dias_atras": 32, "hora": "09:00", "nota": 3}, # > 30 dias: gera alerta de recência
            {"nome": "Quintino Barros", "dias_atras": 35, "hora": "11:00", "nota": 4}, # > 30 dias: gera alerta de recência
            {"nome": "Rafael Castro",   "dias_atras": 40, "hora": "14:00", "nota": 5}, # > 30 dias: gera alerta de recência
            {"nome": "Sara Dias",       "dias_atras": 18, "hora": "15:00", "nota": 5},
            {"nome": "Tiago Nogueira",  "dias_atras": 7,  "hora": "16:00", "nota": 4},
        ]

        hoje = date.today()
        registros_inseridos = 0

        for i, config in enumerate(atendimentos_config):
            nome_cliente = config["nome"]
            cliente = Usuario.query.filter_by(username=nome_cliente).first()

            if not cliente:
                print(f"Aviso: Cliente '{nome_cliente}' não encontrado na tabela de usuários. Pulando...")
                continue

            data_atendimento = hoje - timedelta(days=config["dias_atras"])
            servico_escolhido = servicos[i % len(servicos)]

            # Verifica se já existe esse agendamento específico para não duplicar
            ja_existe = Post.query.filter_by(
                username=cliente.username,
                data=data_atendimento,
                hora=config["hora"]
            ).first()

            if ja_existe:
                print(f"-> Atendimento para {cliente.username} em {data_atendimento.strftime('%d/%m/%Y')} já existe.")
                continue

            # Cria o registro completo com todos os lembretes marcados como enviados (True)
            novo_post = Post(
                username=cliente.username,
                cell="(19) 98888-0000",
                servico=servico_escolhido.nome,
                valor=servico_escolhido.valor,
                data=data_atendimento,
                hora=config["hora"],
                id_usuario=cliente.id,  # Vinculado diretamente ao ID do cliente
                avaliacao=config["nota"],
                lembrete_24h_enviado=True,
                lembrete_2h_enviado=True,
                lembrete_1h_enviado=True,
                lembrete_30min_enviado=True
            )

            database.session.add(novo_post)
            registros_inseridos += 1
            print(f"-> Inserido: {cliente.username} | Data: {data_atendimento.strftime('%d/%m/%Y')} | Serviço: {servico_escolhido.nome}")

        if registros_inseridos > 0:
            database.session.commit()
            print(f"\nConcluído com sucesso! {registros_inseridos} agendamentos retroativos adicionados.")
        else:
            print("\nNenhum registro novo precisou ser inserido.")

if __name__ == "__main__":
    popular_retroativos()