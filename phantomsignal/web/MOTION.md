# Motion Layer — Tiered Cascade

The web console ships a progressive-enhancement motion system in
`static/css/motion.css` + `static/js/motion.js`. Five tiers, one animation
authority per layer, everything degrades to instant-render.

| Tier | Layer | Driver | What it does |
|------|-------|--------|--------------|
| 0 | Route changes | CSS `@view-transition` | Same-origin navigations cross-fade (0.28s); nav bar stays pinned |
| 1 | Page intro | GSAP timeline | Nav → header → staggered cards → stat-bar sweep; **once per tab session** |
| 2 | Ambient loops | GSAP (post-intro) | `[data-motion-ambient]` gentle float, started only `onComplete` |
| 3 | Scroll | Lenis + ScrollTrigger | Smooth inertial scroll (fine pointers), reveal-on-enter |
| 4 | Micro-interactions | CSS | Button lift, row-hover softening, focus-visible rings |

## Data-attribute contract (opt in per template)

| Attribute | Effect |
|-----------|--------|
| `data-motion` | Element joins the intro timeline (fade-up, 80ms stagger) |
| `data-motion-stagger` | Container — its direct children cascade in the intro (60ms cadence) |
| `data-motion-ambient` | Element starts a subtle yoyo float **after** the intro |
| `data-motion-scroll` | Element reveals when scrolled into view (`top 92%`, once) |
| `data-motion-scroll-stagger` | Container — children cascade when scrolled into view |

## Guarantees & rules

- **One driver per property.** When GSAP takes over `.stat-bar-fill` width it
  kills the CSS `transition` on that element first; `clearProps` restores
  natural styles after each tween so hover transforms keep working.
- **No invisible-content failure mode.** The `motion-pre` veil is added by an
  inline bootstrap only when motion will run (no reduced-motion, intro not yet
  played), and a 1.6s failsafe lifts it if CDNs are blocked.
- **Reduced motion is a kill-switch.** OS-level `prefers-reduced-motion`
  disables view transitions, all keyframe loops (glitch/sweep/pulse), Lenis,
  and the GSAP cascade — including a live mid-session switch.
- **Intro plays once per tab** (`sessionStorage: phantomsignal-intro-played`)
  so the dashboard's 10s live-reload never replays it.
- **bfcache-safe.** `pagehide` kills all tweens/triggers/Lenis; `pageshow`
  (persisted) re-boots the scroll tier.

## Libraries (CDN, deferred, optional)

`gsap 3.12.5`, `ScrollTrigger 3.12.5`, `lenis 1.1.14`. If a CDN is
unreachable the page renders normally without animation. To run fully
offline, vendor the three files into `static/vendor/` and repoint the
`<script defer>` tags in `templates/base.html`.
