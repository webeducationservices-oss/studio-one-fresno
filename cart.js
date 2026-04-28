/* Studio One Fresno — client-side cart module.
 * Persists to localStorage, updates cart icon badge, renders cart page.
 * Tax + shipping logic exposed for PayPal Smart Payment Buttons in cart.html.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'studio_one_cart_v1';
  const STATE_KEY   = 'studio_one_cart_state_v1';

  // Fresno + CA Sales Tax = 8.35%
  const CA_TAX_RATE = 0.0835;

  // Shipping config (mirrors .env.keys.cat / Vercel env vars)
  const SHIPPING_FLAT_USD     = 8.00;
  const SHIPPING_FREE_OVER    = 75.00;

  function read() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch { return []; }
  }

  function write(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    updateBadge(items);
    document.dispatchEvent(new CustomEvent('cart:updated', { detail: items }));
  }

  // Cart-page state (pickup vs ship, ship-to state) — persists across reloads
  function readState() {
    try { return JSON.parse(localStorage.getItem(STATE_KEY) || '{}'); }
    catch { return {}; }
  }
  function writeState(s) {
    localStorage.setItem(STATE_KEY, JSON.stringify(s));
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
    if (existing) existing.qty += item.qty;
    else items.push(item);
    write(items);
  }

  function remove(slug, variant) {
    write(read().filter(i => !(i.slug === slug && (i.variant || '') === (variant || ''))));
  }

  function updateQty(slug, variant, qty) {
    const items = read();
    const item = items.find(i => i.slug === slug && (i.variant || '') === (variant || ''));
    if (!item) return;
    if (qty < 1) return remove(slug, variant);
    item.qty = qty;
    write(items);
  }

  function clear() { write([]); }

  // ---- Money math (all in cents, formatted to dollars at display time) ----
  function subtotalCents() {
    return read().reduce((sum, i) => sum + i.price_cents * i.qty, 0);
  }

  /** Tax cents — only charged for in-store pickup OR shipping to CA. */
  function taxCents(state = readState()) {
    const sub = subtotalCents();
    const isPickup = state.method === 'pickup';
    const isCA = (state.shipState || '').toUpperCase() === 'CA';
    if (state.wholesale) return 0;          // future: wholesale exempt
    if (isPickup || (state.method === 'ship' && isCA)) {
      return Math.round(sub * CA_TAX_RATE);
    }
    return 0;
  }

  /** Shipping cents — free for pickup, free over $75 ship, else flat $8. */
  function shippingCents(state = readState()) {
    if (state.method === 'pickup') return 0;
    const sub = subtotalCents();
    if (sub >= SHIPPING_FREE_OVER * 100) return 0;
    return Math.round(SHIPPING_FLAT_USD * 100);
  }

  function totalCents(state = readState()) {
    return subtotalCents() + taxCents(state) + shippingCents(state);
  }

  function fmt(cents) { return '$' + (cents / 100).toFixed(2); }

  // ------------------------------------------------------------------------
  function renderCartPage() {
    const items = read();
    const empty = document.getElementById('cartEmpty');
    const content = document.getElementById('cartContent');
    const itemsEl = document.getElementById('cartItems');
    const itemCountEl = document.getElementById('cartItemCount');
    if (!itemsEl) return;

    if (items.length === 0) {
      if (empty) empty.style.display = 'block';
      if (content) content.style.display = 'none';
      if (itemCountEl) itemCountEl.textContent = '0 items';
      document.dispatchEvent(new CustomEvent('cart:rendered', { detail: { empty: true } }));
      return;
    }
    if (empty) empty.style.display = 'none';
    if (content) content.style.display = 'block';

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

    itemsEl.querySelectorAll('.cart-item').forEach(row => {
      const slug = row.dataset.slug, variant = row.dataset.variant;
      row.querySelector('.qty-dec').addEventListener('click', () => {
        const cur = read().find(i => i.slug === slug && (i.variant || '') === variant);
        if (cur) updateQty(slug, variant, cur.qty - 1);
        renderCartPage();
        recomputeSummary();
      });
      row.querySelector('.qty-inc').addEventListener('click', () => {
        const cur = read().find(i => i.slug === slug && (i.variant || '') === variant);
        if (cur) updateQty(slug, variant, cur.qty + 1);
        renderCartPage();
        recomputeSummary();
      });
      row.querySelector('input').addEventListener('change', (e) => {
        updateQty(slug, variant, parseInt(e.target.value, 10) || 1);
        renderCartPage();
        recomputeSummary();
      });
      row.querySelector('.cart-remove').addEventListener('click', () => {
        remove(slug, variant);
        renderCartPage();
        recomputeSummary();
      });
    });

    recomputeSummary();
    document.dispatchEvent(new CustomEvent('cart:rendered', { detail: { empty: false } }));
  }

  function recomputeSummary() {
    const state = readState();
    const sub = subtotalCents();
    const ship = shippingCents(state);
    const tax = taxCents(state);
    const tot = sub + ship + tax;
    setText('sumSubtotal', fmt(sub));
    setText('sumShipping', state.method === 'pickup' ? 'Free (in-store pickup)' : (ship === 0 ? 'Free' : fmt(ship)));
    setText('sumTax', taxLabel(state) + ' ' + fmt(tax));
    setText('sumTotal', fmt(tot));
    document.dispatchEvent(new CustomEvent('cart:summary-updated', { detail: { sub, ship, tax, tot, state } }));
  }

  function taxLabel(state) {
    if (state.wholesale) return 'Tax (wholesale exempt)';
    if (state.method === 'pickup') return 'Tax (CA 8.35%)';
    if (state.method === 'ship' && (state.shipState || '').toUpperCase() === 'CA') return 'Tax (CA 8.35%)';
    if (state.method === 'ship') return 'Tax (out-of-state, exempt)';
    return 'Tax';
  }

  function setText(id, txt) {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  updateBadge(read());

  window.Cart = {
    add, remove, updateQty, clear, read, write,
    subtotalCents, taxCents, shippingCents, totalCents, fmt,
    renderCartPage, recomputeSummary,
    readState, writeState,
    CA_TAX_RATE, SHIPPING_FLAT_USD, SHIPPING_FREE_OVER,
  };
})();
