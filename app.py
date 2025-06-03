from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date, timedelta  # <--- adicionei date aqui
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from supabase import create_client, Client



app = Flask(__name__)

SUPABASE_URL =  'https://fijsbauiupuamssehksw.supabase.co'
SUPABASE_KEY =  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpanNiYXVpdXB1YW1zc2Voa3N3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMjMwOTcsImV4cCI6MjA2MzY5OTA5N30.Dr9ZZtDExZOOHMVssx7x-8DlS3i7m4jB9C9N-fbajZA'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}



@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime(format)
    except Exception:
        return value  # se falhar, retorna valor cru


#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:wordKey##@localhost:5433/barbearia'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '747d003611e2cb0afd469075f617e501'  # necessário para flash messages
app.permanent_session_lifetime = timedelta(minutes=30)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

#db = SQLAlchemy(app)


    
    
# Rota inicial

@app.route('/')
def index():
    return render_template('index.html')




# Rota para agendamento
@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        corte_id = int(request.form['corte_id'])
        barbeiro_id = int(request.form['barbeiro_id'])
        data = request.form['data']
        hora = request.form['hora']

        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        hora_obj = datetime.strptime(hora, '%H:%M').time()

        # Verificar se já existe agendamento para o barbeiro na data e hora via Supabase
        response = supabase.table('agendamentos').select('*, cortes!fk_agendamento_corte(nome), barbeiros(nome)').eq('barbeiro_id', barbeiro_id).eq('data', data).eq('hora', hora).execute()
       
        
        if response.data and len(response.data) > 0:
            flash('Horário indisponível. Escolha outro.', 'error')
            return redirect(url_for('agendar'))

        # Inserir novo agendamento no Supabase
        insert_response = supabase.table('agendamentos').insert({
            'nome_cliente': nome_cliente,
            'corte_id': corte_id,
            'barbeiro_id': barbeiro_id,
            'data': data,
            'hora': hora,
            'concluido': False,
            'arquivado': False
        }).execute()

        if insert_response.data:
            flash('Agendamento realizado com sucesso!', 'success')
        else:
            flash('Erro ao realizar agendamento.', 'error')

        return redirect(url_for('index'))

    # Para GET: buscar cortes e barbeiros do Supabase para mostrar no form
    cortes_resp = supabase.table('cortes').select('*').execute()
    barbeiros_resp = supabase.table('barbeiros').select('*').neq('nome', 'Administrador').execute()

    cortes = cortes_resp.data or []
    barbeiros = barbeiros_resp.data or []

    return render_template('agendar.html', cortes=cortes, barbeiros=barbeiros)




# Rota login

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        username = request.form.get("username") or request.form.get("email")
        senha = request.form["senha"]

        response = supabase.table('barbeiros').select('*').or_(
            f"username.eq.{username},email.eq.{username}"
        ).limit(1).execute()

        if response.data and len(response.data) > 0:
            user = response.data[0]
            if user.get('senha') and check_password_hash(user['senha'], senha):
                session.permanent = True
                session["barbeiro_id"] = user['id']
                session["barbeiro_nome"] = user['nome']
                session["is_admin"] = user.get('is_admin', False)

                if session["is_admin"]:
                    return redirect(url_for("painel_admin"))
                else:
                    return redirect(url_for("painel_barbeiro"))
            else:
                erro = "Usuário ou senha inválidos."
        else:
            erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro)

    
    

# Painel do barbeiro
@app.route("/painel_barbeiro")
def painel_barbeiro():
    if 'barbeiro_id' not in session:
        return redirect(url_for('login'))

    barbeiro_id = session['barbeiro_id']

    # Buscar agendamentos no Supabase
    response = supabase.table('agendamentos').select(
        'id, nome_cliente, corte_id, barbeiro_id, data, hora, concluido, arquivado, corte(nome), barbeiro(nome)'
    ).eq('barbeiro_id', barbeiro_id).eq('arquivado', False).order('concluido,data,hora', desc=True).execute()

    try:
            agendamentos = response.data
    except Exception as e:
            flash('Erro ao carregar agendamentos.', 'error')
            agendamentos = []

    # Buscar dados do barbeiro no Supabase
    barbeiro_resp = supabase.table('barbeiros').select('*').eq('id', barbeiro_id).single().execute()
    try:
            barbeiro = barbeiro_resp.data
    except Exception:
            barbeiro = None

    return render_template("painel_barbeiro.html", barbeiro=barbeiro, agendamentos=agendamentos)


    

