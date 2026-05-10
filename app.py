from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao"

# CONFIGURAÇÃO DO BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matriculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TABELAS
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

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- ROTAS ---

@app.route('/')
def portal():
    return render_template('portal.html')

@app.route('/cadastro_responsavel', methods=['GET', 'POST'])
def cadastro_responsavel():
    if request.method == 'POST':
        user = request.form.get('usuario')
        passw = request.form.get('senha')
        if Responsavel.query.filter_by(usuario=user).first():
            return "Usuário já existe!", 400
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
            return redirect(url_for('ficha'))
        return render_template('parent_login.html', erro="Usuário ou senha incorretos!")
    return render_template('parent_login.html')

@app.route('/ficha', methods=['GET', 'POST'])
def ficha():
    if not session.get('responsavel_id'):
        return redirect(url_for('login_responsavel'))
    
    if request.method == 'POST':
        # (Lógica de salvar arquivos e matrícula aqui...)
        # Para encurtar, use a lógica de salvar arquivos que já tínhamos
        return "Matrícula Enviada!"
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('usuario') == 'luana' and request.form.get('senha') == '123':
            session['logado'] = True
            return redirect(url_for('painel'))
    return render_template('login.html')

@app.route('/painel')
def painel():
    if not session.get('logado'): return redirect(url_for('login'))
    cadastros = Matricula.query.all()
    return render_template('painel.html', cadastros=cadastros)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
