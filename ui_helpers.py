"""
ui_helpers.py
Shared styling helpers for app.py - keeps score-tier colors (green/amber/red)
consistent across all 3 tabs instead of each tab picking its own colors.
"""

# Consistent tier thresholds used everywhere a 0-100 score is shown.
TIER_STRONG = {"label": "Strong", "color": "#16A34A", "bg": "#DCFCE7"}
TIER_MODERATE = {"label": "Moderate", "color": "#D97706", "bg": "#FEF3C7"}
TIER_WEAK = {"label": "Weak", "color": "#DC2626", "bg": "#FEE2E2"}


def get_score_tier(score: float) -> dict:
    """Returns the tier dict (label/color/bg) for a 0-100 score."""
    if score >= 70:
        return TIER_STRONG
    elif score >= 50:
        return TIER_MODERATE
    return TIER_WEAK


def score_badge_html(score: float, label: str) -> str:
    """Renders a colored pill badge for a score, e.g. 'Match Score: 77.8% · Strong'."""
    tier = get_score_tier(score)
    return (
        f'<div style="display:inline-flex;align-items:center;gap:10px;'
        f'background:{tier["bg"]};border-radius:12px;padding:14px 20px;margin:4px 0;">'
        f'<span style="font-size:26px;font-weight:700;color:{tier["color"]};">{score}%</span>'
        f'<span style="font-size:13px;color:#374151;">{label}</span>'
        f'<span style="font-size:12px;font-weight:600;color:{tier["color"]};'
        f'background:white;border-radius:8px;padding:2px 8px;">{tier["label"]}</span>'
        f'</div>'
    )


def section_header_html(icon: str, title: str) -> str:
    """Consistent styled section header used above each tab's main content."""
    return (
        f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0 16px 0;">'
        f'<span style="font-size:22px;">{icon}</span>'
        f'<span style="font-size:20px;font-weight:700;color:#111827;">{title}</span>'
        f'</div>'
    )