# Marcar agendamento como concluído
@app.route('/concluir_agendamento/<int:agendamento_id>', methods=['POST'])
def concluir_agendamento(agendamento_id):
    # Atualizar o campo concluido para True no Supabase
    response = supabase.table('agendamentos').update({'concluido': True}).eq('id', agendamento_id).execute()

    # Você pode checar se a atualização deu certo, opcional
    if response.error is not None:
        flash('Erro ao marcar agendamento como concluído.', 'error')

    return redirect(url_for('painel_barbeiro'))

    
    
# rota painel admin
@app.route("/painel_admin")
def painel_admin():
    if 'barbeiro_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    barbeiros_resp = supabase.table('barbeiros').select('*').execute()
    try:
            barbeiros = barbeiros_resp.data
    except Exception:
            barbeiros = []

    agend_resp = supabase.table('agendamentos').select(
        'id, nome_cliente, corte_id, barbeiro_id, data, hora, concluido, arquivado'
    ).eq('arquivado', False).execute()

    try:
            agendamentos = agend_resp.data
    except Exception:
            agendamentos = []

    # Ordenar agendamentos por concluido, data, hora (em Python)
    agendamentos.sort(key=lambda x: (x['concluido'], x['data'], x['hora']), reverse=True)

    return render_template("painel_admin.html", barbeiros=barbeiros, agendamentos=agendamentos)




    
    
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
                        senha_hash = generate_password_hash(senha)
                        supabase.table('barbeiros').insert({
                            'nome': nome,
                            'email': email,
                            'username': username,
                            'senha': senha_hash
                        }).execute()
                else:  # Atualizar barbeiro existente
                    data_update = {
                        'nome': nome,
                        'email': email,
                        'username': username,
                    }
                    if senha:
                        data_update['senha'] = generate_password_hash(senha)
                    supabase.table('barbeiros').update(data_update).eq('id', int(id_str)).execute()

        flash("Barbeiros atualizados com sucesso.")
        return redirect(url_for('gerenciar_barbeiros'))

    response = supabase.table('barbeiros').select('*').execute()
    try:
        barbeiros = response.data
    except Exception:
        barbeiros = []
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
                preco = float(request.form.get(f"preco_{id_str}", 0.0))

                if id_str.startswith("-"):  # novo corte
                    if nome:
                        supabase.table("cortes").insert({
                            "nome": nome,
                            "preco": preco
                        }).execute()
                else:  # atualizar corte
                    supabase.table("cortes").update({
                        "nome": nome,
                        "preco": preco
                    }).eq("id", int(id_str)).execute()

        flash("Cortes atualizados com sucesso.")
        return redirect(url_for("gerenciar_cortes"))

    cortes_resp = supabase.table("cortes").select("*").execute()
    cortes = cortes_resp.data if cortes_resp.data else []
    return render_template("gerenciar_cortes.html", cortes=cortes)



    

    
@app.route('/arquivados')
def listar_arquivados():
    origem = request.args.get('origem', 'barbeiro')
    
    # Busca agendamentos arquivados no Supabase, ordenando por data e hora desc
    response = (
        supabase
        .table('agendamentos')
        .select('*')
        .eq('arquivado', True)
        .order('data', desc=True)
        .order('hora', desc=True)
        .execute()
    )

    agendamentos = []
    if response.data:
        agendamentos = response.data
    
    return render_template('arquivados.html', agendamentos=agendamentos, origem=origem)

    
    
@app.route('/arquivar/<int:agendamento_id>', methods=['POST'])
def arquivar_agendamento(agendamento_id):
    origem = request.args.get('origem', 'barbeiro')
    response = supabase.table('agendamentos').update({'arquivado': True}).eq('id', agendamento_id).execute()
    if response.error:
        flash('Erro ao arquivar agendamento.', 'error')

    if origem == 'admin':
        return redirect(url_for('painel_admin'))
    else:
        return redirect(url_for('painel_barbeiro'))


    
    
  
# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

