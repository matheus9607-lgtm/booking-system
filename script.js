// State
let currentRoom = null;
let currentPricePerHour = 0;
let currentWeekStart = new Date();
let selectedSlots = [];
let showMorning = false;
let apiSettings = null; // Cache settings

// API Base URL - Production
const API_URL = 'https://marcos-lima-booking.onrender.com/api';

// DOM Elements
const modal = document.getElementById('booking-modal');
const calendarMonthYear = document.getElementById('calendar-month-year');
const sidebarRoomName = document.getElementById('sidebar-room-name');
const sidebarDate = document.getElementById('sidebar-date');
const sidebarTime = document.getElementById('sidebar-time');
const sidebarTotal = document.getElementById('sidebar-total');

// Hours - split into morning and afternoon
const MORNING_HOURS = ['08:00', '09:00', '10:00', '11:00'];
const AFTERNOON_HOURS = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'];

function getHoursToShow() {
    return showMorning ? [...MORNING_HOURS, ...AFTERNOON_HOURS] : AFTERNOON_HOURS;
}

// Initialize
async function init() {
    const today = new Date();
    const day = today.getDay();
    const diff = today.getDate() - day + (day === 0 ? -6 : 1);
    currentWeekStart = new Date(today.setDate(diff));
    currentWeekStart.setHours(0, 0, 0, 0);

    await loadSettings();
    await renderRoomsGrid();
}

// Load Settings
async function loadSettings() {
    try {
        const response = await fetch(`${API_URL}/settings`);
        apiSettings = await response.json();
    } catch (error) {
        console.error('Error loading settings:', error);
        // Fallback
        apiSettings = { "startTime": "08:00", "endTime": "22:00", "workDays": ["1", "2", "3", "4", "5"] };
    }
}

init();

