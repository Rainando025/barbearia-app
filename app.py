from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
# O CORS é vital para que o ficheiro index.html consiga falar com este servidor
CORS(app) 

# Configuração do PostgreSQL
# Certifica-te de que o utilizador 'postgres' e a base de dados 'barberflow' existem no teu PGAdmin
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:wordKey##@localhost:5433/barberflow'
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

# Inicialização segura das tabelas
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"ERRO CRÍTICO: Não foi possível ligar ao Postgres. Verifique as credenciais. Detalhe: {e}")

# --- ROTAS DA API E FRONTEND ---

# Rota principal que agora carrega o ficheiro HTML
@app.route('/')
def index():
    # Certifique-se de que o index.html está dentro de uma pasta chamada 'templates'
    return render_template('index.html')

# Endpoint de verificação de status
@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "message": "Servidor BarberFlow Ativo."
    })

# Serviços
@app.route('/services', methods=['GET', 'POST'])
def manage_services():
    if request.method == 'GET':
        services = Service.query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'price': s.price} for s in services])
    
    data = request.json
    new_service = Service(name=data['name'], price=data['price'])
    db.session.add(new_service)
    db.session.commit()
    return jsonify({'message': 'Serviço adicionado'}), 201

@app.route('/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Serviço removido'})

# Barbeiros
@app.route('/barbers', methods=['GET', 'POST'])
def manage_barbers():
    if request.method == 'GET':
        barbers = Barber.query.all()
        return jsonify([{'id': b.id, 'name': b.name} for b in barbers])
    
    data = request.json
    new_barber = Barber(name=data['name'])
    db.session.add(new_barber)
    db.session.commit()
    return jsonify({'message': 'Barbeiro adicionado'}), 201

@app.route('/barbers/<int:id>', methods=['DELETE'])
def delete_barber(id):
    barber = Barber.query.get_or_404(id)
    db.session.delete(barber)
    db.session.commit()
    return jsonify({'message': 'Barbeiro removido'})

# Agendamentos
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
    return jsonify({'message': 'Agendamento criado'}), 201

@app.route('/appointments/<int:id>', methods=['PUT', 'DELETE'])
def update_appointment(id):
    appo = Appointment.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        if 'status' in data:
            appo.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Status atualizado'})
    
    db.session.delete(appo)
    db.session.commit()
    return jsonify({'message': 'Agendamento removido'})

# Custos/Despesas
@app.route('/costs', methods=['GET', 'POST'])
def manage_costs():
    if request.method == 'GET':
        costs = Cost.query.all()
        return jsonify([{'id': c.id, 'description': c.description, 'value': c.value} for c in costs])
    
    data = request.json
    new_cost = Cost(description=data['description'], value=data['value'])
    db.session.add(new_cost)
    db.session.commit()
    return jsonify({'message': 'Despesa registrada'}), 201

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)