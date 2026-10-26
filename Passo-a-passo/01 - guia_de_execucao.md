# 💈 Guia de Instalação e Execução do AppBarbearia

Este guia foi criado para orientar qualquer pessoa a configurar e executar a aplicação **AppBarbearia** a partir do zero em uma máquina limpa (sem dependências, sem banco de dados, sem arquivo `.env` e sem ambientes virtuais prévios).

---

## 1. Pré-requisitos

Antes de iniciar os comandos no terminal, confirme se você possui as seguintes ferramentas instaladas:

1. **Git**: Para baixar o código do GitHub.
   * [Download do Git](https://git-scm.com/downloads)
2. **Python (Versão 3.10 ou superior recomendada)**:
   * [Download do Python](https://www.python.org/downloads/)
   * ⚠️ **Atenção (Windows):** Ao instalar o Python, marque obrigatoriamente a opção **"Add Python to PATH"** (Adicionar Python às variáveis de ambiente) na primeira tela do instalador.

Para verificar se estão instalados, abra um terminal e rode:
```bash
git --version
python --version
```
*(No Linux ou macOS, se o comando `python` não existir, use `python3`).*

---

## 2. Clonando o Repositório

Abra o terminal (PowerShell, Prompt de Comando ou Terminal do Linux/macOS) na pasta onde você guarda seus projetos e execute:

```bash
git clone https://github.com/alinessvieira/AppBarbearia.git
cd AppBarbearia
```

Certifique-se de estar dentro da pasta raiz `AppBarbearia` (onde estão os arquivos `app.py`, `requirements.txt` e `set_admin.py`).

---

## 3. Criando e Ativando o Ambiente Virtual (`venv`)

O ambiente virtual isola as dependências do projeto para não interferir em outros programas da sua máquina.

### Criar o ambiente virtual:
```bash
python -m venv .venv
```

### Ativar o ambiente virtual:

* **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  > *Se o PowerShell exibir um erro de segurança bloqueando scripts, execute primeiro:*
  > ```powershell
  > Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  > ```
  > *Em seguida, rode o comando de ativação novamente.*

* **Windows (Prompt de Comando - CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

* **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

Quando ativado, o indicador `(.venv)` aparecerá no início da linha do terminal.

---

## 4. Instalando as Bibliotecas do Projeto

Com o ambiente virtual ativado, atualize o `pip` e faça a instalação de todas as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Aguarde o download e a compilação dos pacotes (Flask, SQLAlchemy, Bcrypt, Scikit-learn, PyWhatKit, etc.).

---

## 5. Configurando o Arquivo de Variáveis de Ambiente (`.env`)

Arquivos `.env` guardam credenciais e segredos locais e não sobem para o GitHub por motivos de segurança. Crie um arquivo chamado `.env` na raiz do projeto (no mesmo nível de `app.py`).

1. Crie o arquivo `.env` usando seu editor de texto (VS Code, Bloco de Notas, etc.).
2. Adicione as seguintes configurações padrão:

```ini
SECRET_KEY=sua_chave_secreta_aqui
MAIL_USERNAME=
MAIL_PASSWORD=
```

### Como gerar uma chave secreta segura (`SECRET_KEY`):
No próprio terminal, execute:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copie o código gerado no terminal e substitua em `sua_chave_secreta_aqui` dentro do arquivo `.env`.

> **Nota sobre e-mails:** As configurações `MAIL_USERNAME` e `MAIL_PASSWORD` são opcionais para o funcionamento local inicial. Caso não vá testar envio real de e-mails, pode deixá-las vazias.

---

## 6. Criação e Povoamento do Banco de Dados

Como o banco SQLite (`instance/barbearia.db`) é local e não vem no clone do GitHub, você precisa inicializá-lo e popular com dados de teste para poder navegar.

Na raiz do projeto e com a `.venv` ativada, execute:

### 1. Criar estrutura e dados básicos (Serviços, barbeiros e usuários de exemplo):
```bash
python popular_db.py
```

### 2. (Opcional) Gerar agendamentos fictícios para testes de relatórios e agenda:
```bash
python popular_posts.py
```
*(Caso queira gerar histórico retroativo completo, você também pode executar: `python popular_retroativo.py`).*

Após rodar esses scripts, a pasta `instance/` com o banco `barbearia.db` estará criada e pronta.

---

## 7. Promovendo um Usuário a Administrador

Algumas rotas (como cadastro de novos serviços, relatórios financeiros e visualização de clientes) exigem permissão de administrador (`role: admin`).

1. Inicie a aplicação (passo 8 a seguir) e cadastre uma conta para você na tela de registro.
2. Pare o servidor no terminal pressionando `Ctrl + C`.
3. Execute o script de promoção:
   ```bash
   python set_admin.py
   ```
4. Digite o e-mail cadastrado quando solicitado. O script atualizará seu usuário para o nível administrativo.

---

## 8. Executando o Aplicativo

Para iniciar o servidor web do Flask:

```bash
python app.py
```

Você verá mensagens indicando que o servidor foi iniciado e que o monitor de lembretes está ativo. Acesse no seu navegador:

👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (ou `http://localhost:5000`)

Para encerrar o servidor a qualquer momento, volte à janela do terminal e aperte **`Ctrl + C`**.

---

## 9. Resumo Rápido de Comandos

Para quem precisa apenas do roteiro de terminal direto:

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/alinessvieira/AppBarbearia.git
cd AppBarbearia

# 2. Criar e ativar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # No Windows PowerShell

# 3. Instalar pacotes
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Criar .env (faça manualmente ou via terminal)
# 5. Popular banco de dados
python popular_db.py
python popular_posts.py

# 6. Rodar servidor
python app.py
```