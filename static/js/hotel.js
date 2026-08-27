/* Hotel Detail Interactions*/

document.addEventListener('DOMContentLoaded', () => {
  const bookingRoomName = document.getElementById('booking-room-name');
  const bookingBoard = document.getElementById('booking-board');
  const bookingTotal = document.getElementById('booking-total');
  const bookingContinue = document.querySelector('.sticky-bar a[href^="/checkout/"]');
  const searchParams = new URLSearchParams(window.location.search);
  const checkIn = searchParams.get('check_in') || '2026-07-15';
  const checkOut = searchParams.get('check_out') || '2026-07-22';
  const requestedGuests = Math.max(1, Number(searchParams.get('guests') || 2));

  const updateBookingSummary = (button) => {
    if (!button) return;
    const pricePerPerson = Number(button.dataset.pricePp);
    const booking = {
      roomId: button.dataset.roomId,
      roomName: button.dataset.roomName,
      board: button.dataset.board,
      pricePerPerson,
      guests: requestedGuests,
      checkIn,
      checkOut,
      location: document.body.dataset.hotelLocation || '',
      total: pricePerPerson * requestedGuests,
    };

    localStorage.setItem('travelHuhBooking', JSON.stringify(booking));
    if (bookingRoomName) bookingRoomName.textContent = booking.roomName;
    if (bookingBoard) bookingBoard.textContent = booking.board;
    if (bookingTotal) bookingTotal.textContent = `Rs ${booking.total.toLocaleString('en-PK')}`;
    if (bookingContinue) bookingContinue.href = `/checkout/?check_in=${encodeURIComponent(booking.checkIn)}&check_out=${encodeURIComponent(booking.checkOut)}&guests=${booking.guests}&room_id=${encodeURIComponent(booking.roomId)}`;
  };

  // --- Tabs Logic ---
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active classes
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      // Add active class to clicked
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-target');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('active');
        if (targetId === 'location' && window.hotelMap) {
          setTimeout(() => {
            window.hotelMap.invalidateSize();
          }, 100);
        }
      }
    });
  });

  // --- Room Selection Logic ---
  const roomSelectBtns = document.querySelectorAll('.room-card__select');

  roomSelectBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const requestedGuests = Number(new URLSearchParams(window.location.search).get('guests') || 2);
      if (requestedGuests > Number(btn.dataset.maxGuests)) {
        btn.title = `This room accommodates a maximum of ${btn.dataset.maxGuests} guests.`;
        return;
      }
      // Reset all cards
      const allCards = document.querySelectorAll('.room-card');
      const allRadios = document.querySelectorAll('.room-card__radio');
      const allSelectBtns = document.querySelectorAll('.room-card__select');

      allCards.forEach(c => {
        c.classList.remove('selected');
        const actionArea = c.querySelector('.room-card__action');
        if (actionArea) actionArea.classList.remove('bg-pink-light');
      });
      
      allRadios.forEach(r => r.classList.remove('active'));
      
      allSelectBtns.forEach(b => {
        b.classList.remove('active');
        b.innerHTML = '<span class="room-card__radio"></span> SELECT';
      });

      // Set active state on clicked card
      const card = btn.closest('.room-card');
      card.classList.add('selected');
      
      const actionArea = card.querySelector('.room-card__action');
      if (actionArea) actionArea.classList.add('bg-pink-light');

      btn.classList.add('active');
      btn.innerHTML = '<span class="room-card__radio active"></span> SELECTED';
      updateBookingSummary(btn);
    });
  });

  const savedBooking = JSON.parse(localStorage.getItem('travelHuhBooking') || 'null');
  const savedRoomButton = Array.from(roomSelectBtns).find(button => button.dataset.roomName === savedBooking?.roomName);
  updateBookingSummary(savedRoomButton || document.querySelector('.room-card__select.active'));
});
