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
    threshold: 0.15,
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

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;

      items.forEach(item => {
        if (filter === 'all' || item.dataset.category === filter) {
          item.classList.remove('hidden');
          item.style.display = '';
        } else {
          item.classList.add('hidden');
          item.style.display = 'none';
        }
      });
    });
  });
})();

/* ===== Gallery Modal ===== */
(function () {
  const modal = document.getElementById('galleryModal');
  const modalImg = document.getElementById('modalImage');
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
