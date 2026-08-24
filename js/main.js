/* Travel Huh? — Main Shared JavaScript*/

document.addEventListener('DOMContentLoaded', () => {
  
  // --- Mobile Menu Toggle ---
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenuBtn.classList.toggle('active');
      mobileMenu.classList.toggle('active');
    });
  }

  // --- Shortlist Persistence ---
  const shortlistStorageKey = 'travelHuhShortlist';
  const shortlistButtons = document.querySelectorAll('[data-shortlist-id]');
  const shortlistLinks = document.querySelectorAll('a[href="search-results.html"]');

  const getShortlist = () => {
    try {
      return JSON.parse(localStorage.getItem(shortlistStorageKey) || '[]');
    } catch {
      return [];
    }
  };

  const updateShortlistUI = () => {
    const shortlist = getShortlist();
    shortlistButtons.forEach(button => {
      const isSaved = shortlist.includes(button.dataset.shortlistId);
      button.classList.toggle('active', isSaved);
      button.setAttribute('aria-label', isSaved ? 'Remove from shortlist' : 'Add to shortlist');
      button.setAttribute('aria-pressed', String(isSaved));
    });
    shortlistLinks.forEach(link => {
      if (link.textContent.includes('Shortlist')) {
        link.textContent = `Shortlist (${shortlist.length})`;
      }
    });
  };

  shortlistButtons.forEach(button => {
    button.addEventListener('click', () => {
      const shortlist = getShortlist();
      const hotelId = button.dataset.shortlistId;
      const nextShortlist = shortlist.includes(hotelId)
        ? shortlist.filter(id => id !== hotelId)
        : [...shortlist, hotelId];

      localStorage.setItem(shortlistStorageKey, JSON.stringify(nextShortlist));
      updateShortlistUI();
    });
  });

  updateShortlistUI();

  // --- Navbar Scroll Effect ---
  const navbar = document.getElementById('navbar');
  
  if (navbar && navbar.classList.contains('navbar--transparent')) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('navbar--scrolled');
      } else {
        navbar.classList.remove('navbar--scrolled');
      }
    }, { passive: true });
  }

  // --- Scroll Reveal Animation ---
  const revealElements = document.querySelectorAll('.reveal');
  
  const revealOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
  };

  const revealOnScroll = new IntersectionObserver(function(entries, observer) {
    entries.forEach(entry => {
      if (!entry.isIntersecting) {
        return;
      } else {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, revealOptions);

  revealElements.forEach(el => {
    revealOnScroll.observe(el);
  });

  // --- Search Widget Tabs ---
  const tabHolidays = document.getElementById('tab-holidays');
  const tabHotels = document.getElementById('tab-hotels');
  const formHolidays = document.getElementById('form-holidays');
  const formHotels = document.getElementById('form-hotels');

  if (tabHolidays && tabHotels && formHolidays && formHotels) {
    tabHolidays.addEventListener('click', () => {
      tabHolidays.classList.add('active');
      tabHotels.classList.remove('active');
      formHolidays.style.display = 'block';
      formHotels.style.display = 'none';
    });

    tabHotels.addEventListener('click', () => {
      tabHotels.classList.add('active');
      tabHolidays.classList.remove('active');
      formHotels.style.display = 'block';
      formHolidays.style.display = 'none';
    });
  }

  // --- Search Form Navigation ---
  const holidayForm = formHolidays?.querySelector('form');
  const hotelForm = formHotels?.querySelector('form');

  const navigateToResults = (form, type) => {
    if (!form) return;

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const destination = type === 'hotel'
        ? formData.get('hotel-destination')
        : formData.get('destination');
      const params = new URLSearchParams({
        type,
        destination: String(destination || '').trim(),
      });

      window.location.href = `search-results.html?${params.toString()}`;
    });
  };

  navigateToResults(holidayForm, 'holiday');
  navigateToResults(hotelForm, 'hotel');

  // --- Deals Carousel ---
  const track = document.getElementById('deals-track');
  const prevBtn = document.getElementById('deals-prev');
  const nextBtn = document.getElementById('deals-next');

  if (track && prevBtn && nextBtn) {
    let currentIndex = 0;
    const cards = Array.from(track.children);
    
    const updateCarousel = () => {
      if (cards.length === 0) return;
      
      const cardWidth = cards[0].offsetWidth;
      const gap = parseFloat(window.getComputedStyle(track).gap) || 0;
      const itemWidth = cardWidth + gap;
      
      track.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
      
      prevBtn.disabled = currentIndex === 0;
      
      const wrapperWidth = track.parentElement.offsetWidth;
      const visibleItems = Math.max(1, Math.floor((wrapperWidth + gap) / itemWidth));
      
      const maxIndex = Math.max(0, cards.length - visibleItems);
      
      if (currentIndex > maxIndex) {
        currentIndex = maxIndex;
        track.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
      }
      
      nextBtn.disabled = currentIndex >= maxIndex;
    };
    
    nextBtn.addEventListener('click', () => {
      currentIndex++;
      updateCarousel();
    });
    
    prevBtn.addEventListener('click', () => {
      currentIndex--;
      updateCarousel();
    });
    
    setTimeout(updateCarousel, 100);
    window.addEventListener('resize', updateCarousel);
  }

});
