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
    window.dataLayer.push({ event: eventName, form_type: formType || '' });
  };
})();
