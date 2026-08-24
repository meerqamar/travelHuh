/* Hotel Detail Interactions*/

document.addEventListener('DOMContentLoaded', () => {
  const bookingRoomName = document.getElementById('booking-room-name');
  const bookingBoard = document.getElementById('booking-board');
  const bookingTotal = document.getElementById('booking-total');
  const bookingContinue = document.querySelector('.sticky-bar a[href="checkout.html"]');

  const updateBookingSummary = (button) => {
    const pricePerPerson = Number(button.dataset.pricePp);
    const booking = {
      roomName: button.dataset.roomName,
      board: button.dataset.board,
      pricePerPerson,
      total: pricePerPerson * 2,
    };

    localStorage.setItem('travelHuhBooking', JSON.stringify(booking));
    if (bookingRoomName) bookingRoomName.textContent = booking.roomName;
    if (bookingBoard) bookingBoard.textContent = booking.board;
    if (bookingTotal) bookingTotal.textContent = `£${booking.total.toLocaleString('en-GB')}`;
    if (bookingContinue) bookingContinue.href = `/checkout/?room=${encodeURIComponent(booking.roomName)}`;
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
      }
    });
  });

  // --- Room Selection Logic ---
  const roomSelectBtns = document.querySelectorAll('.room-card__select');

  roomSelectBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
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
