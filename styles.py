"""Shared visual styles for the Kanji Flashcard app.

All aesthetic decisions are sourced from flashcard_deck.py and centralised
here.  Every @ui.page handler calls inject_styles() so the full CSS is
available on every route without duplication in source.

Design language (from flashcard_deck.py):
  - Gradient surfaces: blue front, green success, purple/orange variants
  - Border-radius 14-20px throughout
  - box-shadow: 0 4px 32px rgba(0,0,0,0.10) for cards
  - Uppercase tracking-wide micro-labels
  - font-light for display/hero text
  - Hover-lift on interactive tiles (translateY + shadow)
  - Action buttons: rounded-10px, font-weight 600, hover-lift
  - Progress bar: linear-gradient(90deg, #4ade80, #22c55e)
  - Full dark-mode support via .dark variants
"""

from nicegui import ui

_CSS = """
/* ══════════════════════════════════════════════════════════
   GRADIENT SURFACES  —  matches flip-front / flip-back in
   flashcard_deck.py.  Apply as an extra class on ui.card()
   or ui.element('div').
   ══════════════════════════════════════════════════════════ */

.surface-blue {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%) !important;
  border: 1.5px solid #c7d7f8 !important;
}
.dark .surface-blue {
  background: linear-gradient(135deg, #1e2a3a 0%, #1a2332 100%) !important;
  border-color: #2d3f5a !important;
}

.surface-green {
  background: linear-gradient(135deg, #f0fff4 0%, #e6f9ef 100%) !important;
  border: 1.5px solid #b7e4c7 !important;
}
.dark .surface-green {
  background: linear-gradient(135deg, #1a2e22 0%, #162419 100%) !important;
  border-color: #2a4a35 !important;
}

.surface-purple {
  background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%) !important;
  border: 1.5px solid #d8b4fe !important;
}
.dark .surface-purple {
  background: linear-gradient(135deg, #2e1a3a 0%, #261432 100%) !important;
  border-color: #6d28d9 !important;
}

.surface-orange {
  background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%) !important;
  border: 1.5px solid #fed7aa !important;
}
.dark .surface-orange {
  background: linear-gradient(135deg, #3a2a14 0%, #322410 100%) !important;
  border-color: #92400e !important;
}

.surface-indigo {
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%) !important;
  border: 1.5px solid #a5b4fc !important;
}
.dark .surface-indigo {
  background: linear-gradient(135deg, #1e1a3a 0%, #1a1632 100%) !important;
  border-color: #3730a3 !important;
}

.surface-red {
  background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%) !important;
  border: 1.5px solid #fecdd3 !important;
}
.dark .surface-red {
  background: linear-gradient(135deg, #3a1a1a 0%, #321414 100%) !important;
  border-color: #9f1239 !important;
}

/* ══════════════════════════════════════════════════════════
   GLOBAL CARD RADIUS  —  all Quasar cards get consistent
   border-radius to match the flashcard flip-face style.
   ══════════════════════════════════════════════════════════ */

.q-card {
  border-radius: 14px !important;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08) !important;
}

/* Auth-specific card (login / register) — slightly more dramatic */
.auth-card {
  border-radius: 20px !important;
  box-shadow: 0 8px 40px rgba(99, 102, 241, 0.14) !important;
  border: 1.5px solid #e0e7ff !important;
}
.dark .auth-card {
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.40) !important;
  border-color: #2d3f5a !important;
}

/* ══════════════════════════════════════════════════════════
   NAVIGATION TILES  —  matches the hover-scale pattern used
   in the dashboard nav grid.
   ══════════════════════════════════════════════════════════ */

.nav-tile {
  border-radius: 16px !important;
  transition: transform 0.22s cubic-bezier(.4,0,.2,1),
              box-shadow  0.22s cubic-bezier(.4,0,.2,1) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07) !important;
}
.nav-tile:hover {
  transform: translateY(-5px) !important;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.14) !important;
}

/* ══════════════════════════════════════════════════════════
   ACTION BUTTONS  —  mirrors the .rating-btn style from
   flashcard_deck.py.
   ══════════════════════════════════════════════════════════ */

.app-btn {
  border-radius: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.035em !important;
  transition: transform 0.15s, box-shadow 0.15s !important;
}
.app-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18) !important;
}

/* Destructive / danger variant */
.app-btn-danger {
  border-radius: 10px !important;
  font-weight: 600 !important;
  transition: transform 0.15s, box-shadow 0.15s !important;
}
.app-btn-danger:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 18px rgba(220, 38, 38, 0.28) !important;
}

/* ══════════════════════════════════════════════════════════
   MICRO-LABELS  —  the uppercase tracking-wide section
   headers used in flashcard_deck.py (e.g. "tap to reveal").
   ══════════════════════════════════════════════════════════ */

.micro-label {
  font-size: 0.70rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: #9ca3af;
}

/* ══════════════════════════════════════════════════════════
   PROGRESS BAR  —  identical to flashcard_deck.py.
   ══════════════════════════════════════════════════════════ */

.progress-bar-fill {
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  transition: width 0.4s ease;
}

/* ══════════════════════════════════════════════════════════
   STAT CHIPS  —  for progress visualiser and teacher dash.
   ══════════════════════════════════════════════════════════ */

.stat-chip {
  border-radius: 14px !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07) !important;
}

/* ══════════════════════════════════════════════════════════
   LIST ROWS  —  for student rosters, card lists, etc.
   ══════════════════════════════════════════════════════════ */

.list-row {
  border-radius: 10px;
  transition: background 0.12s;
}

/* ══════════════════════════════════════════════════════════
   DECK CARDS  —  flashcard library grid tiles.
   ══════════════════════════════════════════════════════════ */

.deck-card {
  border-radius: 16px !important;
  transition: transform 0.22s cubic-bezier(.4,0,.2,1),
              box-shadow  0.22s cubic-bezier(.4,0,.2,1) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07) !important;
}
.deck-card:hover {
  transform: translateY(-4px) !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.13) !important;
}
"""


def inject_styles() -> None:
    """Inject the shared application CSS into the current page.

    Call once at the top of every @ui.page handler.  Browsers
    de-duplicate identical <style> tags, so repeated calls across
    navigations are harmless.
    """
    ui.add_head_html(f'<style>{_CSS}</style>')
