<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BarberFlow - Gestão Profissional</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .sidebar-item:hover { background-color: #374151; }
        .active-menu { border-left: 4px solid #fbbf24; background-color: #374151; color: white !important; }
        .schedule-card { transition: all 0.2s; }
        .schedule-card:hover { transform: scale(1.01); background-color: #374151; }
        .slot-btn.selected { background-color: #fbbf24 !important; color: #1f2937 !important; transform: scale(1.1); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #1f2937; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 10px; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 font-sans">

    <div class="flex h-screen overflow-hidden">
        <!-- Sidebar Lateral -->
        <aside class="w-20 md:w-64 bg-gray-800 border-r border-gray-700 flex flex-col transition-all">
            <div class="p-4 text-center font-bold text-yellow-500 text-xl border-b border-gray-700 h-16 flex items-center justify-center">
                <i class="fas fa-scissors"></i> <span class="hidden md:inline ml-2 uppercase tracking-tighter">BarberFlow</span>
            </div>
            <nav class="flex-1 mt-4 overflow-y-auto">
                <a href="#" onclick="changeView('agenda', this)" class="sidebar-item flex items-center p-4 text-gray-400 active-menu" data-view="agenda">
                    <i class="fas fa-calendar-day w-6"></i> <span class="ml-3 hidden md:inline">Hoje</span>
                </a>
                <a href="#" onclick="changeView('future', this)" class="sidebar-item flex items-center p-4 text-gray-400" data-view="future">
                    <i class="fas fa-calendar-alt w-6"></i> <span class="ml-3 hidden md:inline">Futuros</span>
                </a>
                <a href="#" onclick="changeView('finance', this)" class="sidebar-item flex items-center p-4 text-gray-400" data-view="finance">
                    <i class="fas fa-wallet w-6"></i> <span class="ml-3 hidden md:inline">Financeiro</span>
                </a>
                <a href="#" onclick="changeView('booking', this)" class="sidebar-item flex items-center p-4 text-gray-400" data-view="booking">
                    <i class="fas fa-plus-circle w-6"></i> <span class="ml-3 hidden md:inline">Novo Agendamento</span>
                </a>
                <a href="#" onclick="changeView('settings', this)" class="sidebar-item flex items-center p-4 text-gray-400 border-t border-gray-700 mt-4" data-view="settings">
                    <i class="fas fa-cog w-6"></i> <span class="ml-3 hidden md:inline">Ajustes</span>
                </a>
            </nav>
        </aside>

        <!-- Área Principal -->
        <main id="main-content" class="flex-1 overflow-y-auto p-4 md:p-10 bg-gray-900">
            <div id="loader" class="flex flex-col items-center justify-center h-full">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-yellow-500 mb-4"></div>
                <p class="text-gray-500">Conectando ao servidor na nuvem...</p>
            </div>
        </main>
    </div>

    <!-- Modal de Alerta -->
    <div id="modal" class="fixed inset-0 bg-black/80 hidden items-center justify-center z-50 p-4">
        <div class="bg-gray-800 border border-gray-700 p-6 rounded-2xl max-w-sm w-full shadow-2xl text-center">
            <div id="modal-icon" class="text-4xl text-yellow-500 mb-4">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <h3 id="modal-title" class="text-xl font-bold mb-2"></h3>
            <p id="modal-msg" class="text-gray-400 mb-6"></p>
            <button onclick="closeModal()" class="w-full bg-yellow-500 text-gray-900 font-bold py-3 rounded-xl hover:bg-yellow-400 transition">Entendi</button>
        </div>
    </div>

    <script>
        /** * IMPORTANTE: Substitua a URL abaixo pela URL que o Render gerou para você!
         * Exemplo: https://barberflow-api.onrender.com
         */
        const API_URL = "https://barbearia-app.onrender.com"; 
        
        let SERVICES = [], BARBERS = [], APPOINTMENTS = [], COSTS = [];
        let currentView = 'agenda';
        let selectedTime = null;
        let isConnecting = false;

        async function init() {
            try {
                isConnecting = true;
                await loadData();
                isConnecting = false;
                renderCurrentView();
            } catch (e) {
                isConnecting = false;
                showModal(
                    "Erro de Conexão", 
                    "Não foi possível conectar ao servidor no Render. Verifique se o serviço está ativo ou se a URL no index.html está correta."
                );
                document.getElementById('main-content').innerHTML = `
                    <div class="flex flex-col items-center justify-center h-full text-center">
                        <i class="fas fa-cloud-slash text-red-500 text-5xl mb-4"></i>
                        <h2 class="text-2xl font-bold mb-2">Servidor Offline</h2>
                        <p class="text-gray-500 mb-6">URL configurada: ${API_URL}</p>
                        <button onclick="location.reload()" class="bg-gray-800 border border-gray-700 px-6 py-2 rounded-lg hover:bg-gray-700 transition">Tentar Novamente</button>
                    </div>
                `;
            }
        }

        async function loadData() {
            const fetchAPI = async (endpoint) => {
                const res = await fetch(`${API_URL}/${endpoint}`);
                if (!res.ok) throw new Error(`Falha: ${endpoint}`);
                return res.json();
            };

            const [services, barbers, appointments, costs] = await Promise.all([
                fetchAPI('services'),
                fetchAPI('barbers'),
                fetchAPI('appointments'),
                fetchAPI('costs')
            ]);

            SERVICES = services;
            BARBERS = barbers;
            APPOINTMENTS = appointments;
            COSTS = costs;
        }

        function changeView(view, el) {
            if (isConnecting) return;
            currentView = view;
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active-menu'));
            if(el) el.classList.add('active-menu');
            renderCurrentView();
        }

        function renderCurrentView() {
            const main = document.getElementById('main-content');
            if(currentView === 'agenda') main.innerHTML = renderAgenda(false);
            if(currentView === 'future') main.innerHTML = renderAgenda(true);
            if(currentView === 'finance') main.innerHTML = renderFinance();
            if(currentView === 'booking') main.innerHTML = renderBooking();
            if(currentView === 'settings') main.innerHTML = renderSettings();
        }

        function renderAgenda(isFuture) {
            const today = new Date().toISOString().split('T')[0];
            const list = APPOINTMENTS.filter(a => isFuture ? a.date > today : a.date === today)
                                    .filter(a => a.status !== 'cancelled')
                                    .sort((a,b) => (a.date + a.time).localeCompare(b.date + b.time));

            return `
                <h1 class="text-3xl font-black mb-8">${isFuture ? 'Próximos Dias' : 'Agenda de Hoje'}</h1>
                <div class="space-y-3">
                    ${list.length ? list.map(a => {
                        const s = SERVICES.find(s => s.id == a.service_id) || {name: 'Serviço', price: 0};
                        const b = BARBERS.find(b => b.id == a.barber_id) || {name: 'Barbeiro'};
                        return `
                            <div class="bg-gray-800/50 p-4 rounded-xl border border-gray-700 flex justify-between items-center schedule-card">
                                <div>
                                    <div class="flex items-center gap-3">
                                        <span class="text-yellow-500 font-bold">${a.time}</span>
                                        <span class="text-gray-500">|</span>
                                        <span class="font-bold">${a.client}</span>
                                    </div>
                                    <div class="text-sm text-gray-400">${s.name} • ${b.name}</div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <span class="text-green-400 font-bold">R$ ${s.price}</span>
                                    ${a.status !== 'completed' ? `
                                        <button onclick="updateStatus(${a.id}, 'completed')" class="bg-green-600 p-2 rounded text-xs font-bold px-4 hover:bg-green-500 transition">Concluir</button>
                                    ` : '<span class="text-xs text-gray-500">Finalizado</span>'}
                                </div>
                            </div>
                        `;
                    }).join('') : '<p class="text-gray-500 py-10">Agenda vazia.</p>'}
                </div>
            `;
        }

        function renderFinance() {
            const totalGanho = APPOINTMENTS.filter(a => a.status === 'completed')
                                          .reduce((acc, a) => acc + (SERVICES.find(s => s.id == a.service_id)?.price || 0), 0);
            const totalGasto = COSTS.reduce((acc, c) => acc + c.value, 0);

            return `
                <h1 class="text-3xl font-black mb-8">Financeiro</h1>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div class="bg-green-600/20 border border-green-500/30 p-6 rounded-2xl text-center">
                        <p class="text-sm text-green-400 font-bold">GANHOS</p>
                        <p class="text-3xl font-black">R$ ${totalGanho.toFixed(2)}</p>
                    </div>
                    <div class="bg-red-600/20 border border-red-500/30 p-6 rounded-2xl text-center">
                        <p class="text-sm text-red-400 font-bold">CUSTOS</p>
                        <p class="text-3xl font-black">R$ ${totalGasto.toFixed(2)}</p>
                    </div>
                    <div class="bg-blue-600/20 border border-blue-500/30 p-6 rounded-2xl text-center">
                        <p class="text-sm text-blue-400 font-bold">LUCRO</p>
                        <p class="text-3xl font-black">R$ ${(totalGanho - totalGasto).toFixed(2)}</p>
                    </div>
                </div>
                <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                    <h3 class="font-bold mb-4 uppercase text-xs text-gray-400">Registar Despesa</h3>
                    <form onsubmit="handleCost(event)" class="flex flex-col md:flex-row gap-3">
                        <input id="cost_desc" placeholder="Descrição" required class="flex-1 bg-gray-900 border border-gray-700 p-3 rounded-xl outline-none focus:border-yellow-500">
                        <input id="cost_val" type="number" step="0.01" placeholder="Valor" required class="w-full md:w-32 bg-gray-900 border border-gray-700 p-3 rounded-xl outline-none focus:border-yellow-500">
                        <button class="bg-red-600 px-6 py-3 rounded-xl font-bold hover:bg-red-700 transition">Adicionar</button>
                    </form>
                </div>
            `;
        }

        function renderBooking() {
            selectedTime = null;
            return `
                <div class="max-w-xl mx-auto bg-gray-800 p-8 rounded-3xl border border-gray-700 shadow-2xl">
                    <h2 class="text-2xl font-black mb-8 text-center uppercase text-yellow-500">Novo Agendamento</h2>
                    <form onsubmit="saveBooking(event)" class="space-y-4">
                        <input id="bk_name" placeholder="Nome do Cliente" required class="w-full bg-gray-900 border border-gray-700 p-4 rounded-xl focus:border-yellow-500 outline-none">
                        <div class="grid grid-cols-2 gap-4">
                            <select id="bk_svc" required class="bg-gray-900 border border-gray-700 p-4 rounded-xl outline-none">
                                <option value="">Serviço...</option>
                                ${SERVICES.map(s => `<option value="${s.id}">${s.name} (R$ ${s.price})</option>`).join('')}
                            </select>
                            <select id="bk_brb" required onchange="refreshSlots()" class="bg-gray-900 border border-gray-700 p-4 rounded-xl outline-none">
                                <option value="">Barbeiro...</option>
                                ${BARBERS.map(b => `<option value="${b.id}">${b.name}</option>`).join('')}
                            </select>
                        </div>
                        <input type="date" id="bk_date" value="${new Date().toISOString().split('T')[0]}" onchange="refreshSlots()" class="w-full bg-gray-900 border border-gray-700 p-4 rounded-xl outline-none">
                        <div id="slot-container" class="grid grid-cols-4 gap-2 py-4"></div>
                        <button class="w-full bg-yellow-500 text-gray-900 font-black py-4 rounded-xl hover:bg-yellow-600 transition">Reservar Agora</button>
                    </form>
                </div>
            `;
        }

        function renderSettings() {
            return `
                <div class="grid md:grid-cols-2 gap-8">
                    <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                        <h3 class="font-bold mb-4 text-yellow-500">Serviços</h3>
                        <form onsubmit="saveSvc(event)" class="flex gap-2 mb-6">
                            <input id="s_name" placeholder="Nome" required class="flex-1 bg-gray-900 border border-gray-700 p-2 rounded outline-none">
                            <input id="s_price" type="number" step="0.01" placeholder="R$" required class="w-20 bg-gray-900 border border-gray-700 p-2 rounded outline-none">
                            <button class="bg-yellow-500 text-black px-4 rounded font-bold"><i class="fas fa-plus"></i></button>
                        </form>
                        ${SERVICES.map(s => `<div class="p-2 border-b border-gray-700 flex justify-between"><span>${s.name}</span> <span>R$ ${s.price}</span></div>`).join('')}
                    </div>
                    <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
                        <h3 class="font-bold mb-4 text-blue-400">Barbeiros</h3>
                        <form onsubmit="saveBrb(event)" class="flex gap-2 mb-6">
                            <input id="b_name" placeholder="Nome" required class="flex-1 bg-gray-900 border border-gray-700 p-2 rounded outline-none">
                            <button class="bg-blue-600 px-4 rounded font-bold"><i class="fas fa-plus"></i></button>
                        </form>
                        ${BARBERS.map(b => `<div class="p-2 border-b border-gray-700">${b.name}</div>`).join('')}
                    </div>
                </div>
            `;
        }

        async function saveBooking(e) {
            e.preventDefault();
            if(!selectedTime) return showModal("Atenção", "Escolha um horário.");
            const data = {
                client: document.getElementById('bk_name').value,
                service_id: parseInt(document.getElementById('bk_svc').value),
                barber_id: parseInt(document.getElementById('bk_brb').value),
                date: document.getElementById('bk_date').value,
                time: selectedTime
            };
            await fetch(`${API_URL}/appointments`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data)});
            await loadData();
            changeView('agenda');
        }

        function refreshSlots() {
            const container = document.getElementById('slot-container');
            const hours = ["09:00","10:00","11:00","14:00","15:00","16:00","17:00"];
            container.innerHTML = hours.map(h => `<button type="button" onclick="selectSlot('${h}', this)" class="slot-btn p-2 rounded bg-gray-700 text-xs">${h}</button>`).join('');
        }

        window.selectSlot = (h, el) => {
            selectedTime = h;
            document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
            el.classList.add('selected');
        }

        async function updateStatus(id, status) {
            await fetch(`${API_URL}/appointments/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({status})});
            await loadData();
            renderCurrentView();
        }

        async function saveSvc(e) { e.preventDefault(); const data = { name: document.getElementById('s_name').value, price: parseFloat(document.getElementById('s_price').value)}; await fetch(`${API_URL}/services`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); await loadData(); renderCurrentView(); }
        async function saveBrb(e) { e.preventDefault(); const data = { name: document.getElementById('b_name').value }; await fetch(`${API_URL}/barbers`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); await loadData(); renderCurrentView(); }
        async function handleCost(e) { e.preventDefault(); const data = { description: document.getElementById('cost_desc').value, value: parseFloat(document.getElementById('cost_val').value)}; await fetch(`${API_URL}/costs`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); await loadData(); renderCurrentView(); }

        function showModal(title, msg) { document.getElementById('modal-title').innerText = title; document.getElementById('modal-msg').innerText = msg; document.getElementById('modal').classList.replace('hidden', 'flex'); }
        window.closeModal = () => document.getElementById('modal').classList.replace('flex', 'hidden');

        window.onload = init;
    </script>
</body>
</html>
