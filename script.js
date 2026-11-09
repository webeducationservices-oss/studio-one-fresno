/* ===== Smooth Scroll (DISABLED) =====
 * Removed the Lenis-style wheel-event hijacker because preventDefault() on
 * wheel events breaks third-party iframes (PayPal credit-card form, JotForm
 * embeds, YouTube embeds, etc.). Native browser smooth scroll is good
 * enough on modern hardware and doesn't fight with iframes.
 *
 * Use CSS `scroll-behavior: smooth` on <html> for in-page anchor jumps.
 */

/* ===== Scroll-triggered Animations ===== */
(function () {
  const animatedEls = document.querySelectorAll('[data-animate]');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => {
          entry.target.classList.add('is-visible');
        }, delay * 150);
        observer.unobserve(entry.target);
      }
    });
  }, {
    // threshold:0 so elements taller than the viewport (e.g. a long blog
    // article body) still reveal — a ratio-based threshold can never be met
    // when the element is several screens tall, leaving it stuck at opacity:0.
    threshold: 0,
    rootMargin: '0px 0px -50px 0px'
  });

  animatedEls.forEach(el => observer.observe(el));
})();

/* ===== Header Scroll Effect ===== */
(function () {
  const header = document.querySelector('.header');
  let ticking = false;

  function updateHeader() {
    if (window.scrollY > 80) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateHeader);
      ticking = true;
    }
  });
})();

/* ===== Mobile Navigation ===== */
(function () {
  const toggle = document.getElementById('menuToggle');
  const overlay = document.getElementById('navOverlay');
  const close = document.getElementById('navClose');
  if (!toggle || !overlay) return;

  toggle.addEventListener('click', () => {
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  });

  close.addEventListener('click', () => {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  });

  overlay.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      overlay.classList.remove('is-open');
      document.body.style.overflow = '';
    });
  });
})();

/* ===== Testimonial Slider ===== */
(function () {
  const track = document.getElementById('testimonialTrack');
  if (!track) return; // page has no homepage slider (e.g. /testimonials)
  const slides = track.querySelectorAll('.testimonial-slide');
  const prevBtn = document.getElementById('sliderPrev');
  const nextBtn = document.getElementById('sliderNext');
  let current = 0;
  const total = slides.length;
  let autoplayInterval;

  function goTo(index) {
    current = ((index % total) + total) % total;
    track.style.transform = `translateX(-${current * 100}%)`;
  }

  prevBtn.addEventListener('click', () => {
    goTo(current - 1);
    resetAutoplay();
  });

  nextBtn.addEventListener('click', () => {
    goTo(current + 1);
    resetAutoplay();
  });

  // Touch/swipe support
  let startX = 0;
  let isDragging = false;

  track.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
    isDragging = true;
  });

  track.addEventListener('touchmove', (e) => {
    if (!isDragging) return;
  });

  track.addEventListener('touchend', (e) => {
    if (!isDragging) return;
    isDragging = false;
    const diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) {
      if (diff > 0) goTo(current + 1);
      else goTo(current - 1);
      resetAutoplay();
    }
  });

  // Autoplay
  function startAutoplay() {
    autoplayInterval = setInterval(() => goTo(current + 1), 5000);
  }
  function resetAutoplay() {
    clearInterval(autoplayInterval);
    startAutoplay();
  }
  startAutoplay();
})();

/* ===== Gallery Filter ===== */
(function () {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const items = document.querySelectorAll('.gallery-item');
  const empty = document.getElementById('homeGalleryEmpty');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      let visible = 0;

      items.forEach(item => {
        const match = filter === 'all' || item.dataset.category === filter;
        if (match) {
          item.classList.remove('hidden');
          item.style.display = '';
          visible++;
        } else {
          item.classList.add('hidden');
          item.style.display = 'none';
        }
      });

      if (empty) {
        empty.hidden = visible !== 0;
        empty.classList.toggle('is-shown', visible === 0);
      }
    });
  });
})();

