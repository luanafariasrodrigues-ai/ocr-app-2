from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao"

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matriculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS (TABELAS) ---

class Responsavel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    matriculas = db.relationship('Matricula', backref='dono', lazy=True)

class Matricula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    curso = db.Column(db.String(50))
    parentesco = db.Column(db.String(50))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    arquivos_json = db.Column(db.Text)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'))

# Cria o banco de dados
with app.app_context():
    db.create_all()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- ROTAS PRINCIPAIS ---

@app.route('/')
def portal():
    return render_template('portal.html')

# --- LOGIN E CADASTRO DO RESPONSÁVEL ---

@app.route('/cadastro_responsavel', methods=['GET', 'POST'])
def cadastro_responsavel():
    if request.method == 'POST':
        user = request.form.get('usuario')
        passw = request.form.get('senha')
        if Responsavel.query.filter_by(usuario=user).first():
            return "Este usuário já existe! <a href='/cadastro_responsavel'>Tentar outro</a>"
        
        novo_resp = Responsavel(usuario=user, senha=generate_password_hash(passw))
        db.session.add(novo_resp)
        db.session.commit()
        return redirect(url_for('login_responsavel'))
    return render_template('parent_register.html')

@app.route('/login_responsavel', methods=['GET', 'POST'])
def login_responsavel():
    if request.method == 'POST':
        user = request.form.get('usuario')
        passw = request.form.get('senha')
        resp = Responsavel.query.filter_by(usuario=user).first()
        
        if resp and check_password_hash(resp.senha, passw):
            session['responsavel_id'] = resp.id
            session