// Render rooms from API
async function renderRoomsGrid() {
    const container = document.getElementById('room-grid-container');

    try {
        const response = await fetch(`${API_URL}/rooms`);
        const rooms = await response.json();

        if (!rooms || rooms.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 3rem; color: #999;">Nenhuma sala disponível no momento.</p>';
            return;
        }

        container.innerHTML = '';

        rooms.forEach(room => {
            const card = document.createElement('article');
            card.className = 'room-card';
            card.onclick = () => openBooking(room.name, room.price);

            card.innerHTML = `
                <div class="room-image">
                    <img src="${room.image}" alt="${room.name}">
                </div>
                <div class="room-info">
                    <h3 class="room-name">${room.name}</h3>
                    <div class="room-price">R$ ${room.price.toFixed(2)} / hora</div>
                    <div class="room-features">
                        <span>${room.size}m²</span>
                        ${room.features.map(f => `<span>•</span><span>${f}</span>`).join('')}
                    </div>
                    <button class="btn-outline" style="width: 100%; margin-top: 1rem;">Reservar</button>
                </div>
            `;

            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading rooms:', error);
        container.innerHTML = '<p style="text-align: center; padding: 3rem; color: #ef4444;">Erro ao carregar salas. Verifique se o servidor está rodando.</p>';
    }
}

// Check if slot is blocked (by admin or existing booking)
async function isSlotBlocked(roomName, dateStr, timeStr) {
    try {
        // 1. Check Admin Blocks
        const blockedResponse = await fetch(`${API_URL}/blocked-slots`);
        const blockedMap = await blockedResponse.json();

        // We need room ID for blocked slots. 
        // Optimization: Store rooms in a global variable or fetch once.
        const roomsResponse = await fetch(`${API_URL}/rooms`);
        const rooms = await roomsResponse.json();
        const room = rooms.find(r => r.name === roomName);

        if (room && blockedMap[room.id]) {
            const isBlocked = blockedMap[room.id].some(slot => {
                if (slot.date !== dateStr) return false;
                return timeStr >= slot.startTime && timeStr < slot.endTime;
            });
            if (isBlocked) return true;
        }

        // 2. Check Existing Bookings
        const bookingsResponse = await fetch(`${API_URL}/bookings`);
        const bookings = await bookingsResponse.json();

        const isBooked = bookings.some(booking => {
            if (booking.room !== roomName) return false;
            return booking.slots.some(slot => slot.dateStr === dateStr && slot.time === timeStr);
        });

        return isBooked;
    } catch (error) {
        console.error('Error checking availability:', error);
        return false; // Fail safe
    }
}

// Open Booking Modal
async function openBooking(roomName, price) {
    currentRoom = roomName;
    currentPricePerHour = price;
    selectedSlots = [];

    sidebarRoomName.textContent = roomName;
    modal.style.display = 'flex';

    // Clear form inputs
    document.getElementById('customer-name').value = '';
    document.getElementById('customer-phone').value = '';

    await renderWeekGrid();
    updateSidebar();
    document.body.style.overflow = 'hidden';
}

// Close Booking Modal
function closeBooking() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Navigation
function changeWeek(delta) {
    currentWeekStart.setDate(currentWeekStart.getDate() + (delta * 7));
    renderWeekGrid();
}

function goToToday() {
    init();
    renderWeekGrid();
}

function toggleMorningHours() {
    showMorning = !showMorning;
    const btn = document.getElementById('morning-btn');
    btn.textContent = showMorning ? 'Ocultar horários da manhã' : 'Mostrar horários da manhã';
    renderWeekGrid();
}

// Date Picker State
let datePickerMonth = new Date();
let datePickerVisible = false;

function toggleDatePicker() {
    datePickerVisible = !datePickerVisible;
    const picker = document.getElementById('date-picker');

    if (datePickerVisible) {
        datePickerMonth = new Date(currentWeekStart);
        renderDatePicker();
        picker.style.display = 'block';
    } else {
        picker.style.display = 'none';
    }
}

function renderDatePicker() {
    const picker = document.querySelector('.date-picker-content');
    const month = datePickerMonth.toLocaleString('pt-BR', { month: 'long' });
    const year = datePickerMonth.getFullYear();
    const capitalizedMonth = month.charAt(0).toUpperCase() + month.slice(1);

    let html = '<div class="date-picker-header">';
    html += `<h4>${capitalizedMonth} ${year}</h4>`;
    html += '<div class="date-picker-nav">';
    html += '<button onclick="changeDatePickerMonth(-1)">‹</button>';
    html += '<button onclick="changeDatePickerMonth(1)">›</button>';
    html += '</div></div>';

    html += '<div class="date-picker-grid">';

    // Day headers
    const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    dayNames.forEach(day => {
        html += `<div class="date-picker-day-header">${day}</div>`;
    });

    // Get first day of month
    const firstDay = new Date(datePickerMonth.getFullYear(), datePickerMonth.getMonth(), 1);
    const lastDay = new Date(datePickerMonth.getFullYear(), datePickerMonth.getMonth() + 1, 0);
    const startDay = firstDay.getDay();
    const daysInMonth = lastDay.getDate();

    // Previous month days
    const prevMonthLastDay = new Date(datePickerMonth.getFullYear(), datePickerMonth.getMonth(), 0).getDate();
    for (let i = startDay - 1; i >= 0; i--) {
        html += `<div class="date-picker-day other-month">${prevMonthLastDay - i}</div>`;
    }

    // Current month days
    const today = new Date();
    const todayStr = formatDateKey(today);

    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(datePickerMonth.getFullYear(), datePickerMonth.getMonth(), day);
        const dateStr = formatDateKey(date);
        const isToday = dateStr === todayStr;
        const isSelected = dateStr === formatDateKey(currentWeekStart);

        let className = 'date-picker-day';
        if (isToday) className += ' today';
        if (isSelected) className += ' selected';

        html += `<div class="${className}" onclick="selectDate('${dateStr}')">${day}</div>`;
    }

    // Next month days
    const remainingDays = 42 - (startDay + daysInMonth);
    for (let i = 1; i <= remainingDays; i++) {
        html += `<div class="date-picker-day other-month">${i}</div>`;
    }

    html += '</div>';
    picker.innerHTML = html;
}

function changeDatePickerMonth(delta) {
    datePickerMonth.setMonth(datePickerMonth.getMonth() + delta);
    renderDatePicker();
}

function selectDate(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    const selectedDate = new Date(year, month - 1, day);

    // Find the Monday of the week containing this date
    const dayOfWeek = selectedDate.getDay();
    const diff = selectedDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    currentWeekStart = new Date(selectedDate.setDate(diff));
    currentWeekStart.setHours(0, 0, 0, 0);

    renderWeekGrid();
    toggleDatePicker();
}

// Helper: Format Date YYYY-MM-DD
function formatDateKey(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

// Helper: Check if slot is in the past
function isPast(dateStr, timeStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    const [hour, minute] = timeStr.split(':').map(Number);
    const slotDate = new Date(year, month - 1, day, hour, minute);
    const now = new Date();
    return slotDate < now;
}

// Render Grid (Table Layout - Times on Rows, Days on Columns)
async function renderWeekGrid() {
    const settings = apiSettings || { "workDays": ["1", "2", "3", "4", "5"] };

    let workDays = [];
    if (typeof settings.workDays === 'string') {
        if (settings.workDays.trim().startsWith('[')) {
            try {
                workDays = JSON.parse(settings.workDays);
            } catch (e) {
                console.error('Error parsing workDays JSON:', e);
                workDays = [];
            }
        } else {
            workDays = settings.workDays.split(',');
        }
    } else if (Array.isArray(settings.workDays)) {
        workDays = settings.workDays;
    }

    // Convert to numbers
    workDays = workDays.map(Number);

    const month = currentWeekStart.toLocaleString('pt-BR', { month: 'long' });
    const year = currentWeekStart.getFullYear();
    const capitalizedMonth = month.charAt(0).toUpperCase() + month.slice(1);
    calendarMonthYear.textContent = `Data da reserva: ${capitalizedMonth} ${year}`;

    const container = document.querySelector('.week-grid-container');
    const HOURS = getHoursToShow();

    // Fetch availability data once for the grid
    let blockedMap = {};
    let bookings = [];
    let rooms = [];
    let currentRoomId = null;

    try {
        const [blockedRes, bookingsRes, roomsRes] = await Promise.all([
            fetch(`${API_URL}/blocked-slots`),
            fetch(`${API_URL}/bookings`),
            fetch(`${API_URL}/rooms`)
        ]);

        blockedMap = await blockedRes.json();
        bookings = await bookingsRes.json();
        rooms = await roomsRes.json();

        const room = rooms.find(r => r.name === currentRoom);
        if (room) currentRoomId = room.id;

    } catch (e) {
        console.error("Error fetching grid data", e);
    }

    let html = '<div class="week-grid-table">';

    // Header Row
    html += '<div class="week-grid-header-row">';
    html += '<div class="week-grid-header-cell time-header"></div>';

    for (let i = 0; i < 7; i++) {
        const d = new Date(currentWeekStart);
        d.setDate(currentWeekStart.getDate() + i);
        const dayName = d.toLocaleString('pt-BR', { weekday: 'short' });
        const dayNumber = d.getDate();
        const dateStr = formatDateKey(d);
        const dayOfWeek = d.getDay();

        const hasSelectedSlots = selectedSlots.some(s => s.dateStr === dateStr);
        const isClosed = !workDays.includes(dayOfWeek);

        let className = 'week-grid-header-cell';
        if (dayOfWeek === 0) className += ' sunday';
        if (dayOfWeek === 6) className += ' saturday';
        if (hasSelectedSlots) className += ' selected-day';
        if (isClosed) className += ' closed-day';

        html += `<div class="${className}">
            ${dayName} ${dayNumber}
            ${isClosed ? '<span style="display:block; font-size:0.7em; color:#ef4444;">Fechado</span>' : ''}
        </div>`;
    }
    html += '</div>';

    // Time Rows
    HOURS.forEach(time => {
        html += '<div class="week-grid-row">';
        html += `<div class="week-grid-time-cell">${time}</div>`;

        for (let i = 0; i < 7; i++) {
            const d = new Date(currentWeekStart);
            d.setDate(currentWeekStart.getDate() + i);
            const dateStr = formatDateKey(d);
            const dayOfWeek = d.getDay();

            const isClosed = !workDays.includes(dayOfWeek);
            const isSelected = selectedSlots.some(s => s.dateStr === dateStr && s.time === time);
            const past = isPast(dateStr, time);

            // Check availability synchronously with pre-fetched data
            let isOccupied = false;

            // 1. Admin Block
            if (currentRoomId && blockedMap[currentRoomId]) {
                isOccupied = blockedMap[currentRoomId].some(slot => {
                    if (slot.date !== dateStr) return false;
                    return time >= slot.startTime && time < slot.endTime;
                });
            }

            // 2. Existing Bookings (only approved ones)
            if (!isOccupied) {
                isOccupied = bookings.some(booking => {
                    if (booking.room !== currentRoom) return false;
                    if (booking.status !== 'approved') return false; // Only show approved bookings as occupied
                    return booking.slots.some(slot => slot.dateStr === dateStr && slot.time === time);
                });
            }

            let className = 'week-grid-slot';
            if (isClosed) className += ' closed';
            else if (past) className += ' disabled';
            else if (isOccupied) className += ' occupied';
            else if (isSelected) className += ' selected';

            const onclick = (!isClosed && !past && !isOccupied) ? ` onclick="toggleSlot('${dateStr}', '${time}')"` : '';

            html += `<div class="${className}"${onclick}>`;

            if (isSelected) {
                const selectedOnDay = selectedSlots.filter(s => s.dateStr === dateStr).sort((a, b) => a.time.localeCompare(b.time));
                const isFirst = selectedOnDay[0].time === time;

                if (isFirst) {
                    const duration = selectedOnDay.length;
                    const total = calculateTotal(selectedOnDay, currentPricePerHour);
                    html += `<span class="slot-duration">${duration} hora${duration > 1 ? 's' : ''}</span>`;
                    html += `<span class="slot-total">R$ ${total}</span>`;
                }
            } else if (!isClosed && !past && !isOccupied) {
                // Show price for available slots
                const slotPrice = calculateSlotPrice(dateStr, time, currentPricePerHour);
                html += `<span class="slot-price">R$ ${slotPrice}</span>`;
            }

            html += '</div>';
        }

        html += '</div>';
    });

    html += '</div>';
    container.innerHTML = html;
}

// Toggle Slot Selection (Contiguous-Only Logic)
function toggleSlot(dateStr, time) {
    const existingIndex = selectedSlots.findIndex(s => s.dateStr === dateStr && s.time === time);

    // If clicking on a different day, clear all selections
    if (selectedSlots.length > 0 && selectedSlots[0].dateStr !== dateStr) {
        selectedSlots = [];
    }

    if (existingIndex !== -1) {
        // Deselecting a slot
        selectedSlots.splice(existingIndex, 1);
    } else {
        // Selecting a new slot
        const HOURS = getHoursToShow();

        if (selectedSlots.length === 0) {
            // First selection
            selectedSlots.push({ dateStr, time });
        } else {
            // Check if the new slot is contiguous with existing selections
            const times = selectedSlots.map(s => s.time).sort();
            const newHourIndex = HOURS.indexOf(time);
            const minHourIndex = HOURS.indexOf(times[0]);
            const maxHourIndex = HOURS.indexOf(times[times.length - 1]);

            // Allow selection only if it's adjacent to the current range
            if (newHourIndex === minHourIndex - 1 || newHourIndex === maxHourIndex + 1) {
                selectedSlots.push({ dateStr, time });
            } else if (newHourIndex >= minHourIndex && newHourIndex <= maxHourIndex) {
                // Filling a gap within the range
                selectedSlots.push({ dateStr, time });
            } else {
                // Not contiguous - replace with new selection
                selectedSlots = [{ dateStr, time }];
            }
        }
    }
    renderWeekGrid();
    updateSidebar();
}

// Helper: Calculate Price for a Single Slot
function calculateSlotPrice(dateStr, time, basePrice) {
    let slotPrice = basePrice;

    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
    const hour = parseInt(time.split(':')[0]);

    // Surcharge Logic: Weekend (Sat/Sun) OR Evening (>= 18:00)
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isEvening = hour >= 18;

    if (isWeekend || isEvening) {
        slotPrice += 100;
    }
    return slotPrice;
}

// Helper: Calculate Total with Dynamic Pricing and Progressive Discount
function calculateTotal(slots, basePricePerHour) {
    if (!slots || slots.length === 0) return 0;

    let rawTotal = 0;

    slots.forEach(slot => {
        rawTotal += calculateSlotPrice(slot.dateStr, slot.time, basePricePerHour);
    });

    // Progressive Discount: R$ 50 off for each additional hour
    const duration = slots.length;
    const discount = duration > 1 ? (duration - 1) * 50 : 0;

    return rawTotal - discount;
}

// Update Sidebar
function updateSidebar() {
    if (selectedSlots.length === 0) {
        sidebarDate.textContent = '-';
        sidebarTime.textContent = '-';
        sidebarTotal.textContent = 'R$ 0,00';
        return;
    }

    selectedSlots.sort((a, b) => a.time.localeCompare(b.time));

    const dateParts = selectedSlots[0].dateStr.split('-');
    const dateObj = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
    sidebarDate.textContent = dateObj.toLocaleDateString('pt-BR');

    // Calculate time range
    const startTime = selectedSlots[0].time;
    const duration = selectedSlots.length;

    // Calculate end time
    const [startHour, startMinute] = startTime.split(':').map(Number);
    const endHour = startHour + duration;
    const endTime = `${String(endHour).padStart(2, '0')}:${String(startMinute).padStart(2, '0')}`;

    // Format: "2 horas 13:00 - 15:00" or "1 hora 13:00 - 14:00"
    const timeRange = duration > 1
        ? `${duration} horas ${startTime} - ${endTime}`
        : `${duration} hora ${startTime} - ${endTime}`;

    sidebarTime.textContent = timeRange;

    const total = calculateTotal(selectedSlots, currentPricePerHour);
    sidebarTotal.textContent = total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// Confirm Booking
async function confirmBooking() {
    if (selectedSlots.length === 0) {
        showToast('Por favor, selecione pelo menos um horário.', 'error');
        return;
    }

    const customerName = document.getElementById('customer-name').value.trim();
    const customerPhone = document.getElementById('customer-phone').value.trim();

    if (!customerName || !customerPhone) {
        showToast('Por favor, preencha seu nome e telefone.', 'error');
        return;
    }

    const booking = {
        room: currentRoom,
        date: sidebarDate.textContent,
        timeRange: sidebarTime.textContent,
        total: sidebarTotal.textContent,
        customerName: customerName,
        customerPhone: customerPhone,
        createdAt: new Date().toISOString(),
        slots: selectedSlots
    };

    try {
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(booking)
        });

        if (response.ok) {
            showToast('Reserva confirmada com sucesso! Redirecionando para WhatsApp...', 'success');

            // WhatsApp Integration - Mobile friendly
            const phone = '5592993404476';
            const message = `*Nova Reserva Solicitada* 📸\n\n` +
                `*Cliente:* ${booking.customerName}\n` +
                `*Telefone:* ${booking.customerPhone}\n` +
                `*Sala:* ${booking.room}\n` +
                `*Data:* ${booking.date}\n` +
                `*Horário:* ${booking.timeRange}\n` +
                `*Valor Total:* ${booking.total}\n\n` +
                `Aguardo confirmação!`;

            const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;

            // Close modal first
            closeBooking();

            // Redirect to WhatsApp after a short delay
            setTimeout(() => {
                window.location.href = whatsappUrl;
            }, 500);

            // Refresh grid
            renderWeekGrid();
        } else {
            showToast('Erro ao salvar reserva.', 'error');
        }
    } catch (error) {
        console.error('Error saving booking:', error);
        showToast('Erro de conexão com o servidor.', 'error');
    }
}

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? '✅' : '⚠️';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Close modal when clicking outside
window.onclick = function (event) {
    if (event.target == modal) {
        closeBooking();
    }
}

// Header Scroll Effect
window.addEventListener('scroll', () => {
    const header = document.getElementById('main-header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});
