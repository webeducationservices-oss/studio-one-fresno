/* Studio One Fresno — client-side cart module.
 * Persists to localStorage, updates cart icon badge, renders cart page.
 * PayPal Smart Payment Buttons integration slot lives in cart.html (commented)
 * and will be activated in Phase 4 when credentials arrive.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'studio_one_cart_v1';
  const TAX_RATE = 0.07975; // California sales tax — confirm w/ client

  function read() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
      return [];
    }
  }

  function write(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    updateBadge(items);
    document.dispatchEvent(new CustomEvent('cart:updated', { detail: items }));
  }

  function updateBadge(items) {
    const count = items.reduce((sum, i) => sum + i.qty, 0);
    const badge = document.getElementById('cartCount');
    if (badge) {
      badge.textContent = count;
      badge.classList.toggle('is-empty', count === 0);
    }
  }

  function add(item) {
    const items = read();
    const key = item.slug + (item.variant || '');
    const existing = items.find(i => (i.slug + (i.variant || '')) === key);
    if (existing) {
      existing.qty += item.qty;
    } else {
      items.push(item);
    }
    write(items);
  }

  function remove(slug, variant) {
    const items = read().filter(i => !(i.slug === slug && (i.variant || '') === (variant || '')));
    write(items);
  }

  function updateQty(slug, variant, qty) {
    const items = read();
    const item = items.find(i => i.slug === slug && (i.variant || '') === (variant || ''));
    if (!item) return;
    if (qty < 1) {
      return remove(slug, variant);
    }
    item.qty = qty;
    write(items);
  }

  function clear() {
    write([]);
  }

  function subtotalCents() {
    return read().reduce((sum, i) => sum + i.price_cents * i.qty, 0);
  }

  function taxCents() {
    return Math.round(subtotalCents() * TAX_RATE);
  }

  function totalCents() {
    return subtotalCents() + taxCents();
  }

  function fmt(cents) {
    return '$' + (cents / 100).toFixed(2);
  }

  // ------------------------------------------------------------------------
  // Cart page rendering (/cart)
  // ------------------------------------------------------------------------
  function renderCartPage() {
    const items = read();
    const empty = document.getElementById('cartEmpty');
    const content = document.getElementById('cartContent');
    const itemsEl = document.getElementById('cartItems');
    const itemCountEl = document.getElementById('cartItemCount');
    if (!itemsEl) return; // not on cart page

    if (items.length === 0) {
      empty.style.display = 'block';
      content.style.display = 'none';
      itemCountEl.textContent = '0 items';
      return;
    }
    empty.style.display = 'none';
    content.style.display = 'block';

    const totalQty = items.reduce((s, i) => s + i.qty, 0);
    itemCountEl.textContent = totalQty + (totalQty === 1 ? ' item' : ' items');

    itemsEl.innerHTML = items.map((i, idx) => `
      <div class="cart-item" data-slug="${escapeHtml(i.slug)}" data-variant="${escapeHtml(i.variant || '')}">
        <div class="cart-item-img"><img src="${escapeHtml(i.image)}" alt="${escapeHtml(i.name)}"></div>
        <div class="cart-item-info">
          <p class="brand">${escapeHtml(i.brand || '')}</p>
          <h3>${escapeHtml(i.name)}</h3>
          ${i.variant ? `<p class="variant">${escapeHtml(i.variant)}</p>` : ''}
        </div>
        <div class="cart-qty">
          <button class="qty-dec" aria-label="Decrease quantity">−</button>
          <input type="number" value="${i.qty}" min="1" max="99" data-idx="${idx}">
          <button class="qty-inc" aria-label="Increase quantity">+</button>
        </div>
        <div class="cart-item-price">${fmt(i.price_cents * i.qty)}</div>
        <button class="cart-remove" aria-label="Remove item">✕</button>
      </div>
    `).join('');

    // Wire up +/- and remove
    itemsEl.querySelectorAll('.cart-item').forEach(row => {
      const slug = row.dataset.slug;
      const variant = row.dataset.variant;
      row.querySelector('.qty-dec').addEventListener('click', () => {
        const cur = read().find(i => i.slug === slug && (i.variant || '') === variant);
        if (cur) updateQty(slug, variant, cur.qty - 1);
        renderCartPage();
      });
      row.querySelector('.qty-inc').addEventListener('click', () => {
        const cur = read().find(i => i.slug === slug && (i.variant || '') === variant);
        if (cur) updateQty(slug, variant, cur.qty + 1);
        renderCartPage();
      });
      row.querySelector('input').addEventListener('change', (e) => {
        const q = parseInt(e.target.value, 10) || 1;
        updateQty(slug, variant, q);
        renderCartPage();
      });
      row.querySelector('.cart-remove').addEventListener('click', () => {
        remove(slug, variant);
        renderCartPage();
      });
    });

    // Totals
    document.getElementById('sumSubtotal').textContent = fmt(subtotalCents());
    document.getElementById('sumTax').textContent = fmt(taxCents());
    document.getElementById('sumTotal').textContent = fmt(totalCents());
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // Initialize badge on any page
  updateBadge(read());

  // Public API
  window.Cart = {
    add, remove, updateQty, clear, read, write,
    subtotalCents, taxCents, totalCents, fmt,
    renderCartPage,
    TAX_RATE,
  };
})();
