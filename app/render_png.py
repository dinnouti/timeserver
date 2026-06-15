from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont

from .time_logic import TimeState

WIDTH = 480
HEIGHT = 200

WORKING_BG = (255, 244, 196)
WORKING_FG = (60, 50, 0)
OFF_BG = (24, 32, 64)
OFF_FG = (235, 240, 255)

TEXT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TEXT_FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMOJI_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

EMOJI_FONT_NATIVE_SIZE = 109


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _load_emoji_font() -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(EMOJI_FONT_PATH, EMOJI_FONT_NATIVE_SIZE)


def render_png(state: TimeState) -> bytes:
    bg = WORKING_BG if state.is_working else OFF_BG
    fg = WORKING_FG if state.is_working else OFF_FG
    glyph = "☀️" if state.is_working else "\U0001F319"

    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)

    time_font = _load_font(TEXT_FONT_PATH, 64)
    sub_font = _load_font(TEXT_FONT_PATH_REGULAR, 20)

    emoji_layer = Image.new("RGBA", (EMOJI_FONT_NATIVE_SIZE, EMOJI_FONT_NATIVE_SIZE), (0, 0, 0, 0))
    emoji_draw = ImageDraw.Draw(emoji_layer)
    try:
        emoji_font = _load_emoji_font()
        emoji_draw.text((0, 0), glyph, font=emoji_font, embedded_color=True)
    except OSError:
        emoji_font = _load_font(TEXT_FONT_PATH, 80)
        emoji_draw.text((0, 0), glyph, font=emoji_font, fill=fg)

    target_emoji_size = 110
    emoji_scaled = emoji_layer.resize((target_emoji_size, target_emoji_size), Image.LANCZOS)
    emoji_x = 24
    emoji_y = (HEIGHT - target_emoji_size) // 2
    img.paste(emoji_scaled, (emoji_x, emoji_y), emoji_scaled)

    text_x = emoji_x + target_emoji_size + 24
    draw.text((text_x, 28), state.time_str, font=time_font, fill=fg)
    draw.text((text_x, 110), state.date_str, font=sub_font, fill=fg)
    draw.text((text_x, 140), state.tz_label, font=sub_font, fill=fg)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