/* ===== Gallery Modal ===== */
(function () {
  const modal = document.getElementById('galleryModal');
  const modalImg = document.getElementById('modalImage');
  if (!modal || !modalImg) return; // page has no gallery modal (e.g. /testimonials)
  const closeBtn = modal.querySelector('.modal-close');
  const expandBtns = document.querySelectorAll('.gallery-expand');
  const galleryItems = document.querySelectorAll('.gallery-item');

  galleryItems.forEach(item => {
    item.addEventListener('click', () => {
      const img = item.querySelector('.gallery-pair img');
      if (img) {
        modalImg.src = img.src;
        modal.classList.add('is-open');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  function closeModal() {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  }
})();

/* ===== Phone Widget Toggle ===== */
(function () {
  const toggle = document.getElementById('phoneToggle');
  const actions = document.getElementById('phoneActions');
  const widget = document.getElementById('phoneWidget');
  if (!toggle || !widget) return;
  const phoneIcon = toggle.querySelector('.phone-icon');
  const closeIcon = toggle.querySelector('.close-icon');
  let isOpen = false;

  toggle.addEventListener('click', () => {
    isOpen = !isOpen;
    actions.classList.toggle('is-open', isOpen);
    phoneIcon.style.display = isOpen ? 'none' : 'block';
    closeIcon.style.display = isOpen ? 'block' : 'none';
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (isOpen && !widget.contains(e.target)) {
      isOpen = false;
      actions.classList.remove('is-open');
      phoneIcon.style.display = 'block';
      closeIcon.style.display = 'none';
    }
  });
})();

/* ===== Parallax on Hero & CTA backgrounds ===== */
(function () {
  const heroBg = document.querySelector('.hero-bg-image');
  const ctaBg = document.querySelector('.cta-bg-image');

  function updateParallax() {
    const scrollTop = window.scrollY;

    if (heroBg) {
      const heroRect = heroBg.parentElement.getBoundingClientRect();
      if (heroRect.bottom > 0) {
        heroBg.style.transform = `translateY(${scrollTop * 0.2}px)`;
      }
    }

    if (ctaBg) {
      const ctaRect = ctaBg.parentElement.getBoundingClientRect();
      if (ctaRect.top < window.innerHeight && ctaRect.bottom > 0) {
        const offset = (ctaRect.top - window.innerHeight) * 0.15;
        ctaBg.style.transform = `translateY(${offset}px)`;
      }
    }

    requestAnimationFrame(updateParallax);
  }

  updateParallax();
})();


/* ===== Source attribution + Google Ads lead tracking (WES) =====
 * Captures click IDs (gclid/gbraid/wbraid/fbclid/msclkid) + UTMs on first
 * touch, caches first-touch in sessionStorage, and exposes:
 *   window.soAttribution()            -> object to spread into form payloads
 *                                        (lands in the lead's raw_data so the
 *                                        admin portal can attribute leads to ads)
 *   window.soTrackLead(evt, formType) -> dataLayer push that fires the
 *                                        form-specific Google Ads conversion
 *                                        tag in GTM (container GTM-WQGCMZ9Q).
 */
(function () {
  var CACHE = 'so_first_touch';
  var UTM   = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content'];
  var CLICK = ['gclid','gbraid','wbraid','fbclid','msclkid'];

  function classify(p, ref) {
    var s = (p.utm_source || '').toLowerCase(), m = (p.utm_medium || '').toLowerCase();
    if (p.gclid || p.gbraid || p.wbraid) return (m.indexOf('display') !== -1) ? 'OTHER_CAMPAIGNS' : 'PAID_SEARCH';
    if (p.msclkid) return 'PAID_SEARCH';
    if (p.fbclid)  return 'PAID_SOCIAL';
    if (m === 'cpc' || m === 'ppc' || m === 'paidsearch' || m === 'paid_search') return 'PAID_SEARCH';
    if (m === 'paid-social' || m === 'paid_social' || m === 'paidsocial') return 'PAID_SOCIAL';
    if (m === 'email' || s === 'email' || s === 'newsletter') return 'EMAIL_MARKETING';
    if (m === 'social' || ['facebook','instagram','twitter','linkedin','tiktok','youtube','pinterest','x'].indexOf(s) !== -1) return 'SOCIAL_MEDIA';
    if (m === 'organic' || ['google','bing','yahoo','duckduckgo'].indexOf(s) !== -1) return 'ORGANIC_SEARCH';
    if (m === 'referral') return 'REFERRALS';
    if (p.utm_campaign || p.utm_source || p.utm_medium) return 'OTHER_CAMPAIGNS';
    if (ref) {
      var h = ''; try { h = new URL(ref).hostname.toLowerCase(); } catch (e) {}
      if (!h || h.indexOf(location.hostname) !== -1) return 'DIRECT_TRAFFIC';
      if (/google\.|bing\.|yahoo\.|duckduckgo\./.test(h)) return 'ORGANIC_SEARCH';
      if (/facebook\.|instagram\.|twitter\.|t\.co|linkedin\.|tiktok\.|youtube\.|pinterest\./.test(h)) return 'SOCIAL_MEDIA';
      return 'REFERRALS';
    }
    return 'DIRECT_TRAFFIC';
  }

  function compute() {
    var qs = null; try { qs = new URLSearchParams(location.search); } catch (e) {}
    var url = {}, found = false;
    if (qs) UTM.concat(CLICK).forEach(function (k) { var v = qs.get(k); if (v) { url[k] = v; found = true; } });
    var cached = null; try { cached = JSON.parse(sessionStorage.getItem(CACHE) || 'null'); } catch (e) {}
    var ref = document.referrer || '';
    if (found) {
      var a = {
        utm_source: url.utm_source || '', utm_medium: url.utm_medium || '', utm_campaign: url.utm_campaign || '',
        utm_term: url.utm_term || '', utm_content: url.utm_content || '',
        gclid: url.gclid || '', gbraid: url.gbraid || '', wbraid: url.wbraid || '',
        fbclid: url.fbclid || '', msclkid: url.msclkid || '',
        analytics_source: classify(url, ref),
        analytics_source_data_1: (url.utm_source || '').toLowerCase() || (url.gclid ? 'google' : (url.fbclid ? 'facebook' : (url.msclkid ? 'bing' : ''))),
        analytics_source_data_2: url.utm_campaign || url.utm_term || url.gclid || url.fbclid || url.msclkid || '',
        first_referrer: (cached && cached.first_referrer) || ref,
        first_url: (cached && cached.first_url) || location.href
      };
      try { sessionStorage.setItem(CACHE, JSON.stringify(a)); } catch (e) {}
      return a;
    }
    if (cached) return cached;
    var a0 = {
      utm_source: '', utm_medium: '', utm_campaign: '', utm_term: '', utm_content: '',
      gclid: '', gbraid: '', wbraid: '', fbclid: '', msclkid: '',
      analytics_source: classify({}, ref), analytics_source_data_1: '', analytics_source_data_2: '',
      first_referrer: ref, first_url: location.href
    };
    try { sessionStorage.setItem(CACHE, JSON.stringify(a0)); } catch (e) {}
    return a0;
  }

  var current = compute();
  window.soAttribution = function () { return Object.assign({}, current); };
  window.soTrackLead = function (eventName, formType) {
    window.dataLayer = window.dataLayer || [];
    var push = { event: eventName, form_type: formType || '' };
    // Hashed email/phone the visitor typed on this page (see below). The Google
    // Ads form tags send it as user-provided data so a later Vagaro booking,
    // uploaded with the same hashed phone/email, can be paired with the ad click.
    if (window.__soUserData) push.user_data = window.__soUserData;
    window.dataLayer.push(push);
  };
})();

/* ===== Hashed user-provided data for Google Ads enhanced conversions (WES) =====
 * Watches email and phone fields on any form and keeps SHA-256 hashes of the
 * normalized values in window.__soUserData, ready before the form's own submit
 * finishes. Raw values never go to Google; only the hex hashes do.
 */
(function () {
  function hex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  }
  function sha256(s) {
    if (!window.crypto || !crypto.subtle || !window.TextEncoder) return Promise.resolve('');
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)).then(hex).catch(function () { return ''; });
  }
  function normEmail(v) {
    v = String(v || '').trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return '';
    var at = v.split('@');
    if (at[1] === 'gmail.com' || at[1] === 'googlemail.com') at[0] = at[0].replace(/\./g, '');
    return at[0] + '@' + at[1];
  }
  function normPhone(v) {
    var d = String(v || '').replace(/\D/g, '');
    if (d.length === 11 && d[0] === '1') d = d.slice(1);
    return d.length === 10 ? '+1' + d : '';
  }
  window.soHashPhone = function (v) { var p = normPhone(v); return p ? sha256(p) : Promise.resolve(''); };
  function isEmail(el) { return el.type === 'email' || /e-?mail/i.test(el.name || el.id || ''); }
  function isPhone(el) { return el.type === 'tel' || /phone|mobile|cell/i.test(el.name || el.id || ''); }
  function capture(el) {
    if (!el || el.tagName !== 'INPUT') return;
    if (isEmail(el)) {
      var e = normEmail(el.value); if (!e) return;
      sha256(e).then(function (h) { if (h) { window.__soUserData = window.__soUserData || {}; window.__soUserData.sha256_email_address = h; } });
    } else if (isPhone(el)) {
      var p = normPhone(el.value); if (!p) return;
      sha256(p).then(function (h) { if (h) { window.__soUserData = window.__soUserData || {}; window.__soUserData.sha256_phone_number = h; } });
    }
  }
  ['change', 'focusout'].forEach(function (t) {
    document.addEventListener(t, function (ev) { try { capture(ev.target); } catch (e) {} }, true);
  });
  document.addEventListener('submit', function (ev) {
    try { Array.prototype.forEach.call(ev.target.querySelectorAll('input'), capture); } catch (e) {}
  }, true);
})();

/* ===== New-or-returning step before Vagaro (WES, 2026-11-09) =====
 * Every link to vagaro.com opens a short question first. Returning guests go
 * straight on. New guests give a first name and phone, which we save as a lead
 * (/api/booking-intent) and send to Google Ads as a hashed phone, so the Vagaro
 * booking can be matched back to the visit. It must never stop anyone booking:
 * any error, and the link simply proceeds as normal.
 */
(function () {
  var DONE_KEY = 'so_booking_gate_done';
  var overlay = null, pendingLink = null;

  function done() { try { return sessionStorage.getItem(DONE_KEY) === '1'; } catch (e) { return false; } }
  function markDone() { try { sessionStorage.setItem(DONE_KEY, '1'); } catch (e) {} }

  function go(href, newTab) {
    var w = null;
    if (newTab) {
      try { w = window.open(href, '_blank'); } catch (e) { w = null; }
      if (w) { try { w.opener = null; } catch (e) {} return w; }
    }
    // Same-tab link, or the new tab was blocked: go in this tab.
    location.href = href;
    return null;
  }

  function track(guestType, userData) {
    window.dataLayer = window.dataLayer || [];
    var p = { event: 'so_booking_intent', guest_type: guestType };
    if (userData) p.user_data = userData;
    window.dataLayer.push(p);
  }

  function css() {
    if (document.getElementById('so-gate-css')) return;
    var s = document.createElement('style'); s.id = 'so-gate-css';
    s.textContent = [
      '.so-gate{position:fixed;inset:0;z-index:100000;display:flex;align-items:center;justify-content:center;padding:max(16px,env(safe-area-inset-top)) 16px;background:rgba(10,10,10,.72)}',
      '.so-gate__box{background:#0a0a0a;color:#f5f5f5;border:1px solid #4c5223;width:100%;max-width:420px;padding:28px 24px 22px;position:relative;font-family:var(--body-font,Arial,sans-serif);box-shadow:0 20px 60px rgba(0,0,0,.5)}',
      '.so-gate__x{position:absolute;top:8px;right:10px;background:none;border:0;color:#d9d9d9;font-size:26px;line-height:1;cursor:pointer;padding:6px}',
      '.so-gate h2{font-family:var(--heading-font,Georgia,serif);font-weight:400;font-size:26px;line-height:1.2;margin:0 0 8px;color:#fff}',
      '.so-gate p{margin:0 0 18px;font-size:15px;line-height:1.5;color:#d9d9d9}',
      '.so-gate__row{display:grid;gap:10px}',
      '.so-gate__btn{display:block;width:100%;padding:14px 16px;font-size:15px;letter-spacing:.06em;text-transform:uppercase;border:1px solid #727a35;background:#4c5223;color:#fff;cursor:pointer;font-family:inherit}',
      '.so-gate__btn--ghost{background:transparent;color:#f5f5f5;border-color:#555}',
      '.so-gate__btn:focus-visible,.so-gate input:focus-visible,.so-gate__skip:focus-visible{outline:2px solid #b9c26f;outline-offset:2px}',
      '.so-gate label{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#a3a493;margin:0 0 6px}',
      '.so-gate input[type=text],.so-gate input[type=tel]{display:block;width:100%;box-sizing:border-box;padding:12px;font-size:16px;background:#16170f;color:#fff;border:1px solid #444;margin:0 0 14px;font-family:inherit}',
      '.so-gate__consent{font-size:12.5px;color:#a3a493;margin:-4px 0 16px}',
      '.so-gate__err{color:#ef7a5f;font-size:13px;margin:-6px 0 12px;min-height:1em}',
      '.so-gate__skip{display:inline-block;margin-top:14px;font-size:13px;color:#a3a493;background:none;border:0;padding:0;text-decoration:underline;cursor:pointer;font-family:inherit}',
      '.so-gate__hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}'
    ].join('');
    document.head.appendChild(s);
  }

  function close() {
    if (overlay) { overlay.remove(); overlay = null; }
    document.removeEventListener('keydown', onKey, true);
    if (pendingLink && pendingLink.el && pendingLink.el.focus) { try { pendingLink.el.focus(); } catch (e) {} }
  }
  function onKey(e) { if (e.key === 'Escape') close(); }

  function screenAsk() {
    return '<h2 id="so-gate-title">Have you been to Studio One before?</h2>' +
      '<p>One quick question before we open booking.</p>' +
      '<div class="so-gate__row">' +
      '<button type="button" class="so-gate__btn" data-gate="new">I\'m a new guest</button>' +
      '<button type="button" class="so-gate__btn so-gate__btn--ghost" data-gate="returning">I\'ve been here before</button>' +
      '</div>';
  }
  function screenNew() {
    return '<h2 id="so-gate-title">Welcome! Who\'s booking?</h2>' +
      '<p>So we can look out for your booking, and help if anything goes wrong.</p>' +
      '<form id="so-gate-form" novalidate>' +
      '<label for="so-gate-name">First name</label><input id="so-gate-name" type="text" name="so_gate_name" autocomplete="given-name" maxlength="60" required>' +
      '<label for="so-gate-phone">Mobile phone</label><input id="so-gate-phone" type="tel" name="so_gate_phone" autocomplete="tel" inputmode="tel" required>' +
      '<div class="so-gate__hp" aria-hidden="true"><label for="so-gate-company">Company</label><input id="so-gate-company" type="text" name="company" tabindex="-1" autocomplete="off"></div>' +
      '<p class="so-gate__consent">We\'ll only text you about your booking.</p>' +
      '<div class="so-gate__err" id="so-gate-err" role="alert"></div>' +
      '<button type="submit" class="so-gate__btn">Continue to booking</button>' +
      '</form>' +
      '<button type="button" class="so-gate__skip" data-gate="skip">Skip, take me to booking</button>';
  }

  function render(html) {
    overlay.querySelector('.so-gate__body').innerHTML = html;
    var f = overlay.querySelector('button[data-gate],input');
    if (f) f.focus();
  }

  function proceed(guestType, userData) {
    var l = pendingLink; markDone();
    track(guestType, userData);
    close();
    if (l) go(l.href, l.newTab);
  }

  function submitNew(form) {
    var name = form.querySelector('#so-gate-name').value.trim();
    var phone = form.querySelector('#so-gate-phone').value;
    var digits = phone.replace(/\D/g, ''); if (digits.length === 11 && digits[0] === '1') digits = digits.slice(1);
    var err = form.querySelector('#so-gate-err');
    if (!name) { err.textContent = 'Please add your first name.'; return; }
    if (digits.length !== 10) { err.textContent = 'Please enter a 10-digit phone number.'; return; }
    var l = pendingLink; markDone(); close();
    // Open Vagaro first, inside the click, so pop-up blockers allow it.
    if (l) go(l.href, l.newTab);
    var attribution = {}; try { attribution = window.soAttribution ? window.soAttribution() : {}; } catch (e) {}
    try {
      fetch('/api/booking-intent', {
        method: 'POST', keepalive: true, headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ first_name: name, phone: digits, company: form.querySelector('#so-gate-company').value,
          page: location.pathname, vagaro_url: l ? l.href : '', attribution: attribution })
      }).catch(function () {});
    } catch (e) {}
    var hp = window.soHashPhone ? window.soHashPhone(digits) : Promise.resolve('');
    hp.then(function (h) {
      var ud = h ? { sha256_phone_number: h } : null;
      if (ud) { window.__soUserData = window.__soUserData || {}; window.__soUserData.sha256_phone_number = h; }
      track('new', ud);
      // Fires the Google Ads "New Guest Booking Intent" tag (GTM v12), which
      // sends the hashed phone as user-provided data.
      window.dataLayer.push(ud ? { event: 'so_new_guest', user_data: ud } : { event: 'so_new_guest' });
    }).catch(function () { track('new', null); });
  }

  function open(link) {
    css();
    pendingLink = link;
    overlay = document.createElement('div');
    overlay.className = 'so-gate';
    overlay.innerHTML = '<div class="so-gate__box" role="dialog" aria-modal="true" aria-labelledby="so-gate-title">' +
      '<button type="button" class="so-gate__x" aria-label="Close">&times;</button><div class="so-gate__body"></div></div>';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay || e.target.closest('.so-gate__x')) { close(); return; }
      var b = e.target.closest('[data-gate]'); if (!b) return;
      var g = b.getAttribute('data-gate');
      if (g === 'new') render(screenNew());
      else if (g === 'returning') proceed('returning', null);
      else if (g === 'skip') proceed('new_skipped', null);
    });
    overlay.addEventListener('submit', function (e) {
      e.preventDefault();
      try { submitNew(e.target); } catch (x) { var l = pendingLink; close(); if (l) go(l.href, l.newTab); }
    });
    document.addEventListener('keydown', onKey, true);
    render(screenAsk());
  }

  document.addEventListener('click', function (e) {
    try {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a || !/(^|\.)vagaro\.com$/i.test(a.hostname || '')) return;
      if (done()) return;
      e.preventDefault();
      open({ href: a.href, newTab: (a.getAttribute('target') || '').toLowerCase() === '_blank', el: a });
    } catch (x) { /* never block a booking */ }
  }, false);
})();

/* ===== Footer copyright year ===== */
document.querySelectorAll('.copyright-year').forEach(function (el) {
  el.textContent = new Date().getFullYear();
});
