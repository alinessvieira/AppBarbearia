# App_Barbearia/routs.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from App_Barbearia import database, bcrypt, mail, create_app
from App_Barbearia.forms import (
    FormLogin, FormCriarConta, Form_Agendar, Form_Avaliar,
    Form_EditarPerfil, Form_Botao, FormRecuperarSenha,
    FormRedefinirSenha, Form_GerenciarServicos, Form_RelatorioLucro
)
from App_Barbearia.decorators import admin_required
from App_Barbearia.models import Usuario, Post, Servico, Cupom
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
import string
import random
import pandas as pd
from PIL import Image
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from .ml_model import preparar_dados_para_ml, treinar_modelo_ml, prever_proxima_visita, segmentar_clientes_kmeans
from collections import Counter

# Instância global do modelo de ML para ser acessível nas rotas
modelo_ml_global = None

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("home.html", ano=datetime.now().year)

@main.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and "botao_submit_login" in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f"Login Feito com Sucesso no E-Mail: {form_login.email.data}", "alert alert-success")
            par_next = request.args.get("next")
            return redirect(par_next) if par_next else redirect(url_for("main.home"))
        else:
            flash("Falha no Login, Verifique Senha ou E-Mail", "alert-danger")

    if form_criarconta.validate_on_submit() and "botao_submit_criarconta" in request.form:
        senha_crypt = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta Criada com Sucesso para o E-Mail: {form_criarconta.email.data}", "alert success")
        return redirect(url_for("main.home"))
    return render_template("login.html", form_login=form_login, form_criarconta=form_criarconta)

@main.route("/sair")
@login_required
def sair():
    logout_user()
    flash("Logout Feito com sucesso", "alert-success")
    return render_template("home.html", ano=datetime.now().year)

@main.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("perfil.html", foto_perfil=foto_perfil)

def enviar_email_confirmacao(email_destino, agendamento):
    msg = Message(
        subject="Confirmação de Agendamento - Barbearia CorteFácil",
        recipients=[email_destino],
        body=f"""Olá, {agendamento.username}!
        
Seu agendamento foi confirmado com sucesso.

Detalhes do Agendamento:
Serviço: {agendamento.servico}
Data: {agendamento.data.strftime('%d/%m/%Y')}
Hora: {agendamento.hora}
Valor Final: R$ {agendamento.valor:.2f}

Se precisar reagendar, entre em contato conosco.

Atenciosamente,
Equipe CorteFácil
"""
    )
    try:
        mail.send(msg)
        print(f"Email de confirmação enviado com sucesso para {email_destino}")
    except Exception as e:
        print(f"Falha ao enviar e-mail de confirmação: {e}")

