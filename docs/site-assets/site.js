(() => {
  'use strict';

  const toggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  const filter = document.querySelector('[data-feature-filter]');
  const cards = Array.from(document.querySelectorAll('[data-feature-card]'));
  const noResults = document.querySelector('[data-no-results]');
  if (filter && cards.length) {
    const apply = () => {
      const query = filter.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(card => {
        const match = !query || card.textContent.toLowerCase().includes(query) || (card.dataset.tags || '').includes(query);
        card.hidden = !match;
        if (match) visible += 1;
      });
      if (noResults) noResults.style.display = visible ? 'none' : 'block';
    };
    filter.addEventListener('input', apply);
  }

  document.querySelectorAll('[data-copy]').forEach(button => {
    button.addEventListener('click', async () => {
      const value = button.getAttribute('data-copy') || '';
      try {
        await navigator.clipboard.writeText(value);
        const original = button.textContent;
        button.textContent = 'Copied';
        setTimeout(() => { button.textContent = original; }, 1200);
      } catch {
        window.prompt('Copy this value:', value);
      }
    });
  });

  document.querySelectorAll('[data-iso-date]').forEach(node => {
    const value = node.getAttribute('data-iso-date');
    if (!value) return;
    const date = new Date(value);
    if (!Number.isNaN(date.valueOf())) {
      node.title = value;
      node.textContent = new Intl.DateTimeFormat(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      }).format(date);
    }
  });
})();
