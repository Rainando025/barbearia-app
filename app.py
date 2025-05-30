from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime, date  # <--- adicionei date aqui
from werkzeug.security import generate_password_hash, check_password_hash
import requests

SUPABASE_URL = 'https://fijsbauiupuamssehksw.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpanNiYXVpdXB1YW1zc2Voa3N3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMjMwOTcsImV4cCI6MjA2MzY5OTA5N30.Dr9ZZtDExZOOHMVssx7x-8DlS3i7m4jB9C9N-fbajZA'
supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:wordKey##@localhost:5433/barbearia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Falsefrom flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime, date  # <--- adicionei date aqui
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.secret_key = '747d003611e2cb0afd469075f617e501'  # necessário para flash messages
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

SUPABASE_URL = 'https://fijsbauiupuamssehksw.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpanNiYXVpdXB1YW1zc2Voa3N3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMjMwOTcsImV4cCI6MjA2MzY5OTA5N30.Dr9ZZtDExZOOHMVssx7x-8DlS3i7m4jB9C9N-fbajZA'
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- Funções auxiliares para CRUD no Supabase ---

def supabase_get(table, filters=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = filters if filters else {}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro GET {table}: {response.status_code} {response.text}")
        return None

def supabase_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in (200, 201):
        return response.json()
    else:
        print(f"Erro POST {table}: {response.status_code} {response.text}")
        return None

def supabase_patch(table, id_value, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_value}"
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 204:
        return True
    else:
        print(f"Erro PATCH {table} id {id_value}: {response.status_code} {response.text}")
        return False

def supabase_delete(table, id_value):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_value}"
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return True
    else:
        print(f"Erro DELETE {table} id {id_value}: {response.status_code} {response.text}")
        return False


# --- Rotas para Barbeiros ---

@app.route('/barbeiros')
def listar_barbeiros():
    barbeiros = supabase_get('barbeiros')
    return render_template('painel_barbeiro.html', barbeiros=barbeiros)

@app.route('/barbeiros/cadastrar', methods=['GET', 'POST'])
def cadastrar_barbeiro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        username = request.form['username']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        data = {
            'nome': nome,
            'email': email,
            'username': username,
            'senha': senha_hash
        }
        supabase_post('barbeiros', data)
        return redirect(url_for('listar_barbeiros'))

    return render_template('cadastrar_barbeiro.html')

@app.route('/barbeiros/editar/<int:id>', methods=['GET', 'POST'])
def editar_barbeiro(id):
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        username = request.form['username']
        senha = request.form.get('senha')
        data = {
            'nome': nome,
            'email': email,
            'username': username
        }
        if senha:
            data['senha'] = generate_password_hash(senha)

        supabase_patch('barbeiros', id, data)
        return redirect(url_for('listar_barbeiros'))

    barbeiro = supabase_get('barbeiros', {'id': f'eq.{id}'})
    if barbeiro:
        return render_template('editar_barbeiro.html', barbeiro=barbeiro[0])
    return "Barbeiro não encontrado", 404

@app.route('/barbeiros/deletar/<int:id>', methods=['POST'])
def deletar_barbeiro(id):
    supabase_delete('barbeiros', id)
    return redirect(url_for('listar_barbeiros'))


# --- Rotas para Cortes ---

@app.route('/cortes')
def listar_cortes():
    cortes = supabase_get('cortes')
    return render_template('cortes.html', cortes=cortes)

@app.route('/cortes/cadastrar', methods=['GET', 'POST'])
def cadastrar_corte():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        data = {'nome': nome, 'preco': preco}
        supabase_post('cortes', data)
        return redirect(url_for('listar_cortes'))

    return render_template('cadastrar_corte.html')

@app.route('/cortes/editar/<int:id>', methods=['GET', 'POST'])
def editar_corte(id):
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        data = {'nome': nome, 'preco': preco}
        supabase_patch('cortes', id, data)
        return redirect(url_for('listar_cortes'))

    corte = supabase_get('cortes', {'id': f'eq.{id}'})
    if corte:
        return render_template('editar_corte.html', corte=corte[0])
    return "Corte não encontrado", 404

@app.route('/cortes/deletar/<int:id>', methods=['POST'])
def deletar_corte(id):
    supabase_delete('cortes', id)
    return redirect(url_for('listar_cortes'))


# --- Rotas para Agendamentos ---

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        cliente = request.form['cliente']
        barbeiro_id = int(request.form['barbeiro_id'])
        corte_id = int(request.form['corte_id'])
        data_hora = request.form['data_hora']

        data = {
            'cliente': cliente,
            'barbeiro_id': barbeiro_id,
            'corte_id': corte_id,
            'data_hora': data_hora,
            'concluido': False
        }
        supabase_post('agendamentos', data)
        return redirect(url_for('listar_agendamentos'))

    barbeiros = supabase_get('barbeiros')
    cortes = supabase_get('cortes')
    return render_template('agendar.html', barbeiros=barbeiros, cortes=cortes)

