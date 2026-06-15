from __future__ import annotations

from html import escape

from .time_logic import TimeState

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{time} — {tz}</title>
<style>
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: "DejaVu Sans", system-ui, sans-serif;
    background: {bg};
    color: {fg};
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .card {{
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 32px 48px;
  }}
  .glyph {{ font-size: 96px; line-height: 1; }}
  .time {{ font-size: 64px; font-weight: 700; line-height: 1; }}
  .sub {{ font-size: 18px; margin-top: 8px; }}
</style>
</head>
<body>
  <div class="card">
    <div class="glyph">{glyph}</div>
    <div>
      <div class="time">{time}</div>
      <div class="sub">{date}</div>
      <div class="sub">{tz}</div>
    </div>
  </div>
</body>
</html>
"""


def render_html(state: TimeState) -> str:
    if state.is_working:
        bg, fg, glyph = "#fff4c4", "#3c3200", "☀️"
    else:
        bg, fg, glyph = "#182040", "#ebf0ff", "🌙"
    return _TEMPLATE.format(
        bg=bg,
        fg=fg,
        glyph=glyph,
        time=escape(state.time_str),
        date=escape(state.date_str),
        tz=escape(state.tz_label),
    )
