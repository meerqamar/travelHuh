/* Search Results Interactions */
document.addEventListener('DOMContentLoaded', () => {
  const searchParams = new URLSearchParams(window.location.search);
  const destination = searchParams.get('destination');
  const resultsTitle = document.querySelector('.section-header h1');
  const resultsSubtitle = document.querySelector('.section-header p');
  const stickyDestination = document.querySelector('.sticky-bar__item:first-child span:last-child');
  const resultCards = Array.from(document.querySelectorAll('.result-card'));
  const resultsList = document.querySelector('.search-results');

  if (destination) {
    const formattedDestination = destination.replace(/\s+/g, ' ').trim();
    if (resultsTitle) resultsTitle.textContent = `Search Results for ${formattedDestination}`;
    if (resultsSubtitle) resultsSubtitle.textContent = `Showing the best "Huh?" moments for ${formattedDestination}.`;
    if (stickyDestination) stickyDestination.textContent = formattedDestination;
  }

  const noResults = document.createElement('p');
  noResults.className = 'text-muted';
  noResults.textContent = 'No holidays match these filters. Try widening your search.';
  noResults.hidden = true;
  resultsList?.appendChild(noResults);

  const filterSections = Array.from(document.querySelectorAll('.filter-section'));
  const priceRange = document.getElementById('priceRange');
  const priceValue = document.getElementById('priceValue');

  const getFilterSection = (title) => filterSections.find(section =>
    section.querySelector('.filter-title')?.textContent.trim() === title
  );

  const applyFilters = () => {
    const selectedStars = Array.from(getFilterSection('Star Rating')?.querySelectorAll('input:checked') || [])
      .map(input => Number(input.closest('label')?.textContent.match(/(\d) Stars/)?.[1]));
    const selectedBoard = getFilterSection('Board Basis')?.querySelector('input:checked')?.closest('label')?.textContent.trim();
    const selectedFacilities = Array.from(getFilterSection('Facilities')?.querySelectorAll('input:checked') || [])
      .map(input => input.closest('label')?.textContent.trim().toLowerCase());
    const maxPrice = Number(priceRange?.value || Number.MAX_SAFE_INTEGER);

    let visibleCount = 0;
    resultCards.forEach(card => {
      const price = Number(card.querySelector('.result-card__price')?.textContent.replace(/[^\d]/g, '') || 0);
      const score = Number(card.querySelector('.rating-badge__score')?.textContent || 0);
      const cardText = card.textContent.toLowerCase();
      const matches = price <= maxPrice
        && (!selectedStars.length || selectedStars.some(star => Math.floor(score) === star))
        && (!selectedBoard || cardText.includes(selectedBoard.toLowerCase()))
        && selectedFacilities.every(facility => facility === 'free wifi'
          ? cardText.includes('wifi')
          : cardText.includes(facility));

      card.hidden = !matches;
      if (matches) visibleCount++;
    });

    noResults.hidden = visibleCount > 0;
  };

  // Price Range Slider
  if (priceRange && priceValue) {
    priceRange.addEventListener('input', (e) => {
      priceValue.textContent = `£${e.target.value}+`;
      applyFilters();
    });
  }

  document.querySelectorAll('.search-filters input[type="checkbox"], .search-filters input[type="radio"]')
    .forEach(input => input.addEventListener('change', applyFilters));

  // Clear Filters
  const clearFiltersBtn = document.getElementById('clear-filters');
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', () => {
      const inputs = document.querySelectorAll('.search-filters input');
      inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
          input.checked = false;
        } else if (input.type === 'range') {
          input.value = input.max;
          if (priceValue) priceValue.textContent = `£${input.max}+`;
        }
      });
      applyFilters();
    });
  }

  applyFilters();
});
