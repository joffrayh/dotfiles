#!/usr/bin/env python3
"""Windows 2000 style "Unlock Computer" lock screen for hyprlock.

Draws the dialog onto a full-screen background and writes hyprlock.conf
with the password field placed exactly over the drawn password box.
Re-run after changing resolution:  python3 make-lock.py [WIDTH HEIGHT]
"""
import getpass
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) == 3 else (1920, 1080)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PNG = os.path.join(HERE, "win2000-lock.png")
OUT_CONF = os.path.expanduser("~/.config/hypr/hyprlock.conf")
# hyprlock expands ~, so the generated conf doesn't hardcode the home directory
OUT_PNG_CONF = "~/" + os.path.relpath(OUT_PNG, os.path.expanduser("~"))
USER = getpass.getuser()

FONT = "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
FONT_B = "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
f_body = ImageFont.truetype(FONT, 19)
f_title = ImageFont.truetype(FONT_B, 19)
f_btn = ImageFont.truetype(FONT, 19)

DESKTOP = (58, 110, 165)
FACE = (212, 208, 200)
WHITE = (255, 255, 255)
SHADOW = (128, 128, 128)
DARK = (64, 64, 64)
BLACK = (0, 0, 0)

img = Image.new("RGB", (W, H), DESKTOP)
d = ImageDraw.Draw(img)


def bevel(x0, y0, x1, y1, outer_tl, outer_br, inner_tl, inner_br):
    """Two-pixel Windows bevel around the box (x0, y0)-(x1, y1), inclusive."""
    d.line([(x0, y1), (x0, y0), (x1, y0)], fill=outer_tl)
    d.line([(x0, y1), (x1, y1), (x1, y0)], fill=outer_br)
    d.line([(x0 + 1, y1 - 1), (x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=inner_tl)
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y0 + 1)], fill=inner_br)


def raised(x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=FACE)
    bevel(x0, y0, x1, y1, WHITE, DARK, FACE, SHADOW)


def sunken(x0, y0, x1, y1, fill=WHITE):
    d.rectangle([x0, y0, x1, y1], fill=fill)
    bevel(x0, y0, x1, y1, SHADOW, WHITE, DARK, FACE)


def button(x0, y0, w, h, text, default=False):
    if default:
        d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=BLACK)
        x0, y0, w, h = x0 + 1, y0 + 1, w - 2, h - 2
    raised(x0, y0, x0 + w - 1, y0 + h - 1)
    tw = d.textlength(text, font=f_btn)
    d.text((x0 + (w - tw) / 2, y0 + h / 2), text, font=f_btn, fill=BLACK, anchor="lm")


# --- dialog frame -----------------------------------------------------------
DW, DH = 660, 360
dx, dy = (W - DW) // 2, (H - DH) // 2
d.rectangle([dx + 6, dy + 6, dx + DW + 5, dy + DH + 5], fill=(30, 60, 95))  # soft drop shadow
raised(dx, dy, dx + DW - 1, dy + DH - 1)

# title bar: classic dark-to-light blue gradient
tx0, ty0, tx1, ty1 = dx + 4, dy + 4, dx + DW - 5, dy + 33
for x in range(tx0, tx1 + 1):
    t = (x - tx0) / (tx1 - tx0)
    c = tuple(round(a + (b - a) * t) for a, b in zip((10, 36, 106), (166, 202, 240)))
    d.line([(x, ty0), (x, ty1)], fill=c)
d.text((tx0 + 8, (ty0 + ty1) / 2), "Unlock Computer", font=f_title, fill=WHITE, anchor="lm")

# close button (decorative)
cb = 24
cx0, cy0 = tx1 - cb - 3, ty0 + 3
raised(cx0, cy0, cx0 + cb - 1, cy0 + cb - 3)
for o in (0, 1):
    d.line([(cx0 + 7 + o, cy0 + 6), (cx0 + cb - 9 + o, cy0 + cb - 9)], fill=BLACK)
    d.line([(cx0 + 7 + o, cy0 + cb - 9), (cx0 + cb - 9 + o, cy0 + 6)], fill=BLACK)

