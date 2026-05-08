from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy  # Importa o banco de dados
import os
import json

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao"

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matriculas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Tabela do Banco de Dados
class Matricula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    curso = db.Column(db.String(50))
    parentesco = db.Column(db.String(50))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    arquivos_json = db.Column(db.Text)  # Guarda os nomes dos arquivos como texto


# Cria o arquivo do banco se ele não existir
with app.app_context():
    db.create_all()

# --------------------------------------

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def portal():
    return render_template('portal.html')


@app.route('/ficha', methods=['GET', 'POST'])
def ficha():
    if request.method == 'POST':
        campos_arquivos = [
            'doc_aluno', 'doc_pai', 'doc_mae', 'doc_resp',
            'comprovante_residencia', 'cartao_vacina', 'declaracao_escola',
            'historico_escola', 'boletim_escola', 'ficha_transferencia'
        ]

        arquivos_salvos = {}
        for campo in campos_arquivos:
            arquivo = request.files.get(campo)
            if arquivo and arquivo.filename != '':
                nome_arquivo = f"{request.form.get('nome')}_{arquivo.filename}"
                arquivo.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
                arquivos_salvos[campo] = nome_arquivo

        endereco = f"{request.form.get('rua')}, Nº {request.form.get('numero_da_rua')} ({request.form.get('complemento')}) - {request.form.get('bairro')}, {request.form.get('cidade')}/{request.form.get('estado')}"

        # SALVANDO NO BANCO DE DADOS (SQLite)
        nova_ficha = Matricula(
            nome=request.form.get('nome'),
            curso=request.form.get('curso'),
            parentesco=request.form.get('parentesco'),
            telefone=request.form.get('telefone'),
            endereco=endereco,
            arquivos_json=json.dumps(arquivos_salvos)  # Transforma dicionário em texto
        )

        db.session.add(nova_ficha)
        db.session.commit()  # Grava no arquivo .db

        return "<h1>Matrícula enviada com sucesso!</h1><a href='/'>Voltar ao Início</a>"

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        if usuario == 'luana' and senha == '123':
            session['logado'] = True
            return redirect(url_for('painel'))
        return render_template('login.html', erro="Usuário ou senha incorretos!")
    return render_template('login.html')


@app.route('/painel')
def painel():
    if not session.get('logado'):
        return redirect(url_for('login'))

    # BUSCA TODOS OS DADOS DO BANCO
    dados_do_banco = Matricula.query.all()

    # Prepara os dados para o HTML entender os arquivos
    lista_para_exibir = []
    for d in dados_do_banco:
        lista_para_exibir.append({
            "nome": d.nome,
            "curso": d.curso,
            "parentesco": d.parentesco,
            "telefone": d.telefone,
            "endereco": d.endereco,
            "arquivos": json.loads(d.arquivos_json) if d.arquivos_json else {}
        })

    return render_template('painel.html', cadastros=lista_para_exibir)


@app.route('/sair')
def sair():
    session.pop('logado', None)
    return redirect(url_for('portal'))


@app.route('/baixar/<nome_arquivo>')
def baixar_arquivo(nome_arquivo):
    if not session.get('logado'):
        return "Acesso negado", 403
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo)


if __name__ == '__main__':
    # O Render define a porta automaticamente pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
