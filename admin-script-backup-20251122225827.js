// Admin Authentication
const ADMIN_CREDENTIALS = {
    username: 'admin',
    password: 'admin123'
};

// API Base URL - Dynamic to work on mobile
const API_URL = `http://${window.location.hostname}:5000/api`;

// Initialize data structure
let roomsData = [];
let blockedSlots = {};
let currentEditingRoomId = null;
let confirmCallback = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadDataFromStorage();
});

// Authentication
function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-message');

    if (username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password) {
        sessionStorage.setItem('adminLoggedIn', 'true');
        showDashboard();
    } else {
        errorMsg.textContent = 'Usuário ou senha incorretos';
    }
}

function checkAuth() {
    const isLoggedIn = sessionStorage.getItem('adminLoggedIn');
    if (isLoggedIn === 'true') {
        showDashboard();
    }
}

function showDashboard() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('admin-dashboard').style.display = 'flex';
    loadRooms();
    loadRoomSelect();
}

function handleLogout() {
    sessionStorage.removeItem('adminLoggedIn');
    location.reload();
}

// Load data from API
async function loadDataFromStorage() {
    try {
        const roomsResponse = await fetch(`${API_URL}/rooms`);
        roomsData = await roomsResponse.json();

        const blockedResponse = await fetch(`${API_URL}/blocked-slots`);
        blockedSlots = await blockedResponse.json();
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Erro ao carregar dados do servidor. Verifique se o backend está rodando.');
    }
}

function saveRoomsToStorage() {
    // No longer needed, individual actions save to DB
    updateMainSite();
}

function saveBlockedSlotsToStorage() {
    // No longer needed
}

function updateMainSite() {
    // Trigger update in main site via event if needed, but main site fetches from API now.
    // We can dispatch a storage event just in case legacy listeners exist, but it's less relevant.
    localStorage.setItem('set92_rooms_updated', Date.now().toString());
}

// Section Navigation
function showSection(sectionName) {
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    document.getElementById(`${sectionName}-section`).style.display = 'block';
    event.target.closest('.nav-item').classList.add('active');

    if (sectionName === 'rooms') {
        loadRooms();
    } else if (sectionName === 'availability') {
        loadRoomSelect();
        loadAvailability();
    } else if (sectionName === 'bookings') {
        loadBookings();
    } else if (sectionName === 'settings') {
        loadSettings();
    }
}

