from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Inicializa o Flask. O template_folder é usado caso o HTML esteja no backend.
app = Flask(__name__, template_folder='templates')
CORS(app) 

# --- CONFIGURAÇÃO DINÂMICA DO BANCO DE DADOS ---

# 1. No Render, você deve configurar a variável de ambiente DATABASE_URL com a "Connection String" do Supabase.
# 2. Se estiver rodando localmente e não houver essa variável, ele tentará usar o seu Postgres local.
uri = os.environ.get('DATABASE_URL')

if uri:
    # O Supabase geralmente fornece a URL começando com "postgres://". 
    # O SQLAlchemy moderno exige "postgresql://" para funcionar corretamente.
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
else:
    # Fallback para desenvolvimento local caso você não tenha configurado as variáveis de ambiente ainda.
    # Substitua pela sua string do Supabase se quiser testar o banco da nuvem localmente.
    uri = 'postgresql://postgres:wordKey##@localhost:5433/barberflow'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DO BANCO DE DADOS ---

class Barber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    barber_id = db.Column(db.Integer, db.ForeignKey('barber.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    value = db.Column(db.Float, nullable=False)

# Cria as tabelas automaticamente no banco conectado (Supabase ou Local)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Erro na conexão com o banco de dados: {e}")

# --- ROTAS ---

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return jsonify({"message": "Backend BarberFlow Ativo", "db_connected": True})

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online", 
        "database": "Supabase/Cloud" if os.environ.get('DATABASE_URL') else "Local"
    })

@app.route('/services', methods=['GET', 'POST'])
def manage_services():
    if request.method == 'GET':
        services = Service.query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'price': s.price} for s in services])
    data = request.json
    new_service = Service(name=data['name'], price=data['price'])
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Ok'}), 201

@app.route('/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Removido'})

@app.route('/barbers', methods=['GET', 'POST'])
def manage_barbers():
    if request.method == 'GET':
        barbers = Barber.query.all()
        return jsonify([{'id': b.id, 'name': b.name} for b in barbers])
    data = request.json
    new_barber = Barber(name=data['name'])
    db.session.add(new_barber)
    db.session.commit()
    return jsonify({'message': 'Ok'}), 201

@app.route('/barbers/<int:id>', methods=['DELETE'])
def delete_barber(id):
    barber = Barber.query.get_or_404(id)
    db.session.delete(barber)
    db.session.commit()
    return jsonify({'message': 'Removido'})

@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    if request.method == 'GET':
        apps = Appointment.query.all()
        return jsonify([{
            'id': a.id, 'client': a.client, 'date': a.date, 
            'time': a.time, 'status': a.status, 
            'barber_id': a.barber_id, 'service_id': a.service_id
        } for a in apps])
    data = request.json
    new_app = Appointment(
        client=data['client'], date=data['date'], time=data['time'],
        barber_id=data['barber_id'], service_id=data['service_id'],
        status=data.get('status', 'confirmed')
    )
    db.session.add(new_app)
    db.session.commit()
    return jsonify({'message': 'Agendado'}), 201

@app.route('/appointments/<int:id>', methods=['PUT', 'DELETE'])
def update_appointment(id):
    appo = Appointment.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        if 'status' in data: appo.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Atualizado'})
    db.session.delete(appo)
    db.session.commit()
    return jsonify({'message': 'Removido'})

@app.route('/costs', methods=['GET', 'POST'])
def manage_costs():
    if request.method == 'GET':
        costs = Cost.query.all()
        return jsonify([{'id': c.id, 'description': c.description, 'value': c.value} for c in costs])
    data = request.json
    new_cost = Cost(description=data['description'], value=data['value'])
    db.session.add(new_cost)
    db.session.commit()
    return jsonify({'message': 'Registrado'}), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
