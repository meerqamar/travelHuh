/* Checkout Interactions*/

const formatPKR = (value) => `Rs ${Math.round(Number(value)).toLocaleString('en-PK')}`;

document.addEventListener('DOMContentLoaded', () => {
  const btnAddCover = document.getElementById('btn-add-cover');
  const coverCostRow = document.getElementById('cover-cost-row');
  const totalPriceEl = document.getElementById('total-price');
  const checkoutHotelName = document.getElementById('checkout-hotel-name');
  const checkoutLocation = document.getElementById('checkout-hotel-location');
  const confirmBooking = document.getElementById('confirm-booking');
  const checkoutSteps = document.querySelectorAll('.checkout-stepper .step');
  const paymentSection = document.getElementById('payment-section');
  const checkoutForm = document.getElementById('checkout-form');
  const coverInput = document.getElementById('checkout-travel-cover');
  const adultsLabel = document.getElementById('checkout-adults-label');
  const roomTotalEl = document.getElementById('checkout-room-total');
  const booking = JSON.parse(localStorage.getItem('travelHuhBooking') || 'null');

  const coverPrice = Number(totalPriceEl?.dataset.coverPrice || 2500);
  const roomTotal = Number(totalPriceEl?.dataset.roomTotal || 0);
  const transportTotal = Number(totalPriceEl?.dataset.transportTotal || 0);
  let baseTotal = roomTotal + transportTotal;
  
  // Fallback for non-dataset versions
  if (baseTotal === 0 && document.getElementById('checkout-total-price')?.value) {
      baseTotal = Number(document.getElementById('checkout-total-price').value);
  }
  
  let coverAdded = false;
  let paymentReady = false;

  if (booking) {
    if (checkoutHotelName && !checkoutHotelName.textContent.includes(booking.roomName || '')) {
      checkoutHotelName.textContent = `${booking.roomName} - ${booking.board}`;
    }
    if (!document.getElementById('checkout-room-id').value) {
      document.getElementById('checkout-room-id').value = booking.roomId || '';
    }
    document.getElementById('checkout-guests').value = booking.guests || document.getElementById('checkout-guests').value;
    document.getElementById('checkout-check-in').value = booking.checkIn || document.getElementById('checkout-check-in').value;
    document.getElementById('checkout-check-out').value = booking.checkOut || document.getElementById('checkout-check-out').value;
    if (!basePrice && booking.total) basePrice = Number(booking.total);
    if (adultsLabel) adultsLabel.textContent = `Adults (x${booking.guests || 2})`;
    if (roomTotalEl && basePrice) roomTotalEl.textContent = formatPKR(basePrice);
    if (checkoutLocation && booking.location) checkoutLocation.textContent = booking.location;
  }

  const currentTotal = () => basePrice + (coverAdded ? coverPrice : 0);

  const refreshTotals = () => {
    const total = currentTotal();
    if (totalPriceEl) totalPriceEl.textContent = formatPKR(total);
    document.getElementById('checkout-total-price').value = total.toFixed(2);
    if (coverInput) coverInput.value = coverAdded ? '1' : '0';
    if (paymentReady && confirmBooking) confirmBooking.textContent = `Pay ${formatPKR(total)}`;
  };

  refreshTotals();

  if (confirmBooking) {
    const requiredFields = ['firstName', 'lastName', 'dob', 'gender', 'email', 'phone', 'address']
      .map(id => document.getElementById(id));
    const validationMessage = document.createElement('p');
    validationMessage.className = 'text-sm';
    validationMessage.setAttribute('role', 'status');
    confirmBooking.before(validationMessage);

    confirmBooking.addEventListener('click', () => {
      const fieldsToValidate = paymentReady ? [] : requiredFields;
      const invalidFields = fieldsToValidate.filter(field => !field.value.trim());
      fieldsToValidate.forEach(field => field.setAttribute('aria-invalid', String(!field.value.trim())));

      if (invalidFields.length) {
        validationMessage.textContent = 'Please complete all traveller details before continuing.';
        validationMessage.style.color = 'var(--color-pink)';
        invalidFields[0].focus();
        return;
      }

      if (!paymentReady) {
        paymentReady = true;
        paymentSection.style.display = 'block';
        validationMessage.textContent = 'Traveller details saved. Continue to secure payment.';
        validationMessage.style.color = 'var(--color-green-light)';
        checkoutSteps[0]?.classList.remove('active');
        checkoutSteps[1]?.classList.add('active');
        checkoutSteps[2]?.classList.add('active');
        refreshTotals();
        return;
      }

      validationMessage.textContent = 'Opening secure payment...';
      validationMessage.style.color = 'var(--color-green-light)';

      const formData = new FormData(checkoutForm);
      fetch(checkoutForm.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(response => response.json().then(data => ({ ok: response.ok, data })))
        .then(({ ok, data }) => {
          if (!ok) throw new Error(data.error || 'Unable to save booking.');
          window.location.href = data.checkout_url;
        })
        .catch(error => {
          validationMessage.textContent = error.message;
          validationMessage.style.color = 'var(--color-pink)';
        });
    });
  }

  if (btnAddCover && coverCostRow && totalPriceEl) {
    btnAddCover.addEventListener('click', () => {
      const isAdded = coverInput.value === '1';
      if (isAdded) {
        coverInput.value = '0';
        btnAddCover.textContent = 'Add to Booking';
        btnAddCover.classList.replace('btn--primary', 'btn--outline');
        coverCostRow.style.display = 'none';
        coverAdded = false;
        totalPriceEl.textContent = formatPKR(baseTotal);
      } else {
        coverInput.value = '1';
        btnAddCover.textContent = 'Remove Cover';
        btnAddCover.classList.replace('btn--outline', 'btn--primary');
        coverCostRow.style.display = 'flex';
        coverAdded = true;
        totalPriceEl.textContent = formatPKR(baseTotal + coverPrice);
      }
    });
  }
});