@app.route('/agendamentos')
def listar_agendamentos():
    agendamentos = supabase_get('agendamentos')
    return render_template('agendamentos.html', agendamentos=agendamentos)

@app.route('/agendamentos/concluir/<int:id>', methods=['POST'])
def concluir_agendamento(id):
    sucesso = supabase_patch('agendamentos', id, {'concluido': True})
    if sucesso:
        return redirect(url_for('listar_agendamentos'))
    return "Erro ao concluir agendamento", 400

@app.route('/agendamentos/deletar/<int:id>', methods=['POST'])
def deletar_agendamento(id):
    supabase_delete('agendamentos', id)
    return redirect(url_for('listar_agendamentos'))


# --- Login e Logout ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']

        usuarios = supabase_get('barbeiros', {'username': f'eq.{username}'})
        if usuarios and len(usuarios) > 0:
            usuario = usuarios[0]
            if check_password_hash(usuario['senha'], senha):
                session['usuario_id'] = usuario['id']
                session['usuario_nome'] = usuario['nome']
                return redirect(url_for('listar_agendamentos'))
        return render_template('login.html', erro="Usuário ou senha inválidos")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

app.secret_key = '747d003611e2cb0afd469075f617e501'  # necessário para flash messages
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

db = SQLAlchemy(app)

# Modelos do banco

class Corte(db.Model):
    __tablename__ = 'cortes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)

class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    senha = db.Column(db.String(255))
    username = db.Column(db.String(100), unique=True) 
    is_admin = db.Column(db.Boolean, default=False)

    
    def set_senha(self, senha_texto):  # corrigi 'Self' para 'self'
        self.senha = generate_password_hash(senha_texto)
        
    def checar_senha(self, senha_texto):
        return check_password_hash(self.senha, senha_texto)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100))
    corte_id = db.Column(db.Integer, db.ForeignKey('cortes.id'))  # chave estrangeira para tabela cortes
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'))
    data = db.Column(db.Date)
    hora = db.Column(db.Time)
    concluido = db.Column(db.Boolean, default=False)

    corte = db.relationship('Corte')
    barbeiro = db.relationship('Barbeiro')

# Rota inicial
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/agendar_cliente', methods=['GET', 'POST'])
def agendar_cliente():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        corte_id = request.form['corte_id']
        barbeiro_id = request.form['barbeiro_id']
        data = request.form['data']
        hora = request.form['hora']

        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora, '%H:%M').time()

        # Verificar se já existe agendamento nesse horário
        existe = Agendamento.query.filter_by(barbeiro_id=barbeiro_id, data=data_obj, hora=hora_obj).first()
        if existe:
            flash('Horário indisponível. Escolha outro.', 'error')
            return redirect(url_for('agendar_cliente'))

        novo_agendamento = Agendamento(
            nome_cliente=nome_cliente,
            corte_id=corte_id,
            barbeiro_id=barbeiro_id,
            data=data_obj,
            hora=hora_obj
        )
        db.session.add(novo_agendamento)
        db.session.commit()
        flash('Agendamento realizado com sucesso!', 'success')
        return redirect(url_for('agendar_cliente'))

    cortes = Corte.query.all()
    barbeiros = Barbeiro.query.filter(Barbeiro.nome != 'Administrador').all()
    return render_template('agendar_cliente.html', cortes=cortes, barbeiros=barbeiros)




# Rota para agendamento
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        corte_id = request.form['corte_id']
        barbeiro_id = request.form['barbeiro_id']
        data = request.form['data']
        hora = request.form['hora']

        # Converter strings para tipos corretos
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora, '%H:%M').time()

        # Verificar se já existe agendamento para o barbeiro na data e hora
        existe = Agendamento.query.filter_by(barbeiro_id=barbeiro_id, data=data_obj, hora=hora_obj).first()
        if existe:
            flash('Horário indisponível. Escolha outro.', 'error')
            return redirect(url_for('agendar'))

                # Enviar dados para o Supabase
        supabase_url = f"{SUPABASE_URL}/rest/v1/agendamentos"

        payload = {
            "nome_cliente": nome_cliente,
            "corte_id": int(corte_id),
            "barbeiro_id": int(barbeiro_id),
            "data": str(data_obj),
            "hora": str(hora_obj),
            "concluido": False
        }

        response = requests.post(supabase_url, headers=supabase_headers, json=payload)

        if response.status_code == 201:
            flash("Agendamento realizado com sucesso!", "success")
        else:
            flash("Erro ao agendar. Verifique os dados.", "error")

        return redirect(url_for('index'))


    cortes = Corte.query.all()
    barbeiros = Barbeiro.query.filter(Barbeiro.nome != 'Administrador').all()
    return render_template('agendar.html', cortes=cortes, barbeiros=barbeiros)



