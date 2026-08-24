/* Checkout Interactions*/

document.addEventListener('DOMContentLoaded', () => {
  const btnAddCover = document.getElementById('btn-add-cover');
  const coverCostRow = document.getElementById('cover-cost-row');
  const totalPriceEl = document.getElementById('total-price');
  const checkoutHotelName = document.getElementById('checkout-hotel-name');
  const confirmBooking = document.getElementById('confirm-booking');
  const checkoutSteps = document.querySelectorAll('.checkout-stepper .step');
  const paymentSection = document.getElementById('payment-section');
  const checkoutForm = document.getElementById('checkout-form');
  const booking = JSON.parse(localStorage.getItem('travelHuhBooking') || 'null');
  
  let basePrice = booking?.total || 1188.00;
  let coverPrice = 45.00;
  let coverAdded = false;

  if (booking && checkoutHotelName) {
    checkoutHotelName.textContent = `${booking.roomName} - ${booking.board}`;
    totalPriceEl.textContent = `£${basePrice.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  }
  if (booking) {
    document.getElementById('checkout-room-id').value = booking.roomId || '';
    document.getElementById('checkout-total-price').value = basePrice.toFixed(2);
  }

  if (confirmBooking) {
    const requiredFields = ['firstName', 'lastName', 'dob', 'gender', 'email', 'phone', 'address']
      .map(id => document.getElementById(id));
    const validationMessage = document.createElement('p');
    validationMessage.className = 'text-sm';
    validationMessage.setAttribute('role', 'status');
    confirmBooking.before(validationMessage);
    let paymentReady = false;

    confirmBooking.addEventListener('click', () => {
      const fieldsToValidate = paymentReady ? [] : requiredFields;
      const invalidFields = fieldsToValidate.filter(field => !field.value.trim());
      fieldsToValidate.forEach(field => field.setAttribute('aria-invalid', String(!field.value.trim())));

      if (invalidFields.length) {
        validationMessage.textContent = paymentReady
          ? 'Please complete all payment details before confirming your booking.'
          : 'Please complete all traveller details before continuing.';
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
        confirmBooking.textContent = `Pay £${basePrice.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        return;
      }

      validationMessage.textContent = 'Booking confirmed. Your travel details have been saved.';
      validationMessage.style.color = 'var(--color-green-light)';
      const formData = new FormData(checkoutForm);
      fetch(checkoutForm.action, { method: 'POST', body: formData, headers: { 'X-Requested-With': 'XMLHttpRequest' } })
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
      coverAdded = !coverAdded;
      
      if (coverAdded) {
        btnAddCover.textContent = 'Remove Cover';
        btnAddCover.classList.replace('btn--outline', 'btn--ghost');
        coverCostRow.style.display = 'flex';
        
        // Update total
        const newTotal = basePrice + coverPrice;
        totalPriceEl.textContent = `£${newTotal.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      } else {
        btnAddCover.textContent = 'Add to Booking';
        btnAddCover.classList.replace('btn--ghost', 'btn--outline');
        coverCostRow.style.display = 'none';
        
        // Update total
        totalPriceEl.textContent = `£${basePrice.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      }
    });
  }
});
