# Guia completo: clonar, configurar e executar o AppBarbearia

Este guia prepara o projeto em uma máquina limpa, sem Python configurado para o projeto, sem bibliotecas, sem arquivo `.env` e sem banco de dados local. Os comandos partem da raiz do repositório, isto é, da pasta `AppBarbearia`.

## 1. Pré-requisitos

Instale:

- **Git**: https://git-scm.com/downloads
- **Python 3.12** (recomendado): https://www.python.org/downloads/
- Um navegador atualizado

Durante a instalação do Python no Windows, marque **Add Python to PATH**. Para confirmar que Git e Python estão disponíveis, abra um terminal novo e execute:

```text
git --version
python --version
```

No macOS/Linux, caso o comando `python` não exista, use `python3` nos comandos deste guia.

## 2. Clonar o repositório

No terminal, escolha onde guardar o projeto e execute:

```bash
git clone https://github.com/alinessvieira/AppBarbearia.git
cd AppBarbearia
```

Confirme que o terminal está na pasta que contém `app.py`, `requirements.txt` e `popular_db.py`:

```bash
git status
```

Execute os próximos comandos a partir dessa pasta.

## 3. Criar e ativar um ambiente virtual

O ambiente virtual mantém as bibliotecas do projeto separadas das demais instalações Python da máquina.

### Windows — PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, permita scripts somente nesta janela e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### Windows — Prompt de Comando (CMD)

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Com o ambiente ativo, normalmente o nome `(.venv)` aparece no início do prompt do terminal. Se abrir outro terminal, ative o ambiente virtual novamente antes de continuar.

## 4. Instalar as bibliotecas

Com o ambiente virtual ativado, execute:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

A instalação pode levar alguns minutos, pois inclui dependências para Flask, SQLite, análise de dados, machine learning, imagens e automação de WhatsApp.

## 5. Configurar o arquivo `.env`

O arquivo `.env` deve ficar na raiz, junto de `app.py`. Ele não é enviado ao Git. Crie-o manualmente com este conteúdo:

```ini
SECRET_KEY=COLOQUE_AQUI_UMA_CHAVE_ALEATORIA
MAIL_USERNAME=
MAIL_PASSWORD=
```

Gere uma chave aleatória executando:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para o valor de `SECRET_KEY`. Não publique nem compartilhe esse valor.

O site pode iniciar sem as configurações de e-mail, mas os e-mails não serão enviados. Para habilitar o envio pelo Gmail, preencha:

- `MAIL_USERNAME`: endereço Gmail usado para envio.
- `MAIL_PASSWORD`: senha de app do Google, não a senha normal da conta. A conta precisa ter a verificação em duas etapas habilitada. Consulte https://myaccount.google.com/apppasswords.

Exemplo de formato (substitua pelos seus próprios valores):

```ini
SECRET_KEY=chave_gerada_no_terminal
MAIL_USERNAME=seuemail@gmail.com
MAIL_PASSWORD=senha_de_app_do_gmail
```

Não use os valores de exemplo literalmente. Não envie o `.env` para o Git ou para outras pessoas.

## 6. Criar e povoar o banco de dados

O banco usado é SQLite e fica em `instance/barbearia.db`. A pasta `instance/` e o banco são locais e ignorados pelo Git; em um clone novo, eles ainda não existem.

Para criar as tabelas e inserir dados fictícios de demonstração, execute na raiz do projeto:

```bash
python popular_db.py
```

O script cria as tabelas que faltarem e tenta cadastrar serviços, um barbeiro, clientes de exemplo e um agendamento. Ele informa no terminal o que foi adicionado. Depois, o banco estará em `instance/barbearia.db`.

Os dados inseridos são fictícios e servem para demonstração/testes. **Não use esses registros como dados reais de clientes.** As contas incluídas pelo script são dados de teste; para entrar no sistema, crie uma conta pela tela de cadastro conforme o próximo passo.

### Opcional: gerar mais agendamentos fictícios

Depois de executar `popular_db.py`, pode-se gerar uma grade de agendamentos para testar agenda e relatórios:

```bash
python popular_posts.py
```

Esse script cria agendamentos fictícios em datas próximas. Não o execute em um banco que contenha dados reais.

## 7. Iniciar a aplicação

Na raiz do projeto e com o ambiente virtual ativado:

```bash
python app.py
```

Quando o servidor indicar que está em execução, abra no navegador:

http://127.0.0.1:5000

Para encerrar, volte ao terminal e pressione **Ctrl+C**. Mantenha essa janela aberta enquanto estiver usando a aplicação.

O modo de execução atual inicia o serviço de lembretes do WhatsApp em segundo plano. O envio depende de ambiente gráfico, navegador/WhatsApp Web e conexão; em servidor sem interface gráfica, trate esse recurso como indisponível. Não é necessário configurar WhatsApp para abrir e usar as páginas principais.

## 8. Criar um usuário administrador

1. Com a aplicação aberta, acesse http://127.0.0.1:5000.
2. Use a opção de cadastro na tela de login e crie uma conta com um e-mail ao qual tenha acesso.
3. Pare a aplicação com **Ctrl+C**.
4. No terminal, ainda na raiz e com o ambiente virtual ativado, execute:

   ```bash
   python set_admin.py
   ```

5. Informe exatamente o e-mail usado no cadastro. O script promove essa conta para administradora.
6. Inicie novamente com `python app.py` e entre com a conta criada.

O script `set_admin.py` só promove um usuário que já exista no banco. Não compartilhe a conta administradora e use uma senha forte.

## 9. Executar os testes (opcional)

O arquivo `requirements.txt` não instala o pytest. Se quiser executar os testes, instale-o no ambiente virtual:

```bash
python -m pip install pytest
python -m pytest
```

## 10. Solução de problemas

### `python` não foi encontrado

- No Windows, reinstale/ajuste o Python e marque **Add Python to PATH**.
- No macOS/Linux, tente os comandos com `python3`.
- Feche e reabra o terminal após instalar o Python.

### `ModuleNotFoundError` ao iniciar

Ative o ambiente virtual e instale as dependências novamente:

```bash
python -m pip install -r requirements.txt
```

### Erro ao ativar o ambiente virtual no PowerShell

Execute nesta janela do PowerShell e tente novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### O site não abre

- Confirme que `python app.py` continua em execução, sem erro no terminal.
- Acesse `http://127.0.0.1:5000`.
- Se a porta 5000 já estiver em uso, encerre o outro processo que a utiliza antes de iniciar o projeto.

### Banco de dados

- Confirme que está executando os comandos na raiz do projeto.
- `python popular_db.py` cria o banco e os registros de demonstração quando ainda não existem.
- Não apague nem substitua `instance/barbearia.db` se houver dados que queira preservar. Faça uma cópia de segurança antes de qualquer alteração no banco.

## Observações sobre banco e migrações

Na primeira execução, `app.py` cria as tabelas ausentes com os modelos atuais. Para uma instalação nova, use o procedimento deste guia e não execute `flask db upgrade`: as migrações existentes ainda não descrevem todos os campos/modelos atuais. `create_all()` cria tabelas que faltam, mas não altera automaticamente tabelas já existentes. Se o banco já tiver dados ou vier de uma versão anterior do projeto, faça backup e trate a atualização do esquema antes de reutilizá-lo.

## Resumo dos comandos principais

Após instalar Git e Python:

```bash
git clone https://github.com/alinessvieira/AppBarbearia.git
cd AppBarbearia
python -m venv .venv
```

Ative o ambiente virtual conforme seu sistema operacional e então:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python popular_db.py
python app.py
```
