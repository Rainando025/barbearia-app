from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import sys

# Inicializa o Flask.
app = Flask(__name__, template_folder='templates')
CORS(app) 

# --- CONFIGURAÇÃO DINÂMICA DO BANCO DE DADOS ---

# 1. Pega a URL das variáveis de ambiente do Render
uri = os.environ.get('DATABASE_URL')

if uri:
    # Correção para o SQLAlchemy 2.0+ aceitar links postgres:// (comum no Render/Heroku)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # Se for Supabase e estiver usando a porta 5432, as vezes o Render exige SSL explícito
    # Ou recomenda-se usar a porta 6543 para Pooling. 
    # Vou forçar o parâmetro de SSL que resolve o erro e3q8 na maioria das vezes.
    if "sslmode" not in uri:
        separator = "&" if "?" in uri else "?"
        uri += f"{separator}sslmode=require"
else:
    # Fallback Localhost
    uri = 'postgresql://postgres:wordKey##@localhost:5433/barberflow'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Adiciona timeout e configurações de pool para evitar conexões "penduradas"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
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
        # Tenta criar as tabelas se não existirem
        db.create_all()
        print(">>> [LOG] Conexão com Supabase estabelecida e tabelas verificadas.")
    except Exception as e:
        print(f">>> [CRÍTICO] Erro de conexão com o Banco de Dados: {e}", file=sys.stderr)

# --- ROTAS ---

@app.route('/')
def index():
    return jsonify({
        "message": "BarberFlow API Online",
        "database_status": "Tentativa de conexão realizada"
    })

@app.route('/api/status')
def status():
    return jsonify({"status": "online"})

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