# --- padlock icon -----------------------------------------------------------
ix, iy = dx + 28, dy + 62
d.arc([ix + 10, iy, ix + 38, iy + 30], 180, 360, fill=DARK, width=5)
d.line([(ix + 12, iy + 15), (ix + 12, iy + 24)], fill=DARK, width=5)
d.line([(ix + 36, iy + 15), (ix + 36, iy + 24)], fill=DARK, width=5)
d.rectangle([ix + 2, iy + 22, ix + 46, iy + 56], fill=(232, 184, 40), outline=(120, 90, 0))
d.line([(ix + 4, iy + 24), (ix + 44, iy + 24)], fill=(252, 228, 140))
d.ellipse([ix + 19, iy + 32, ix + 29, iy + 42], fill=(70, 50, 0))
d.rectangle([ix + 22, iy + 40, ix + 26, iy + 49], fill=(70, 50, 0))

# --- message ----------------------------------------------------------------
mx = dx + 100
d.text((mx, dy + 64), "This computer is in use and has been locked.", font=f_body, fill=BLACK)
d.text((mx, dy + 98), f"Only {USER} or an administrator can unlock", font=f_body, fill=BLACK)
d.text((mx, dy + 122), "this computer.", font=f_body, fill=BLACK)

# --- fields -----------------------------------------------------------------
lx, fx, fw, fh = mx, dx + 236, 390, 34
uy, py = dy + 176, dy + 224
d.text((lx, uy + fh / 2), "User name:", font=f_body, fill=BLACK, anchor="lm")
sunken(fx, uy, fx + fw - 1, uy + fh - 1, fill=FACE)  # read-only field
d.text((fx + 8, uy + fh / 2), USER, font=f_body, fill=SHADOW, anchor="lm")
d.text((lx, py + fh / 2), "Password:", font=f_body, fill=BLACK, anchor="lm")
sunken(fx, py, fx + fw - 1, py + fh - 1)

# --- buttons ----------------------------------------------------------------
bw, bh, by = 110, 36, dy + DH - 60
button(dx + DW - 2 * bw - 32, by, bw, bh, "OK", default=True)
button(dx + DW - bw - 22, by, bw, bh, "Cancel")

img.save(OUT_PNG)

# --- hyprlock.conf ----------------------------------------------------------
# Password field sits inside the 2px bevel of the drawn box.
inner_w, inner_h = fw - 4, fh - 4
icx = fx + 2 + inner_w / 2
icy = py + 2 + inner_h / 2
off_x = round(icx - W / 2)
off_y = round(H / 2 - icy)  # hyprlock: +y is up

conf = f"""# Generated by ~/.config/hypr/lock/make-lock.py ({W}x{H}). Edit the script, not this file.
general {{
    hide_cursor = false
}}

background {{
    path = {OUT_PNG_CONF}
    color = rgb(3a6ea5)
}}

input-field {{
    size = {inner_w}, {inner_h}
    position = {off_x}, {off_y}
    halign = center
    valign = center
    rounding = 0
    outline_thickness = 0
    inner_color = rgb(ffffff)
    font_color = rgb(000000)
    check_color = rgb(ffffff)
    fail_color = rgb(ffffff)
    capslock_color = rgb(ffffe1)
    dots_size = 0.28
    dots_spacing = 0.35
    dots_center = false
    dots_rounding = -1
    fade_on_empty = false
    placeholder_text =
    fail_text = <span color="#c00000">The password is incorrect.</span>
    font_family = Liberation Sans
}}
"""
with open(OUT_CONF, "w") as fh_:
    fh_.write(conf)
print(f"wrote {OUT_PNG} and {OUT_CONF} (field at {off_x},{off_y})")
