from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import sys

# Inicializa o Flask.
# O template_folder indica onde está o teu index.html
app = Flask(__name__, template_folder='templates')
CORS(app) 

# --- CONFIGURAÇÃO DINÂMICA DO BANCO DE DADOS ---

uri = os.environ.get('DATABASE_URL')

if uri:
    # 1. Correção para o SQLAlchemy 2.0+ (postgres:// -> postgresql://)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # 2. Solução para "Network is unreachable" (Erro e3q8 / Porta 5432)
    # Se a URL contém a porta 5432 do Supabase, tentamos trocar para 6543 (Pooler)
    # que é muito mais estável para conexões saindo do Render.
    if "@db.edyayltdzfiovbbmlzyd.supabase.co:5432" in uri:
        uri = uri.replace(":5432", ":6543")
    
    # 3. Garante o uso de SSL, obrigatório para Supabase
    if "sslmode" not in uri:
        separator = "&" if "?" in uri else "?"
        uri += f"{separator}sslmode=require"
else:
    # Fallback Localhost
    uri = 'postgresql://postgres:wordKey##@localhost:5433/barberflow'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de Engine para evitar quedas de conexão
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,     # Verifica se a conexão está viva antes de usar
    "pool_recycle": 280,       # Recicla conexões antes do timeout do banco (Supabase costuma ser 300s)
    "connect_args": {
        "connect_timeout": 10  # Tempo limite para desistir da conexão
    }
}

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

# Inicialização segura do Banco de Dados
with app.app_context():
    try:
        db.create_all()
        print(">>> [LOG] Conexão com Supabase estabelecida com sucesso!")
    except Exception as e:
        print(f">>> [CRÍTICO] Falha na conexão: {e}", file=sys.stderr)

# --- ROTAS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "database": "connected" if uri else "local"})

@app.route('/services', methods=['GET', 'POST'])
def manage_services():
    try:
        if request.method == 'GET':
            services = Service.query.all()
            return jsonify([{'id': s.id, 'name': s.name, 'price': s.price} for s in services])
        data = request.json
        new_service = Service(name=data['name'], price=data['price'])
        db.session.add(new_service)
        db.session.commit()
        return jsonify({'message': 'Ok'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    try:
        service = Service.query.get_or_404(id)
        db.session.delete(service)
        db.session.commit()
        return jsonify({'message': 'Removido'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/barbers', methods=['GET', 'POST'])
def manage_barbers():
    try:
        if request.method == 'GET':
            barbers = Barber.query.all()
            return jsonify([{'id': b.id, 'name': b.name} for b in barbers])
        data = request.json
        new_barber = Barber(name=data['name'])
        db.session.add(new_barber)
        db.session.commit()
        return jsonify({'message': 'Ok'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/appointments', methods=['GET', 'POST'])
def manage_appointments():
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/costs', methods=['GET', 'POST'])
def manage_costs():
    try:
        if request.method == 'GET':
            costs = Cost.query.all()
            return jsonify([{'id': c.id, 'description': c.description, 'value': c.value} for c in costs])
        data = request.json
        new_cost = Cost(description=data['description'], value=data['value'])
        db.session.add(new_cost)
        db.session.commit()
        return jsonify({'message': 'Registrado'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