def salvar_img(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(os.getcwd(), "App_Barbearia", "static", "fotos_perfil", nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

@main.route("/perfil/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form_editar = Form_EditarPerfil()
    if form_editar.validate_on_submit():
        current_user.email = form_editar.email.data
        current_user.username = form_editar.username.data
        if form_editar.foto_perfil.data:
            nome_imagem = salvar_img(form_editar.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        database.session.commit()
        flash(f"Atualizado com Sucesso para o E-Mail: {form_editar.email.data}", "alert success")
        return redirect(url_for("main.perfil"))
    elif request.method == "GET":
        form_editar.email.data = current_user.email
        form_editar.username.data = current_user.username

    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    return render_template("editar_perfil.html", foto_perfil=foto_perfil, form_editar=form_editar)

@main.route("/agendar", methods=["GET", "POST"])
@login_required
def agendar():
    form_agendar = Form_Agendar()
    
    servicos = Servico.query.all()
    form_agendar.servico.choices = [(s.id, f"{s.nome} - R$ {s.valor}") for s in servicos]

    lista_horas = [8, 9, 10, 11, 12, 14, 15, 16]
    form_agendar.hora.choices = [(f"{h}:00", f"{h}:00") for h in lista_horas]

    data_sugerida = None
    if modelo_ml_global:
        try:
            data_sugerida = prever_proxima_visita(modelo_ml_global, current_user.id)
        except Exception as e:
            print(f"Erro ao prever a data para o usuário {current_user.id}: {e}")
            data_sugerida = None
    
    if form_agendar.validate_on_submit():
        agendamento_existente = Post.query.filter(
            and_(Post.data == form_agendar.datar.data, Post.hora == form_agendar.hora.data)
        ).first()
        
        if agendamento_existente:
            flash("Este horário já está ocupado! Por favor, escolha outra data ou horário.", "alert-danger")
        else:
            servico_escolhido = Servico.query.get(form_agendar.servico.data)
            valor_servico = float(servico_escolhido.valor) if servico_escolhido else 0.0
            nome_servico = servico_escolhido.nome if servico_escolhido else ""

            # Verificação rigorosa do cupom (se foi informado e se está estritamente ativo)
            codigo_cupom = None
            if hasattr(form_agendar, 'cupom') and form_agendar.cupom.data:
                codigo_informado = form_agendar.cupom.data.strip().upper()
                cupom_encontrado = Cupom.query.filter_by(codigo=codigo_informado, ativo=True).first()
                if cupom_encontrado:
                    desconto = valor_servico * (cupom_encontrado.desconto_percentual / 100.0)
                    valor_servico = round(valor_servico - desconto, 2)
                    codigo_cupom = cupom_encontrado.codigo
                else:
                    flash(f"Cupom '{codigo_informado}' é inválido ou encontra-se inativo/expirado.", "alert-warning")

            post = Post(
                username=form_agendar.username.data,
                cell=form_agendar.cell.data,
                servico=nome_servico,
                valor=valor_servico,
                data=form_agendar.datar.data,
                hora=form_agendar.hora.data,
                id_usuario=current_user.id,
                cupom_usado=codigo_cupom
            )
            database.session.add(post)
            database.session.commit()
            
            data_formatada = form_agendar.datar.data.strftime('%d/%m/%Y')
            flash(f"Serviço agendado para dia {data_formatada} e hora {form_agendar.hora.data}!", "alert-success")
            
            enviar_email_confirmacao(current_user.email, post)
            return redirect(url_for("main.agendar"))
    else:
        if request.method == 'POST':
            print(form_agendar.errors)

    return render_template("agendar.html", 
                           form_agendar=form_agendar, 
                           data_sugerida=data_sugerida, 
                           servicos=servicos)

@main.route("/agenda_data", methods=["GET", "POST"])
@login_required
@admin_required
def agenda_data():
    form_botao = Form_Botao()
    lista_agendamentos_data = None

    if form_botao.validate_on_submit():
        data_pesquisa = form_botao.data_pesquisa.data
        agendamentos_data = Post.query.filter(Post.data == data_pesquisa).all()
        lista_agendamentos_data = [agendamento for agendamento in agendamentos_data]

    return render_template("agenda_data.html", lista_agendamentos_data=lista_agendamentos_data, form_botao=form_botao)

@main.route("/avaliar_agendamento/<int:id>", methods=["GET", "POST"])
@login_required
def avaliar_agendamento(id):
    agendamento = Post.query.get_or_404(id)
    if current_user.id != agendamento.id_usuario and current_user.role != 'admin':
        abort(403)

    form_avaliar = Form_Avaliar()
    if form_avaliar.validate_on_submit():
        agendamento.avaliacao = form_avaliar.nota.data
        database.session.commit()
        flash('Avaliação salva com sucesso!', 'alert-success')
        if current_user.role == 'admin':
            return redirect(url_for('main.agenda_data'))
        return redirect(url_for('main.meus_agendamentos'))

    if request.method == 'GET' and agendamento.avaliacao is not None:
        form_avaliar.nota.data = agendamento.avaliacao

    return render_template('avaliar.html', form_avaliar=form_avaliar, agendamento=agendamento)

@main.route("/gerenciar_servicos", methods=["GET", "POST"])
@login_required
@admin_required
def gerenciar_servicos():
    form_servico = Form_GerenciarServicos()
    servicos = Servico.query.order_by(Servico.id).all()
    
    if form_servico.validate_on_submit():
        nome = form_servico.nome_servico.data
        valor = form_servico.valor_servico.data
        
        servico_existente = Servico.query.filter_by(nome=nome).first()
        if servico_existente:
            servico_existente.valor = valor
            flash(f"Serviço '{nome}' atualizado com sucesso!", "alert-success")
        else:
            novo_servico = Servico(nome=nome, valor=valor)
            database.session.add(novo_servico)
            flash(f"Serviço '{nome}' adicionado com sucesso!", "alert-success")
        
        database.session.commit()
        return redirect(url_for("main.gerenciar_servicos"))
        
    return render_template("gerenciar_servicos.html", form_servico=form_servico, servicos=servicos)

@main.route("/excluir_servico/<int:id>", methods=["POST"])
@login_required
@admin_required
def excluir_servico(id):
    servico = Servico.query.get_or_404(id)
    database.session.delete(servico)
    database.session.commit()
    flash("Serviço excluído com sucesso!", "alert-success")
    return redirect(url_for("main.gerenciar_servicos"))

@main.route("/relatorio", methods=["GET", "POST"])
@login_required
@admin_required
def relatorio():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        hoje = date.today()
        data_inicio = (hoje - timedelta(days=30)).strftime('%Y-%m-%d')
        data_fim = hoje.strftime('%Y-%m-%d')

    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()

    agendamentos = Post.query.filter(Post.data.between(data_inicio_obj, data_fim_obj)).all()

    contagem_por_dia = Counter([ag.data.strftime("%Y-%m-%d") for ag in agendamentos])
    all_dates = [data_inicio_obj + timedelta(days=x) for x in range((data_fim_obj - data_inicio_obj).days + 1)]
    dados_agendamentos = {d.strftime("%d/%m/%Y"): contagem_por_dia.get(d.strftime("%Y-%m-%d"), 0) for d in all_dates}

    contagem_servicos = database.session.query(Post.servico, func.count(Post.id)).filter(
        Post.data.between(data_inicio_obj, data_fim_obj)
    ).group_by(Post.servico).all()
    dados_servicos = dict(contagem_servicos)

    lucro_por_dia = database.session.query(Post.data, func.sum(Post.valor)).filter(
        Post.data.between(data_inicio_obj, data_fim_obj)
    ).group_by(Post.data).order_by(Post.data).all()
    
    dados_lucro_diario = {d.strftime("%d/%m/%Y"): 0.0 for d in all_dates}
    for data, valor in lucro_por_dia:
        dados_lucro_diario[data.strftime("%d/%m/%Y")] = float(valor)

    lucro_total = sum(dados_lucro_diario.values())
    total_valor_formatado = f"{lucro_total:,.2f}".replace('.', ',')

    return render_template(
        "relatorio.html",
        dados_agendamentos=dados_agendamentos,
        dados_servicos=dados_servicos,
        dados_lucro_diario=dados_lucro_diario,
        total_valor_formatado=total_valor_formatado,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

@main.route("/relatorio_avaliacoes", methods=["GET"])
@login_required
@admin_required
def relatorio_avaliacoes():
    agendamentos_com_avaliacao = Post.query.filter(Post.avaliacao.isnot(None)).all()
    dados_avaliacoes = {}
    contagem_avaliacoes = {}
    
    for agendamento in agendamentos_com_avaliacao:
        servico = agendamento.servico
        if servico not in dados_avaliacoes:
            dados_avaliacoes[servico] = 0
            contagem_avaliacoes[servico] = 0
        
        dados_avaliacoes[servico] += agendamento.avaliacao
        contagem_avaliacoes[servico] += 1
    
    media_avaliacoes = {}
    for servico in dados_avaliacoes:
        media_avaliacoes[servico] = round(dados_avaliacoes[servico] / contagem_avaliacoes[servico], 2)
    
    media_avaliacoes_ordenado = dict(sorted(media_avaliacoes.items(), key=lambda x: x[1], reverse=True))
    total_avaliacoes = len(agendamentos_com_avaliacao)
    media_geral = round(sum(ag.avaliacao for ag in agendamentos_com_avaliacao) / total_avaliacoes, 2) if total_avaliacoes > 0 else 0
    
    return render_template(
        "relatorio_avaliacoes.html",
        media_avaliacoes=media_avaliacoes_ordenado,
        contagem_avaliacoes=contagem_avaliacoes,
        total_avaliacoes=total_avaliacoes,
        media_geral=media_geral
    )

@main.route("/segmentacao", methods=["GET"])
@login_required
@admin_required
def segmentacao():
    ordenar_por = request.args.get("ordenar_por", "valor")
    
    clientes = Usuario.query.filter_by(role="cliente").all()
    if not clientes:
        flash("Nenhum cliente cadastrado para análise.", "alert-info")
        return redirect(url_for("main.home"))

    hoje = date.today()
    dados_clientes = []

    for cliente in clientes:
        agendamentos = Post.query.filter(
            (Post.id_usuario == cliente.id) | (Post.username == cliente.username)
        ).all()

        frequencia = len(agendamentos)
        valor_total = sum(ag.valor for ag in agendamentos if ag.valor is not None)

        if agendamentos:
            datas = [ag.data for ag in agendamentos if ag.data is not None]
            ultima_data = max(datas) if datas else None
            recencia = (hoje - ultima_data).days if ultima_data else None
            # Formata a data para DD/MM/AAAA se existir
            ultima_visita_str = ultima_data.strftime("%d/%m/%Y") if ultima_data else None #
        else:
            recencia = None
            ultima_visita_str = None

        dados_clientes.append({
            "user_id": cliente.id,
            "username": cliente.username,
            "email": cliente.email,
            "frequencia": frequencia,
            "valor_total": valor_total,
            "recencia": recencia,
            "ultima_visita": ultima_visita_str,  # <-- Nova chave com a data exata!
            "destaque_valor": None,
            "destaque_freq": None
        })

    # Top 3 em Valor Financeiro
    clientes_por_valor = sorted(dados_clientes, key=lambda x: x["valor_total"], reverse=True)
    medalhas = ["🥇 Ouro", "🥈 Prata", "🥉 Bronze"]
    for posicao, item in enumerate(clientes_por_valor[:3]):
        if item["valor_total"] > 0:
            item["destaque_valor"] = medalhas[posicao]

    # Top 3 em Frequência
    clientes_por_freq = sorted(dados_clientes, key=lambda x: x["frequencia"], reverse=True)
    for posicao, item in enumerate(clientes_por_freq[:3]):
        if item["frequencia"] > 0:
            item["destaque_freq"] = medalhas[posicao]

    # Ordenação da visualização
    if ordenar_por == "frequencia":
        dados_clientes.sort(key=lambda x: x["frequencia"], reverse=True)
    elif ordenar_por == "recencia":
        dados_clientes.sort(key=lambda x: (x["recencia"] is None, -(x["recencia"] or 0)))
    else:
        dados_clientes.sort(key=lambda x: x["valor_total"], reverse=True)

    return render_template(
        "segmentacao.html",
        segmentos=dados_clientes,
        ordenar_por=ordenar_por
    )

@main.route("/analise_demanda", methods=["GET"])
@login_required
@admin_required
def analise_demanda():
    agendamentos = Post.query.all()
    cupons = Cupom.query.order_by(Cupom.data_criacao.desc()).all()

    dias_semana_pt = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
    horarios_fixos = ['8:00', '9:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00']

    if not agendamentos:
        matriz_demanda = []
        impacto_cupons = {"total_agendamentos": 0, "com_cupom": 0, "taxa_conversao": 0}
    else:
        dados = [{
            'data': ag.data,
            'hora': ag.hora,
            'cupom_usado': ag.cupom_usado,
            'dia_semana': dias_semana_pt[ag.data.weekday()]
        } for ag in agendamentos]

        df = pd.DataFrame(dados)

        pivot = pd.crosstab(
            df['dia_semana'],
            df['hora']
        ).reindex(index=ordem_dias, columns=horarios_fixos, fill_value=0)

        matriz_demanda = []
        for dia in ordem_dias:
            linha = {'dia': dia, 'horarios': {h: int(pivot.loc[dia, h]) for h in horarios_fixos}}
            matriz_demanda.append(linha)

        total_agendamentos = len(df)
        com_cupom = int(df['cupom_usado'].notnull().sum())
        taxa = round((com_cupom / total_agendamentos) * 100, 1) if total_agendamentos > 0 else 0
        impacto_cupons = {
            "total_agendamentos": total_agendamentos,
            "com_cupom": com_cupom,
            "taxa_conversao": taxa
        }

    return render_template(
        "analise_demanda.html",
        matriz_demanda=matriz_demanda,
        horarios_fixos=horarios_fixos,
        cupons=cupons,
        impacto_cupons=impacto_cupons
    )

@main.route("/gerar_cupom", methods=["POST"])
@login_required
@admin_required
def gerar_cupom():
    desconto = request.form.get("desconto", type=float)
    if not desconto or desconto <= 0 or desconto > 100:
        flash("Informe um percentual de desconto válido entre 1% e 100%.", "alert-danger")
        return redirect(url_for("main.analise_demanda"))

    sufixo = ''.join(random.choices(string.digits, k=4))
    codigo_novo = f"CORTE-{sufixo}"

    while Cupom.query.filter_by(codigo=codigo_novo).first():
        sufixo = ''.join(random.choices(string.digits, k=4))
        codigo_novo = f"CORTE-{sufixo}"

    novo_cupom = Cupom(codigo=codigo_novo, desconto_percentual=desconto, ativo=True)
    database.session.add(novo_cupom)
    database.session.commit()

    flash(f"Cupom '{codigo_novo}' ({desconto}%) gerado com sucesso!", "alert-success")
    return redirect(url_for("main.analise_demanda"))

@main.route("/inativar_cupom/<int:id>", methods=["POST"])
@login_required
@admin_required
def inativar_cupom(id):
    cupom = Cupom.query.get_or_404(id)
    cupom.ativo = not cupom.ativo
    database.session.commit()
    
    status_texto = "ativado" if cupom.ativo else "inativado"
    flash(f"O cupom '{cupom.codigo}' foi {status_texto} com sucesso!", "alert-success")
    return redirect(url_for("main.analise_demanda"))

@main.route("/excluir_cupom/<int:id>", methods=["POST"])
@login_required
@admin_required
def excluir_cupom(id):
    cupom = Cupom.query.get_or_404(id)
    database.session.delete(cupom)
    database.session.commit()
    
    flash("Cupom excluído com sucesso do sistema!", "alert-success")
    return redirect(url_for("main.analise_demanda"))

@main.route("/agenda_hoje")
@login_required
@admin_required
def agenda_hoje():
    agendamentos_dia = Post.query.filter_by(data=date.today()).order_by(Post.hora).all()
    return render_template("agenda_hoje.html", agendamentos_dia=agendamentos_dia)

@main.route("/meus_agendamentos")
@login_required
def meus_agendamentos():
    agendamentos = Post.query.filter_by(id_usuario=current_user.id).order_by(Post.data.desc(), Post.hora.desc()).all()
    return render_template("meus_agendamentos.html", agendamentos=agendamentos)

@main.route("/excluir_agendamento/<int:id>", methods=["POST"])
@login_required
@admin_required
def excluir_agendamento(id):
    agendamento = Post.query.get_or_404(id)
    database.session.delete(agendamento)
    database.session.commit()
    flash("Agendamento excluído com sucesso!", "alert-success")
    return redirect(url_for("main.agenda_hoje"))

def enviar_email_recuperacao(usuario):
    token = usuario.get_reset_token()
    msg = Message('Recuperação de Senha',
                  sender='noreply@barbeariacortefacil.com',
                  recipients=[usuario.email])
    msg.body = f'''Para redefinir sua senha, visite o seguinte link:
{url_for('main.redefinir_senha', token=token, _external=True)}
Se você não solicitou esta redefinição, simplesmente ignore este e-mail e nenhuma alteração será feita na sua senha.
'''
    mail.send(msg)

@main.route("/recuperar_senha", methods=["GET", "POST"])
def recuperar_senha():
    form_recuperar = FormRecuperarSenha()
    if form_recuperar.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_recuperar.email.data).first()
        if usuario:
            enviar_email_recuperacao(usuario)
            flash("Um e-mail de recuperação de senha foi enviado.", "alert-success")
            return redirect(url_for("main.login"))
        else:
            flash("E-mail não encontrado.", "alert-danger")
    return render_template("recuperar_senha.html", form_recuperar=form_recuperar)

@main.route("/redefinir_senha/<token>", methods=["GET", "POST"])
def redefinir_senha(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = Usuario.verify_reset_token(token)
    if user is None:
        flash('Token de redefinição de senha inválido ou expirado.', 'danger')
        return redirect(url_for('main.recuperar_senha'))

    form_redefinir = FormRedefinirSenha()
    if form_redefinir.validate_on_submit():
        if form_redefinir.senha.data != form_redefinir.confirmacao_senha.data:
            flash('As senhas não coincidem.', 'danger')
            return render_template('redefinir_senha.html', form_redefinir=form_redefinir, token=token)

        senha_crypt = bcrypt.generate_password_hash(form_redefinir.senha.data)
        user.senha = senha_crypt
        database.session.commit()
        
        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('main.login'))

    return render_template("redefinir_senha.html", form_redefinir=form_redefinir, token=token)

@main.route("/usuarios")
@login_required
def usuarios():
    return render_template("usuarios.html")

@main.route("/servicos")
def servicos():
    return render_template("servicos.html")

@main.app_errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404