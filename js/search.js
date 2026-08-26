/* Search Results Interactions */
document.addEventListener('DOMContentLoaded', () => {
  const searchParams = new URLSearchParams(window.location.search);
  const destination = searchParams.get('destination');
  const resultsTitle = document.querySelector('.section-header h1');
  const resultsSubtitle = document.querySelector('.section-header p');
  const stickyDestination = document.querySelector('.sticky-bar__item:first-child span:last-child');
  const priceRange = document.getElementById('priceRange');
  const priceValue = document.getElementById('priceValue');
  const filters = document.querySelector('.search-filters');

  if (destination) {
    const formattedDestination = destination.replace(/\s+/g, ' ').trim();
    if (resultsTitle) resultsTitle.textContent = `Search Results for ${formattedDestination}`;
    if (resultsSubtitle) resultsSubtitle.textContent = `Showing the best "Huh?" moments for ${formattedDestination}.`;
    if (stickyDestination) stickyDestination.textContent = formattedDestination;
  }

  if (priceRange && priceValue) {
    priceRange.addEventListener('input', (event) => {
      priceValue.textContent = `Rs ${event.target.value}+`;
    });
  }

  const buildSearchUrl = () => {
    const params = new URLSearchParams(window.location.search);
    params.set('max_price', priceRange?.value || '100000');
    params.delete('stars');
    params.delete('facility');
    params.delete('board');
    document.querySelectorAll('input[name="stars"]:checked').forEach((input) => params.append('stars', input.value));
    document.querySelectorAll('input[name="facility"]:checked').forEach((input) => params.append('facility', input.value));
    const board = document.querySelector('input[name="board"]:checked')?.value || '';
    if (board) params.set('board', board);
    return `/search/?${params.toString()}`;
  };

  document.getElementById('update-search')?.addEventListener('click', () => {
    window.location.href = buildSearchUrl();
  });

  document.getElementById('refine-search')?.addEventListener('click', () => {
    filters?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  document.getElementById('clear-filters')?.addEventListener('click', () => {
    const params = new URLSearchParams(window.location.search);
    ['max_price', 'stars', 'facility', 'board'].forEach((key) => params.delete(key));
    params.set('max_price', '100000');
    window.location.href = `/search/?${params.toString()}`;
  });
});
