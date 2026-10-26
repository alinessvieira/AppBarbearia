# AppBarbearia

Aplicação web para apoiar a operação de uma barbearia: clientes podem criar uma conta, agendar serviços e acompanhar seus atendimentos; administradores podem gerenciar a agenda e os serviços e consultar relatórios.

O projeto é desenvolvido em Python com Flask e usa SQLite para persistir os dados. O repositório também inclui recursos de análise de clientes, avaliações e lembretes.

## Funcionalidades

- Cadastro, login, recuperação de senha e edição de perfil.
- Agendamento de serviços e consulta dos agendamentos do cliente.
- Administração de agenda e serviços.
- Avaliações de atendimentos, relatórios e análise de demanda.
- Segmentação de clientes e sugestão de próxima visita com modelos de machine learning.
- Confirmações por e-mail e lembretes de agendamento por WhatsApp. O envio depende das configurações locais e, no caso do WhatsApp, de uma sessão de navegador compatível.

## Começar

Para clonar, configurar o ambiente virtual, instalar as dependências, criar o `.env`, inicializar o banco e executar o sistema, siga o [Guia Completo](Passo-a-passo/Guia%20Completo.md).

Resumo do fluxo na raiz do repositório:

```bash
git clone https://github.com/alinessvieira/AppBarbearia.git
cd AppBarbearia
python -m venv .venv
```

Ative o ambiente virtual de acordo com seu sistema operacional, instale as dependências e prepare a base:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python popular_db.py
python app.py
```

Abra `http://127.0.0.1:5000` no navegador. A aplicação cria tabelas ausentes na inicialização; o script `popular_db.py` prepara dados de demonstração. Para uma instalação nova, use o procedimento do guia antes de iniciar. Não execute scripts de população em uma base com dados reais sem antes revisar o que será inserido e fazer uma cópia de segurança.

O arquivo `.env` e o banco local não devem ser compartilhados. As credenciais de e-mail são opcionais para iniciar o site, mas necessárias para envio de e-mails. Os lembretes por WhatsApp são iniciados junto com `python app.py` e dependem de um ambiente com navegador/interface gráfica e conexão.

## Documentação

- [Guia Completo](Passo-a-passo/Guia%20Completo.md) — instalação do zero, configuração, execução, administração e solução de problemas.
- [Configuração local](Passo-a-passo/SETUP_LOCAL.md) — referência adicional para preparar o ambiente de desenvolvimento.
- [Documentação do projeto](Passo-a-passo/DOCUMENTACAO.md) — descrição técnica e funcionalidades.
- [Como popular o banco](Passo-a-passo/popular_db.md) — instruções para os scripts de dados de demonstração.
- [Como promover um usuário a administrador](Passo-a-passo/senha%20admin.txt) — procedimento e cuidados do script `set_admin.py`.

## Estrutura

```text
AppBarbearia/
├── App_Barbearia/       # Aplicação Flask: modelos, rotas, formulários, templates e arquivos estáticos
├── Passo-a-passo/       # Guias e documentação
├── migrations/          # Histórico de migrações do banco
├── instance/            # Arquivos locais da aplicação, incluindo o SQLite
├── app.py               # Inicialização da aplicação e do serviço de lembretes
├── popular_db.py        # Criação/preenchimento inicial para demonstração
├── popular_posts.py     # Geração de agendamentos fictícios
├── popular_retroativo.py # Geração de dados fictícios retroativos
├── set_admin.py         # Promoção de usuário existente a administrador
└── requirements.txt     # Dependências Python
```

Os scripts de população destinam-se a desenvolvimento e demonstração. Consulte os guias antes de usá-los. A configuração atual usa `create_all()` para criar tabelas ausentes, mas isso não atualiza automaticamente tabelas existentes; para bancos de versões anteriores, faça backup e siga as orientações sobre migrações no [Guia Completo](Passo-a-passo/Guia%20Completo.md).

## Testes

O `requirements.txt` não inclui o `pytest`. Para executar os testes, instale-o no ambiente virtual e rode:

```bash
python -m pip install pytest
python -m pytest
```
