# App_Barbearia/models.py

from App_Barbearia import database, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    __tablename__ = 'usuario'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(30), nullable=False)
    email = database.Column(database.String(120), nullable=False)
    foto_perfil = database.Column(database.String(20), nullable=False, server_default='default.jpg')
    senha = database.Column(database.String(60), nullable=False)
    role = database.Column(database.String(20), nullable=False, default='cliente')
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    posts = database.relationship('Post', backref='autor', lazy=True)

    __table_args__ = (
        UniqueConstraint('username', name='uq_usuario_username'),
        UniqueConstraint('email', name='uq_usuario_email'),
    )

    def __repr__(self):
        return f"Usuario('{self.username}', '{self.email}')"

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return Usuario.query.get(user_id)

class Servico(database.Model):
    __tablename__ = 'servico'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100), nullable=False, unique=True)
    valor = database.Column(database.Float, nullable=False)
    
    def __repr__(self):
        return f"Servico('{self.nome}', R${self.valor}')"

# 🟢 Novo modelo para Cupons de Desconto
class Cupom(database.Model):
    __tablename__ = 'cupom'
    id = database.Column(database.Integer, primary_key=True)
    codigo = database.Column(database.String(15), unique=True, nullable=False)
    desconto_percentual = database.Column(database.Float, nullable=False) # Exemplo: 15.0 para 15%
    ativo = database.Column(database.Boolean, default=True, nullable=False)
    data_criacao = database.Column(database.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"Cupom('{self.codigo}', Desconto: {self.desconto_percentual}%)"

class Post(database.Model):
    __tablename__ = 'post'

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    cell = database.Column(database.String, nullable=False)
    servico = database.Column(database.String, nullable=False)
    valor = database.Column(database.Float, nullable=False, default=0.0)
    hora = database.Column(database.String, nullable=False)
    data = database.Column(database.Date, nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    avaliacao = database.Column(database.Integer, nullable=True, default=None)
    lembrete_24h_enviado = database.Column(database.Boolean, nullable=False, default=False)
    lembrete_2h_enviado = database.Column(database.Boolean, nullable=False, default=False)
    lembrete_1h_enviado = database.Column(database.Boolean, nullable=False, default=False)
    lembrete_30min_enviado = database.Column(database.Boolean, nullable=False, default=False)
    
    # 🟢 Rastreamento do cupom utilizado (permite medir o impacto na demanda)
    cupom_usado = database.Column(database.String(15), nullable=True, default=None)

    def __repr__(self):
        return f"Post('{self.username}', '{self.servico}', '{self.data}')"