// Rooms Management
async function loadRooms() {
    const roomsList = document.getElementById('rooms-list');
    roomsList.innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/rooms`);
        roomsData = await response.json();

        roomsData.forEach(room => {
            const card = document.createElement('div');
            card.className = 'room-card-admin';
            card.innerHTML = `
                <h3>${room.name}</h3>
                <div class="room-info-item">
                    <span class="room-info-label">Preço/hora:</span>
                    <span class="room-info-value">R$ ${room.price.toFixed(2)}</span>
                </div>
                <div class="room-info-item">
                    <span class="room-info-label">Tamanho:</span>
                    <span class="room-info-value">${room.size}m²</span>
                </div>
                <div class="room-info-item">
                    <span class="room-info-label">Características:</span>
                    <span class="room-info-value">${room.features.join(', ')}</span>
                </div>
                <div class="room-actions">
                    <button class="btn-edit" onclick="editRoom(${room.id})">Editar</button>
                    <button class="btn-delete" onclick="deleteRoom(${room.id})">Excluir</button>
                </div>
            `;
            roomsList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

function addNewRoom() {
    currentEditingRoomId = null;
    document.getElementById('modal-title').textContent = 'Nova Sala';
    document.getElementById('room-id').value = '';
    document.getElementById('room-name').value = '';
    document.getElementById('room-price').value = '';
    document.getElementById('room-size').value = '';
    document.getElementById('room-features').value = '';
    document.getElementById('room-image').value = '';
    document.getElementById('edit-room-modal').style.display = 'flex';
}

function editRoom(roomId) {
    const room = roomsData.find(r => r.id === roomId);
    if (!room) return;

    currentEditingRoomId = roomId;
    document.getElementById('modal-title').textContent = 'Editar Sala';
    document.getElementById('room-id').value = room.id;
    document.getElementById('room-name').value = room.name;
    document.getElementById('room-price').value = room.price;
    document.getElementById('room-size').value = room.size;
    document.getElementById('room-features').value = room.features.join(', ');
    document.getElementById('room-image').value = room.image || '';
    document.getElementById('edit-room-modal').style.display = 'flex';
}

async function saveRoom(event) {
    event.preventDefault();

    const roomData = {
        name: document.getElementById('room-name').value,
        price: parseFloat(document.getElementById('room-price').value),
        size: parseInt(document.getElementById('room-size').value),
        features: document.getElementById('room-features').value.split(',').map(f => f.trim()),
        image: document.getElementById('room-image').value || 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069&auto=format&fit=crop'
    };

    try {
        if (currentEditingRoomId) {
            await fetch(`${API_URL}/rooms/${currentEditingRoomId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roomData)
            });
        } else {
            await fetch(`${API_URL}/rooms`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roomData)
            });
        }

        loadRooms();
        closeEditModal();
        updateMainSite();
    } catch (error) {
        console.error('Error saving room:', error);
        alert('Erro ao salvar sala.');
        showConfirmModal(
            'Confirmar Exclusão',
            'Tem certeza que deseja excluir esta sala?',
            async () => {
                try {
                    await fetch(`${API_URL}/rooms/${id}`, { method: 'DELETE' });
                    loadRooms();
                    updateMainSite();
                    setTimeout(() => alert('Sala excluída com sucesso!'), 100);
                } catch (error) {
                    console.error('Error deleting room:', error);
                    alert('Erro ao excluir sala.');
                }
            }
        );
    }

    function closeEditModal() {
        document.getElementById('edit-room-modal').style.display = 'none';
    }

    // Availability Management
    function loadRoomSelect() {
        const select = document.getElementById('room-select');
        select.innerHTML = '<option value="">Selecione uma sala</option>';

        roomsData.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = room.name;
            select.appendChild(option);
        });
    }

    async function loadAvailability() {
        const roomId = document.getElementById('room-select').value;
        if (!roomId) return;

        const blockedList = document.getElementById('blocked-list');
        blockedList.innerHTML = '';

        try {
            const response = await fetch(`${API_URL}/blocked-slots`);
            blockedSlots = await response.json();

            const roomBlocked = blockedSlots[roomId] || [];

            if (roomBlocked.length === 0) {
                blockedList.innerHTML = '<p class="empty-state">Nenhum horário bloqueado para esta sala.</p>';
                return;
            }

            roomBlocked.forEach((slot, index) => {
                const item = document.createElement('div');
                item.className = 'blocked-slot-item';
                item.innerHTML = `
                <div class="blocked-slot-info">
                    <strong>${slot.date}</strong><br>
                    ${slot.startTime} - ${slot.endTime}
                </div>
                <button class="btn-unblock" onclick="unblockSlot(${roomId}, ${index})">Desbloquear</button>
            `;
                blockedList.appendChild(item);
            });
        } catch (error) {
            console.error('Error loading availability:', error);
        }
    }

    async function blockTimeSlot() {
        const roomId = document.getElementById('room-select').value;
        const date = document.getElementById('block-date').value;
        const startTime = document.getElementById('block-start-time').value;
        const endTime = document.getElementById('block-end-time').value;

        if (!roomId || !date || !startTime || !endTime) {
            alert('Por favor, preencha todos os campos');
            return;
        }

        try {
            await fetch(`${API_URL}/blocked-slots`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    roomId,
                    date,
                    startTime,
                    endTime
                })
            });

            loadAvailability();
            document.getElementById('block-date').value = '';
            alert('Horário bloqueado com sucesso!');
        } catch (error) {
            console.error('Error blocking slot:', error);
            alert('Erro ao bloquear horário.');
        }
    }

    function unblockSlot(roomId, index) {
        showConfirmModal(
            'Desbloquear Horário',
            'Deseja realmente desbloquear este horário?',
            async () => {
                try {
                    await fetch(`${API_URL}/blocked-slots/${roomId}/${index}`, { method: 'DELETE' });
                    loadAvailability();
                    setTimeout(() => alert('Horário desbloqueado com sucesso!'), 100);
                } catch (error) {
                    console.error('Error unblocking slot:', error);
                    alert('Erro ao desbloquear horário.');
                }
            }
        );
    }

    // Bookings Management
    async function loadBookings() {
        const bookingsList = document.getElementById('bookings-list');

        try {
            const response = await fetch(`${API_URL}/bookings`);
            const bookings = await response.json();

            if (bookings.length === 0) {
                bookingsList.innerHTML = '<p class="empty-state">Nenhuma reserva registrada ainda.</p>';
                return;
            }

            // Sort by date (newest first)
            bookings.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

            bookingsList.innerHTML = '';

            bookings.forEach((booking) => {
                const card = document.createElement('div');
                card.className = 'booking-card';

                const createdDate = new Date(booking.createdAt).toLocaleString('pt-BR');

                // Status badge
                const statusClass = booking.status === 'approved' ? 'status-approved' :
                    booking.status === 'rejected' ? 'status-rejected' : 'status-pending';
                const statusText = booking.status === 'approved' ? 'Aprovada' :
                    booking.status === 'rejected' ? 'Rejeitada' : 'Pendente';

                // Action buttons based on status
                let actionButtons = '';
                if (booking.status === 'pending') {
                    actionButtons = `
                    <button class="btn-approve" onclick="approveBooking(${booking.id})">✓ Aprovar</button>
                    <button class="btn-reject" onclick="rejectBooking(${booking.id})">✗ Rejeitar</button>
                `;
                } else {
                    actionButtons = `<button class="btn-delete" onclick="deleteBooking(${booking.id})">Excluir</button>`;
                }

                card.innerHTML = `
                <div class="booking-info">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>${booking.customerName}</h3>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                    <div class="booking-details">
                        <span><strong>Sala:</strong> ${booking.room}</span>
                        <span><strong>Data:</strong> ${booking.date}</span>
                        <span><strong>Horário:</strong> ${booking.timeRange}</span>
                        <span><strong>Total:</strong> ${booking.total}</span>
                        <span><strong>Telefone:</strong> ${booking.customerPhone}</span>
                    </div>
                    <div class="booking-meta">
                        Reservado em: ${createdDate}
                    </div>
                </div>
                <div class="booking-actions">
                    ${actionButtons}
                </div>
            `;
                bookingsList.appendChild(card);
            });
        } catch (error) {
            console.error('Error loading bookings:', error);
            bookingsList.innerHTML = '<p class="empty-state">Erro ao carregar reservas.</p>';
        }
    }

    function deleteBooking(id) {
        showConfirmModal(
            'Excluir Reserva',
            'Tem certeza que deseja excluir esta reserva?',
            async () => {
                try {
                    await fetch(`${API_URL}/bookings/${id}`, { method: 'DELETE' });
                    loadBookings();
                    setTimeout(() => alert('Reserva excluída com sucesso!'), 100);
                } catch (error) {
                    console.error('Error deleting booking:', error);
                    alert('Erro ao excluir reserva.');
                }
            }
        );
    }

    function approveBooking(id) {
        console.log('approveBooking called with id:', id, 'type:', typeof id);
        showConfirmModal(
            'Aprovar Reserva',
            'Confirmar aprovação desta reserva?',
            async () => {
                console.log('Approve callback executing for id:', id);
                try {
                    const url = `${API_URL}/bookings/${id}/approve`;
                    console.log('Fetching:', url);
                    const response = await fetch(url, { method: 'PUT' });
                    console.log('Approve response status:', response.status);
                    const responseData = await response.json();
                    console.log('Approve response data:', responseData);
                    loadBookings();
                    setTimeout(() => alert('Reserva aprovada com sucesso!'), 100);
                } catch (error) {
                    console.error('Error approving booking:', error);
                    alert('Erro ao aprovar reserva.');
                }
            }
        );
    }

    function rejectBooking(id) {
        showConfirmModal(
            'Rejeitar Reserva',
            'Tem certeza que deseja rejeitar esta reserva?',
            async () => {
                try {
                    await fetch(`${API_URL}/bookings/${id}/reject`, { method: 'PUT' });
                    loadBookings();
                    setTimeout(() => alert('Reserva rejeitada!'), 100);
                } catch (error) {
                    console.error('Error rejecting booking:', error);
                    alert('Erro ao rejeitar reserva.');
                }
            }
        );
    }

    // Settings Management
    async function loadSettings() {
        try {
            const response = await fetch(`${API_URL}/settings`);
            const settings = await response.json();

            document.getElementById('setting-start-time').value = settings.startTime || '08:00';
            document.getElementById('setting-end-time').value = settings.endTime || '22:00';

            // Reset checkboxes
            document.querySelectorAll('input[name="work-days"]').forEach(cb => cb.checked = false);

            // Set checked days
            const workDays = typeof settings.workDays === 'string' ? JSON.parse(settings.workDays) : (settings.workDays || []);
            workDays.forEach(day => {
                const cb = document.querySelector(`input[name="work-days"][value="${day}"]`);
                if (cb) cb.checked = true;
            });
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    async function saveSettings(event) {
        event.preventDefault();

        const startTime = document.getElementById('setting-start-time').value;
        const endTime = document.getElementById('setting-end-time').value;

        const workDays = [];
        document.querySelectorAll('input[name="work-days"]:checked').forEach(cb => {
            workDays.push(cb.value);
        });

        const settings = {
            startTime,
            endTime,
            workDays
        };

        try {
            await fetch(`${API_URL}/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });

            updateMainSite();
            alert('Configurações salvas com sucesso!');
        } catch (error) {
            console.error('Error saving settings:', error);
            alert('Erro ao salvar configurações.');
        }
    }
