/**
 * PhantomSignal Motion Layer — Tiered Cascade Orchestrator
 *
 *   Tier 0 · Route transitions     → pure CSS (motion.css, @view-transition)
 *   Tier 1 · Intro timeline        → GSAP, once per tab session
 *   Tier 2 · Ambient loops         → started only after the intro completes
 *   Tier 3 · Smooth scroll + reveals→ Lenis driving ScrollTrigger
 *   Tier 4 · Micro-interactions    → pure CSS (motion.css)
 *
 * Rules enforced:
 *   · one driver per property — before GSAP animates a property that a
 *     CSS transition also targets (e.g. .stat-bar-fill width), the CSS
 *     transition is neutralised inline so they never fight
 *   · transform/opacity only, direct mutation, clearProps on completion
 *     so hover transforms keep working afterwards
 *   · prefers-reduced-motion → everything renders instantly, and a live
 *     switch to 'reduce' mid-session tears motion down
 *   · libraries (gsap / ScrollTrigger / Lenis) are optional: if a CDN is
 *     blocked the page still renders, just without animation
 */
(function () {
  'use strict';

  var docEl = document.documentElement;

  /* ── Environment ─────────────────────────────────────────── */
  var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  var finePointer = window.matchMedia('(pointer: fine)').matches;
  var reduced = motionQuery.matches;

  var hasGsap = typeof window.gsap !== 'undefined';
  var hasST = hasGsap && typeof window.ScrollTrigger !== 'undefined';
  var hasLenis = typeof window.Lenis !== 'undefined';

  /* ── Timing config (single source of truth) ──────────────── */
  var T = {
    item: 0.45,          // individual fade-up blocks
    itemStagger: 0.08,   // between blocks
    group: 0.5,          // staggered children (stat cards, chips)
    groupStagger: 0.06,  // 60ms — the "one after another" cadence
    bars: 0.9,           // stat-bar width sweep
    reveal: 0.6,         // scroll-triggered reveals
    ease: 'power3.out',
    barEase: 'power2.inOut'
  };

  var INTRO_FLAG = 'phantomsignal-intro-played';
  var lenis = null;
  var introPlayed = false;

  /* ── Helpers ─────────────────────────────────────────────── */
  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function readFlag() {
    try { return sessionStorage.getItem(INTRO_FLAG) === '1'; }
    catch (e) { return false; }
  }

  function writeFlag() {
    try { sessionStorage.setItem(INTRO_FLAG, '1'); }
    catch (e) { /* private mode — intro replays, harmless */ }
  }

  /** Drop the pre-paint veil: called only after GSAP has set
   *  deterministic from-states, so nothing flashes. */
  function clearVeil() {
    docEl.classList.remove('motion-pre');
  }

  /* ── Stat bars: capture target widths, hand width to GSAP ── */
  function armBars() {
    return qsa('.stat-bar-fill').map(function (el) {
      var target = el.style.width || '0%';
      el.dataset.motionTarget = target;   // remembered for teardown restore
      el.style.transition = 'none';       // CSS `transition: width` would smear every rAF tick
      el.style.width = '0%';
      return { el: el, target: target };
    });
  }

  function releaseBars() {
    qsa('.stat-bar-fill').forEach(function (el) {
      if (el.dataset.motionTarget) el.style.width = el.dataset.motionTarget;
      el.style.transition = '';           // hand width back to CSS
    });
  }

  /* ── Tier 1 · Intro timeline ─────────────────────────────── */
  function playIntro(onComplete) {
    var blocks = qsa('.page-header').concat(qsa('[data-motion]'))
      .filter(function (el, i, arr) { return arr.indexOf(el) === i; }); // .page-header may also carry data-motion
    var groups = qsa('[data-motion-stagger]');
    var ambient = qsa('[data-motion-ambient]');
    var bars = armBars();

    var tl = gsap.timeline({
      defaults: { ease: T.ease },
      onComplete: function () {
        docEl.classList.add('motion-done');
        if (onComplete) onComplete();
      }
    });

    // 1 · Nav chrome slides down
    tl.fromTo('.nav-bar',
      { y: -12, autoAlpha: 0 },
      { y: 0, autoAlpha: 1, duration: 0.35, clearProps: 'transform,opacity,visibility' });

    // 2 · Header blocks cascade (title-block → actions)
    if (blocks.length) {
      tl.fromTo(blocks,
        { autoAlpha: 0, y: 16 },
        { autoAlpha: 1, y: 0, duration: T.item, stagger: T.itemStagger,
          clearProps: 'transform,opacity,visibility' },
        '-=0.15');
    }

    // 3 · Stagger groups — stat cards land one after another
    groups.forEach(function (wrap, i) {
      var kids = Array.prototype.slice.call(wrap.children);
      if (!kids.length) return;
      tl.fromTo(kids,
        { autoAlpha: 0, y: 18 },
        { autoAlpha: 1, y: 0, duration: T.group, stagger: T.groupStagger,
          clearProps: 'transform,opacity,visibility' },
        i === 0 ? '-=0.2' : '-=0.35');
    });

    // 4 · Stat bars sweep to their server-rendered values
    if (bars.length) {
      bars.forEach(function (b, i) {
        tl.to(b.el, { width: b.target, duration: T.bars, ease: T.barEase },
          '-=' + Math.max(0.2, T.bars - 0.08 * i));
      });
    }

    /* Tier 2 · Ambient loops begin ONLY after the intro finishes —
       ambient motion during a read-in is visual noise. */
    tl.add(function () {
      ambient.forEach(function (el) {
        gsap.to(el, {
          y: -4, duration: 2.6, ease: 'sine.inOut',
          yoyo: true, repeat: -1
        });
      });
    });
  }

  /* ── Tier 3 · Lenis smooth scroll + ScrollTrigger reveals ── */
  /* On repeat loads (e.g. the dashboard's 10s live-reload while scans run),
     anything already in the viewport snaps in instantly — re-animating
     above-the-fold content every refresh is the definition of slop. */
  function inViewport(el) {
    return el.getBoundingClientRect().top < window.innerHeight * 0.92;
  }

  function showInstant(els) {
    els.forEach(function (el) {
      gsap.set(el, { clearProps: 'all' });
    });
  }

  function initScrollTier() {
    if (hasST) {
      gsap.registerPlugin(ScrollTrigger);

      // Scroll-reveal singletons
      var singles = qsa('[data-motion-scroll]');
      var toReveal = singles;
      if (introPlayed) {
        showInstant(singles.filter(inViewport));
        toReveal = singles.filter(function (el) { return !inViewport(el); });
      }
      if (toReveal.length) {
        gsap.set(toReveal, { autoAlpha: 0, y: 24 });
        toReveal.forEach(function (el) {
          ScrollTrigger.create({
            trigger: el,
            start: 'top 92%',
            once: true,
            onEnter: function () {
              gsap.to(el, {
                autoAlpha: 1, y: 0, duration: T.reveal, ease: T.ease,
                overwrite: true,
                clearProps: 'transform,opacity,visibility'
              });
            }
          });
        });
      }

      // Scroll-reveal stagger groups (e.g. API chips)
      qsa('[data-motion-scroll-stagger]').forEach(function (wrap) {
        var kids = Array.prototype.slice.call(wrap.children);
        if (!kids.length) return;
        if (introPlayed && inViewport(wrap)) { showInstant(kids); return; }
        gsap.set(kids, { autoAlpha: 0, y: 12 });
        ScrollTrigger.create({
          trigger: wrap,
          start: 'top 92%',
          once: true,
          onEnter: function () {
            gsap.to(kids, {
              autoAlpha: 1, y: 0, duration: 0.5, ease: T.ease,
              stagger: T.groupStagger, overwrite: true,
              clearProps: 'transform,opacity,visibility'
            });
          }
        });
      });

      // Recalibrate once webfonts/images settle
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
      }
      window.addEventListener('load', function () { ScrollTrigger.refresh(); });

    } else if (hasGsap) {
      // GSAP present but ScrollTrigger blocked: reveal instantly,
      // no scroll coupling.
      var unrevealed = qsa('[data-motion-scroll]')
        .concat(qsa('[data-motion-scroll-stagger] > *'));
      if (unrevealed.length) gsap.set(unrevealed, { autoAlpha: 1, y: 0 });
    }

    // Lenis: desktop fine-pointer only; one scroll authority, so any
    // nested scroll well keeps native behavior via data-lenis-prevent.
    if (hasLenis && finePointer) {
      qsa('.terminal-output, pre, .data-table-wrap, .table-wrap, .code-block')
        .forEach(function (el) { el.setAttribute('data-lenis-prevent', ''); });

      lenis = new Lenis({ lerp: 0.11, wheelMultiplier: 0.9 });

      if (hasST) lenis.on('scroll', ScrollTrigger.update);

      if (hasGsap) {
        gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
        gsap.ticker.lagSmoothing(0);
      } else {
        var raf = function (time) { lenis.raf(time); requestAnimationFrame(raf); };
        requestAnimationFrame(raf);
      }

      // In-page anchors route through Lenis for eased scrolling
      document.addEventListener('click', function (ev) {
        var a = ev.target.closest ? ev.target.closest('a[href^="#"]') : null;
        if (!a) return;
        var target = document.getElementById(a.getAttribute('href').slice(1));
        if (!target) return;
        ev.preventDefault();
        lenis.scrollTo(target, { duration: 1.1 });
      });
    }
  }

  /* ── Tear-down (bfcache safety + live reduced-motion switch) ─ */
  function teardown() {
    if (hasST) ScrollTrigger.getAll().forEach(function (t) { t.kill(); });
    if (hasGsap) {
      gsap.globalTimeline.getChildren(true, true, true).forEach(function (tw) { tw.kill(); });
      gsap.set('.nav-bar, [data-motion], [data-motion-scroll], [data-motion-stagger] > *, [data-motion-scroll-stagger] > *',
        { clearProps: 'all' });
    }
    if (lenis) { lenis.destroy(); lenis = null; }
  }

  function revealEverything() {
    clearVeil();
    releaseBars();
  }

  /* ── Boot ────────────────────────────────────────────────── */
  function boot() {
    if (reduced || !hasGsap) {
      revealEverything();          // instant render, no animation
      return;
    }

    if (hasST) gsap.registerPlugin(ScrollTrigger);

    introPlayed = readFlag();
    if (!introPlayed) writeFlag(); // auto-refreshing pages must not replay

    // Deterministic from-states are set inside the timeline builders,
    // which run synchronously here — safe to drop the veil right after.
    if (!introPlayed) {
      playIntro();
    } else {
      // Repeat visit (e.g. dashboard's 10s live-reload): chrome and
      // header snap in, scroll tier still reveals below the fold.
      gsap.set('.nav-bar, .page-header, [data-motion], [data-motion-stagger] > *',
        { clearProps: 'all' });
    }
    clearVeil();

    initScrollTier();
  }

  window.addEventListener('pagehide', teardown);
  window.addEventListener('pageshow', function (ev) {
    if (ev.persisted && !reduced) boot();  // bfcache restore
  });

  // Live OS-level switch to reduced motion mid-session
  if (motionQuery.addEventListener) {
    motionQuery.addEventListener('change', function (e) {
      reduced = e.matches;
      teardown();
      if (!reduced) boot(); else revealEverything();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