# Rota login

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        username = request.form.get("username") or request.form.get("email")
        senha = request.form["senha"]

        barbeiro = Barbeiro.query.filter(
            or_(Barbeiro.username == username, Barbeiro.email == username)
        ).first()

        if barbeiro and barbeiro.senha and check_password_hash(barbeiro.senha, senha):
            session["barbeiro_id"] = barbeiro.id
            session["barbeiro_nome"] = barbeiro.nome
            session["is_admin"] = barbeiro.is_admin

            if barbeiro.is_admin:
                return redirect(url_for("painel_admin"))
            else:
                return redirect(url_for("painel_barbeiro"))
        else:
            erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro)

    
    

# Painel do barbeiro
@app.route("/painel_barbeiro")
def painel_barbeiro():
    if 'barbeiro_id' not in session:
        return redirect(url_for('login'))

    barbeiro_id = session['barbeiro_id']
    barbeiro = Barbeiro.query.get(barbeiro_id)  # se ainda usa o modelo

    # Buscar agendamentos do barbeiro via Supabase
    url = f"{SUPABASE_URL}/rest/v1/agendamentos?barbeiro_id=eq.{barbeiro_id}&select=*,cortes(*),barbeiros(*)"
    response = requests.get(url, headers=supabase_headers)

    if response.status_code == 200:
        agendamentos = response.json()
    else:
        agendamentos = []
        flash("Erro ao buscar agendamentos", "error")

    return render_template("painel_barbeiro.html", barbeiro=barbeiro, agendamentos=agendamentos)
    

# Marcar agendamento como concluído
@app.route('/concluir_agendamento/<int:agendamento_id>', methods=['POST'])
def concluir_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    agendamento.concluido = True
    db.session.commit()
    return redirect(url_for('painel_barbeiro'))
    
    
 #rota painel admin   
@app.route("/painel_admin")
def painel_admin():
    if 'barbeiro_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    barbeiros = Barbeiro.query.all()
    agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.hora).all()
    return render_template("painel_admin.html", barbeiros=barbeiros, agendamentos=agendamentos)



#rota cadastro novo corte
@app.route('/cadastrar_corte', methods=['GET', 'POST'])
def cadastrar_corte():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])

        novo_corte = Corte(nome=nome, preco=preco)
        db.session.add(novo_corte)
        db.session.commit()

        return redirect(url_for('painel'))

    return render_template('cadastrar_corte.html')
    

#rota para editar cortes
@app.route('/editar_cortes', methods=['GET', 'POST'])
def editar_cortes():
    cortes = Corte.query.all()

    if request.method == 'POST':
        for corte in cortes:
            novo_preco = request.form.get(f'preco_{corte.id}')
            if novo_preco:
                corte.preco = float(novo_preco)
        db.session.commit()
        return redirect(url_for('painel'))

    return render_template('editar_cortes.html', cortes=cortes)
    
    
#rota para gerenciar barbeiros
@app.route('/gerenciar_barbeiros', methods=['GET', 'POST'])
def gerenciar_barbeiros():
    if 'barbeiro_id' not in session or not session.get('is_admin'):
        flash("Acesso negado.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        for key in request.form:
            if key.startswith("nome_"):
                id_str = key.split("_")[1]
                nome = request.form.get(f"nome_{id_str}")
                email = request.form.get(f"email_{id_str}")
                username = request.form.get(f"username_{id_str}")
                senha = request.form.get(f"senha_{id_str}")

                if id_str.startswith("-"):  # Novo barbeiro
                    if nome and email and username and senha:
                        novo = Barbeiro(
                            nome=nome,
                            email=email,
                            username=username,
                            senha=generate_password_hash(senha)
                        )
                        db.session.add(novo)
                else:  # Barbeiro existente
                    barbeiro = Barbeiro.query.get(int(id_str))
                    if barbeiro:
                        barbeiro.nome = nome
                        barbeiro.email = email
                        barbeiro.username = username
                        if senha:
                            barbeiro.senha = generate_password_hash(senha)

        db.session.commit()
        flash("Barbeiros atualizados com sucesso.")
        return redirect(url_for('gerenciar_barbeiros'))

    barbeiros = Barbeiro.query.all()
    return render_template('gerenciar_barbeiros.html', barbeiros=barbeiros)

 

#rota para gerenciar cortes 
@app.route('/gerenciar_cortes', methods=['GET', 'POST'])
def gerenciar_cortes():
    if 'barbeiro_id' not in session or not session.get('is_admin'):
        flash("Acesso negado.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        for key in request.form:
            if key.startswith("nome_"):
                id_str = key.split("_")[1]
                nome = request.form.get(f"nome_{id_str}")
                preco = request.form.get(f"preco_{id_str}")

                if not nome or not preco:
                    continue

                try:
                    preco = float(preco)
                except ValueError:
                    continue

                if id_str.startswith("-"):  # Novo corte
                    novo = Corte(nome=nome, preco=preco)
                    db.session.add(novo)
                else:  # Corte existente
                    corte = Corte.query.get(int(id_str))
                    if corte:
                        corte.nome = nome
                        corte.preco = preco

        db.session.commit()
        flash("Cortes atualizados com sucesso.")
        return redirect(url_for('gerenciar_cortes'))

    cortes = Corte.query.all()
    return render_template('gerenciar_cortes.html', cortes=cortes)
    
  
# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
