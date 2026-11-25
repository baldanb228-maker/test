"""Казино, Dately-ийн хөдөлдөг pixel art GIF зургууд (кодоор зурсан, фонт шаардахгүй)."""
import io
import math
import random

import discord
from PIL import Image, ImageDraw

from pix import Canvas, card, chips, fit, shade, sparkle, SCALE

GOLD = (250, 204, 21)
WHITE = (250, 250, 250)
_cache: dict[str, bytes] = {}
RED_NUMS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


# ---------------- GIF бичигч ----------------
def encode_gif(frames: list[Image.Image], ms=80, colors: int = 128) -> bytes:
    """Бүх frame-д нэг палитр ашиглан (өнгө хэлбэлзэхгүй) жижиг GIF гаргана."""
    w, h = frames[0].size
    sheet = Image.new("RGB", (w, h * len(frames)))
    for k, f in enumerate(frames):
        sheet.paste(f, (0, h * k))
    pal = sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = []
    for f in frames:
        big = fit(f)
        out.append(big.quantize(palette=pal, dither=Image.Dither.NONE))
    buf = io.BytesIO()
    out[0].save(buf, "GIF", save_all=True, append_images=out[1:], duration=ms, loop=0, optimize=False, disposal=1)
    return buf.getvalue()


def _felt(cv, a=(14, 78, 52), b=(6, 40, 28)):
    cv.gradient(a, b, bands=8)
    r = random.Random(3)
    for _ in range(90):
        cv.px(r.randrange(cv.w), r.randrange(cv.h), shade(a, 0.82))


def _title(cv, s, y=3, scale=2, col=GOLD):
    cv.ctext(cv.w // 2, y, s, col, scale, shadow=(20, 14, 6))


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ---------------- roulette ----------------
def roulette(i, n, num=17):
    p = i / (n - 1)
    cv = Canvas()
    _felt(cv)
    cx, cy, R = 48, 46, 30
    rot = p * 2 * math.pi
    cv.ell(cx - R - 3, cy - R - 3, 2 * R + 7, 2 * R + 7, (74, 44, 22), (30, 18, 8))
    for y in range(cy - R, cy + R + 1):
        for x in range(cx - R, cx + R + 1):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            if r > R:
                continue
            ang = (math.atan2(dx, -dy) - rot) % (2 * math.pi)
            f = ang / (2 * math.pi) * 37
            idx = int(f)
            if r > 24:
                col = (96, 60, 30)
            elif r > 17:
                col = (30, 140, 70) if idx == 0 else ((200, 30, 40) if idx in RED_NUMS else (28, 28, 34))
                if abs(f - round(f)) < 0.11 and r > 18:
                    col = (230, 200, 90)
            elif r > 13:
                col = (214, 168, 56)
            elif r > 5:
                col = (96, 60, 30) if (x + y) % 2 else (110, 70, 34)
            else:
                col = (230, 200, 90)
            cv.px(x, y, col)
    # ээлжлэх тэмдэг (хөдөлгөөн илүү харагдана)
    ha = rot * -1 + 0.3
    for k in range(4):
        a = ha + k * math.pi / 2
        cv.px(cx + int(math.sin(a) * 9), cy - int(math.cos(a) * 9), (255, 240, 170))
        cv.px(cx + int(math.sin(a) * 10), cy - int(math.cos(a) * 10), (255, 240, 170))
    cv.rect(cx - 1, cy - 2, 3, 5, (255, 240, 170))
    # бөмбөлөг: эсрэг чиглэлд хурдан эргэнэ, төгсгөлд дотогш орно
    e = _ease(p)
    ba = rot + (num + 0.5) / 37 * 2 * math.pi - 3 * 2 * math.pi * (1 - e)
    br = 25.5 - 5 * _ease((p - 0.72) / 0.28)
    cv.ell(int(cx + math.sin(ba) * br) - 1, int(cy - math.cos(ba) * br) - 1, 3, 3, WHITE, (150, 150, 160))
    # ширээний тор
    gx, gy = 94, 14
    nums = [3, 6, 9, 12, 2, 5, 8, 11, 1, 4, 7, 10]
    hot = int(p * 12)
    for k, num in enumerate(nums):
        x, y = gx + (k % 4) * 15, gy + (k // 4) * 11
        red = num in (1, 3, 5, 7, 9, 12)
        cv.box(x, y, 14, 10, (190, 28, 38) if red else (26, 26, 32), (255, 245, 140) if k == hot else (230, 200, 90))
        cv.ctext(x + 7, y + 2, str(num), WHITE)
    chips(cv, 104, 74, (200, 30, 40), 3)
    chips(cv, 120, 76, (40, 90, 200), 4)
    chips(cv, 136, 74, (30, 30, 36), 3)
    chips(cv, 150, 77, GOLD, 2)
    if i % 4 < 2:
        sparkle(cv, 152, 60, GOLD)
    else:
        sparkle(cv, 100, 66, GOLD)
    _title(cv, "ROULETTE", 2, 1, GOLD)
    return cv


# ---------------- blackjack ----------------
def blackjack(i, n):
    cv = Canvas()
    _felt(cv)
    _title(cv, "BLACKJACK", 3, 2)
    t1 = _ease(i / 5)
    t2 = _ease((i - 3) / 5)
    x1 = int(170 + (44 - 170) * t1)
    x2 = int(170 + (62 - 170) * t2)
    y1 = int(-40 + (24 + 40) * t1)
    y2 = int(-40 + (20 + 40) * t2)
    card(cv, x1, y1, "K", "heart", True, 28, 40)
    card(cv, x2, y2, "A", "spade", False, 28, 40)
    if i >= 9:
        flash = (i // 2) % 2 == 0
        cv.text(104, 26, "21", GOLD if flash else WHITE, 5, shadow=(20, 14, 6))
        cv.ctext(122, 56, "x2.5", WHITE, 1)
        for k, (sx, sy) in enumerate(((100, 22), (146, 30), (58, 18), (120, 14))):
            if (i + k) % 3 == 0:
                sparkle(cv, sx, sy, GOLD)
    chips(cv, 20, 74, (200, 30, 40), 4)
    chips(cv, 34, 76, (30, 30, 36), 3)
    chips(cv, 140, 76, (40, 90, 200), 3)
    chips(cv, 152, 74, GOLD, 4)
    return cv


# ---------------- crash ----------------
def rocket(cv, x, y, flame=0):
    cv.poly([(x, y - 9), (x + 4, y - 3), (x + 4, y + 6), (x - 4, y + 6), (x - 4, y - 3)], (236, 240, 248))
    cv.poly([(x, y - 9), (x + 3, y - 4), (x - 3, y - 4)], (220, 38, 38))
    cv.ell(x - 1, y - 2, 3, 3, (60, 150, 230), (30, 70, 120))
    cv.poly([(x - 4, y + 2), (x - 8, y + 8), (x - 4, y + 6)], (200, 40, 40))
    cv.poly([(x + 4, y + 2), (x + 8, y + 8), (x + 4, y + 6)], (200, 40, 40))
    h = 8 + flame * 3
    cv.poly([(x - 3, y + 7), (x + 3, y + 7), (x, y + 7 + h)], (250, 150, 30))
    cv.poly([(x - 1, y + 7), (x + 1, y + 7), (x, y + 7 + h - 4)], (255, 230, 120))


def crash(i, n):
    cv = Canvas()
    cv.gradient((10, 12, 38), (24, 14, 56), bands=8)
    cv.stars(50, 5, 60)
    for k, (sx, sy) in enumerate(((20, 10), (70, 6), (130, 12), (100, 30))):  # одод анивчина
        if (i + k) % 3 == 0:
            cv.px(sx, sy, (255, 255, 200))
    sh = (i * 6) % 16  # тор доош гулгана
    for x in range(8, 150, 16):
        cv.line([(x, 14), (x, 74)], (36, 40, 80))
    for y in range(18 - 14 + sh, 76, 14):
        if 14 <= y <= 74:
            cv.line([(8, y), (150, y)], (36, 40, 80))
    run = n - 5
    t = min(1.0, i / run)
    k = int(t * 105)
    pts = [(10 + j, 72 - (math.exp(2.3 * j / 105) - 1) / (math.exp(2.3) - 1) * 56) for j in range(0, k + 1)]
    for (x, y) in pts[::2]:
        cv.line([(x, y), (x, 74)], (18, 70, 54))
    for j in range(len(pts) - 1):
        tt = j / 105
        col = (int(60 + 190 * tt), int(220 - 40 * tt), int(110 - 70 * tt))
        cv.line([pts[j], pts[j + 1]], col, 2)
    shake = 1 if (i > run and i % 2) else 0
    rocket(cv, int(pts[-1][0]) + 2 + shake, int(pts[-1][1]) - 2, i % 2)
    mult = 1 + (math.exp(2.3 * t) - 1) / (math.exp(2.3) - 1) * 8.5
    cv.text(14, 22, f"x{mult:.1f}", GOLD if t < 1 else (255, 120, 90), 2, shadow=(40, 20, 4))
    _title(cv, "CRASH", 3, 2, (255, 120, 90))
    return cv


# ---------------- crash: бодит тоглоомтой синхрон ----------------
def _crash_bg(cv, f, tint=None):
    top, bot = ((10, 12, 38), (24, 14, 56)) if tint is None else tint
    cv.gradient(top, bot, bands=8)
    cv.stars(50, 5, 60)
    for k, (sx, sy) in enumerate(((20, 10), (70, 6), (130, 12), (100, 30))):
        if (f + k) % 3 == 0:
            cv.px(sx, sy, (255, 255, 200))
    for x in range(10, 150, 16):
        cv.line([(x, 26), (x, 74)], (36, 40, 80))
    for y in range(26, 76, 12):
        cv.line([(10, y), (150, y)], (36, 40, 80))


def _crash_pts(hist, last):
    """hist: дууссан алхмуудын үржвэр; last: одоогийн (завсрын) үржвэр."""
    ms = list(hist[:-1]) + [last]
    steps = max(len(ms) - 1, 8)
    top = max(2.5, ms[-1] * 1.3, max(ms) * 1.05)
    lt = math.log(top)
    pts = []
    for j, m in enumerate(ms):
        pts.append((10 + 118 * j / steps, 74 - 46 * math.log(max(m, 1.0)) / lt))
    return pts


def _crash_curve(cv, pts, col_fn):
    for (x, y) in pts[::2]:
        cv.line([(x, y), (x, 74)], (18, 60, 50))
    for j in range(len(pts) - 1):
        cv.line([pts[j], pts[j + 1]], col_fn(j / max(len(pts) - 1, 1)), 2)


def _mult_col(m):
    return GOLD if m < 3 else ((255, 170, 60) if m < 6 else (255, 110, 80))


def crash_live_gif(hist: list[float], frames: int = 4) -> bytes:
    """Одоо хүртэлх муруй + ракет, сүүлийн алхмаас одоогийн үржвэр хүртэл өснө."""
    cur = hist[-1]
    prev = hist[-2] if len(hist) > 1 else cur
    out = []
    for f in range(frames):
        tt = (f + 1) / frames if len(hist) > 1 else 1.0
        m = prev * (cur / prev) ** tt if prev > 0 else cur
        cv = Canvas()
        _crash_bg(cv, f)
        pts = _crash_pts(hist, m)
        _crash_curve(cv, pts, lambda t: (int(60 + 190 * t), int(220 - 40 * t), int(110 - 70 * t)))
        rocket(cv, int(pts[-1][0]) + 2, int(pts[-1][1]) - 2, f % 2)
        cv.text(14, 6, "CRASH", (255, 120, 90), 2, shadow=(40, 20, 4))
        label = f"x{m:.2f}"
        cv.text(158 - cv.text_w(label, 3) - 6, 4, label, _mult_col(m), 3, shadow=(40, 20, 4))
        out.append(cv.im)
    return encode_gif(out, 90)


def _boom(cv, x, y, r):
    cv.ell(x - r, y - r, 2 * r, 2 * r, (255, 120, 30))
    if r > 4:
        cv.ell(x - r + 3, y - r + 3, 2 * r - 6, 2 * r - 6, (255, 210, 70))
    if r > 9:
        cv.ell(x - r + 7, y - r + 7, 2 * r - 14, 2 * r - 14, (255, 250, 200))
    rnd = random.Random(r)
    for _ in range(14):
        a = rnd.random() * 6.283
        d = r + rnd.randrange(2, 12)
        cv.rect(int(x + math.cos(a) * d), int(y + math.sin(a) * d), 2, 2, (255, 160, 60))


def crash_end_gif(hist: list[float], crash_pt: float, won: bool, cash_mult: float = 0.0) -> bytes:
    """won=False: ракет дэглэв (LOST). won=True: мөнгө авсан (WIN)."""
    out, dur = [], []
    if not won:
        base = list(hist) + [crash_pt] if hist[-1] < crash_pt else list(hist)
        pts = _crash_pts(base, crash_pt)
        ex, ey = int(pts[-1][0]) + 2, int(pts[-1][1]) - 2
        for f, r in enumerate((2, 5, 9, 13, 17, 20, 21)):
            cv = Canvas()
            _crash_bg(cv, f)
            _crash_curve(cv, pts, lambda t: (int(60 + 190 * t), int(220 - 40 * t), int(110 - 70 * t)))
            _boom(cv, ex, ey, r)
            cv.text(14, 6, "CRASH", (255, 120, 90), 2, shadow=(40, 20, 4))
            out.append(cv.im)
            dur.append(70)
        for f in range(2):  # үр дүн: тогтмол, удаан харагдана
            cv = Canvas()
            _crash_bg(cv, f, ((52, 8, 14), (24, 6, 12)))
            _crash_curve(cv, pts, lambda t: (120, 50, 50))
            cv.ctext(80, 12, "LOST", (255, 70, 70), 4, shadow=(40, 6, 6))
            cv.ctext(80, 40, f"CRASHED x{crash_pt:.2f}", (255, 190, 170), 2, shadow=(40, 6, 6))
            cv.ctext(80, 60, "ROCKET EXPLODED", (200, 120, 120), 1)
            out.append(cv.im)
            dur.append(1500)
    else:
        pts0 = _crash_pts(hist, hist[-1])
        sx, sy = pts0[-1]
        for f in range(6):  # ракет аюулгүй зайлж одод руу гарна
            cv = Canvas()
            _crash_bg(cv, f)
            _crash_curve(cv, pts0, lambda t: (250, int(200 - 40 * t), 60))
            rocket(cv, int(sx + 2 + f * 9), int(sy - 2 - f * 6), f % 2)
            cv.text(14, 6, "CASH OUT", (120, 255, 160), 2, shadow=(6, 40, 20))
            out.append(cv.im)
            dur.append(70)
        for f in range(2):
            cv = Canvas()
            _crash_bg(cv, f, ((8, 52, 30), (6, 28, 20)))
            _crash_curve(cv, pts0, lambda t: (250, int(210 - 30 * t), 70))
            for k, (qx, qy) in enumerate(((22, 14), (136, 16), (30, 56), (130, 58), (80, 6))):
                sparkle(cv, qx, qy, GOLD if (f + k) % 2 else (255, 255, 255))
            cv.ctext(80, 12, "WIN", (120, 255, 160), 4, shadow=(6, 40, 20))
            cv.ctext(80, 40, f"CASHED x{cash_mult:.2f}", (255, 235, 140), 2, shadow=(6, 40, 20))
            cv.ctext(80, 60, f"ROCKET WAS x{crash_pt:.2f}", (140, 200, 160), 1)
            out.append(cv.im)
            dur.append(1500)
    return encode_gif(out, dur)


# ---------------- horse race ----------------
def horse(cv, x, y, coat, jockey, step=0):
    dark = shade(coat, 0.6)
    cv.ell(x, y, 17, 8, coat)
    cv.poly([(x + 13, y + 3), (x + 18, y - 5), (x + 22, y - 4), (x + 19, y + 3)], coat)
    cv.poly([(x + 18, y - 5), (x + 24, y - 4), (x + 25, y - 1), (x + 20, y - 1)], coat)
    cv.px(x + 22, y - 3, (10, 10, 10))
    cv.line([(x + 17, y - 5), (x + 14, y + 1)], dark, 2)
    cv.poly([(x + 1, y + 2), (x - 5, y + 6 + step), (x - 3, y + 8 + step), (x + 2, y + 5)], dark)
    for lx, ph in ((x + 2, 0), (x + 5, 1), (x + 11, 1), (x + 14, 0)):
        off = step if ph else -step
        cv.line([(lx, y + 6), (lx + off, y + 13)], dark, 1)
        cv.rect(lx + off, y + 13, 2, 1, (30, 20, 10))
    cv.rect(x + 7, y - 6, 4, 6, jockey)
    cv.ell(x + 7, y - 10, 4, 4, (240, 200, 160))
    cv.rect(x + 7, y - 11, 4, 2, shade(jockey, 0.8))


HORSE_COATS = [(120, 70, 36), (236, 200, 60), (240, 240, 235), (240, 140, 40), (40, 32, 30), (200, 40, 40)]
HORSE_JK = [(60, 90, 220), (200, 40, 50), (50, 150, 70), (130, 60, 190), (250, 210, 50), (60, 200, 220)]


def _mini_horse(cv, x, y, coat, jk, step):
    dark = shade(coat, 0.6)
    cv.ell(x, y, 10, 5, coat)
    cv.ell(x + 8, y - 3, 5, 4, coat)
    cv.px(x + 11, y - 2, (10, 10, 10))
    cv.rect(x - 2, y + 1, 2, 3, dark)
    for lx, ph in ((x + 1, 0), (x + 7, 1)):
        off = step if ph else -step
        cv.line([(lx, y + 4), (lx + off, y + 8)], dark, 1)
    cv.rect(x + 4, y - 3, 3, 4, jk)
    cv.rect(x + 4, y - 5, 3, 2, (240, 200, 160))


def horse_race(i, n, order=(0, 1, 2, 3, 4, 5), pick=None):
    """order: морьдын дугаарууд дуусах дарааллаар (order[0] түрүүлнэ)."""
    cv = Canvas()
    cv.gradient((110, 190, 245), (190, 228, 250), bands=6, y1=22)
    cv.rect(0, 22, 160, 58, (60, 150, 70))
    cv.rect(0, 28, 160, 52, (176, 128, 74))
    for k in range(7):
        cv.rect(0, 30 + k * 8, 160, 1, (150, 104, 58))
    for x in range(8, 150, 5):  # үзэгчид
        cv.px(x, 19 + ((x * 7) % 3) + ((i + x) % 2), [(220, 60, 60), (60, 90, 220), (240, 210, 60)][x % 3])
    for j in range(12):  # финиш
        for k in range(2):
            cv.rect(140 + k * 3, 28 + j * 4, 3, 4, (250, 250, 250) if (j + k) % 2 == 0 else (20, 20, 20))
    p = i / (n - 1)
    rank = {h: r for r, h in enumerate(order)}
    step = 2 if i % 2 else -2
    for h in range(6):
        y = 34 + h * 8
        T = 1.0 + 0.09 * rank[h]
        prog = min(1.0, p / T)
        prog = max(0.0, min(1.0, prog + 0.025 * math.sin(p * 17 + h * 2.1) * min(prog, 1 - prog) * 4))
        x = int(14 + 112 * prog)
        if pick == h:
            cv.rect(0, y - 4, 160, 9, (210, 170, 60))
            cv.rect(0, y - 4, 160, 9, (190, 150, 50))
        cv.ctext(6, y - 3, str(h + 1), WHITE if pick != h else (40, 20, 0), 1)
        _mini_horse(cv, x, y + (1 if i % 2 else 0), HORSE_COATS[h], HORSE_JK[h], step)
    cv.ctext(80, 4, "HORSE RACE", WHITE, 2, shadow=(20, 60, 100))
    return cv


# ---------------- coinflip ----------------
def coinflip(i, n, heads=False):
    p = i / (n - 1)
    cv = Canvas()
    cv.gradient((40, 22, 80), (18, 10, 44), bands=8)
    cv.stars(40, 9)
    cx, cy = 80, 42
    th = p * (5 if heads else 4) * math.pi   # төгсгөлд зөв тал дээш харна
    c = math.cos(th)
    lift = int(16 * math.sin(p * math.pi))
    w = max(4, int(45 * abs(c)))
    h = 45
    sh = max(10, 40 - lift)
    cv.ell(cx - sh // 2, cy + 24, sh, 7, (10, 6, 24))
    top = cy - 22 - lift
    cv.ell(cx - w // 2, top, w, h, (170, 112, 20), (90, 56, 8))
    if w > 6:
        cv.ell(cx - w // 2 + 1, top + 1, max(3, w - 2), h - 2, (240, 190, 50), (200, 140, 30))
    if w > 14:
        iw = int(w * 0.72)
        cv.ell(cx - iw // 2, top + 7, iw, h - 14, (252, 214, 90), (200, 150, 40))
        if c > 0:  # T тал (сүүл)
            m = (180, 120, 20)
            cv.rect(cx - max(2, iw // 4), top + 15, max(4, iw // 2), 4, m)
            cv.rect(cx - 2, top + 15, 5, 18, m)
        else:      # одны тал (тоо)
            cv.poly([(cx, top + 14), (cx + 3, top + 21), (cx + 10, top + 22), (cx + 5, top + 27), (cx + 6, top + 34),
                     (cx, top + 30), (cx - 6, top + 34), (cx - 5, top + 27), (cx - 10, top + 22), (cx - 3, top + 21)], (180, 120, 20))
    for k, (sx, sy) in enumerate(((30, 18), (128, 26), (44, 60), (118, 58), (96, 12))):
        if (i + k) % 4 < 2:
            sparkle(cv, sx, sy, GOLD)
    for k in range(3):
        o = (i * 3) % 8
        cv.line([(cx - 34 - k * 4 - o, cy - 8 + k * 6), (cx - 26 - k * 4 - o, cy - 8 + k * 6)], (140, 110, 200))
        cv.line([(cx + 28 + k * 4 + o, cy - 8 + k * 6), (cx + 36 + k * 4 + o, cy - 8 + k * 6)], (140, 110, 200))
    _title(cv, "COIN FLIP", 3, 2)
    return cv


# ---------------- dice ----------------
def die(cv, x, y, v, size=26):
    cv.ell(x + 2, y + size - 2, size - 2, 5, (30, 6, 8))
    cv.box(x, y, size, size, (248, 246, 240), (80, 80, 90))
    cv.rect(x + 1, y + 1, size - 2, 2, (255, 255, 255))
    cv.rect(x + 1, y + size - 3, size - 2, 2, (210, 208, 200))
    p = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)], 4: [(0, 0), (2, 0), (0, 2), (2, 2)],
         5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)], 6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}[v]
    step = size // 4
    for gx, gy in p:
        cv.ell(x + step - 1 + gx * step, y + step - 1 + gy * step, 4, 4, (190, 30, 40) if v == 1 else (30, 30, 38))


def dice(i, n, roll=5):
    cv = Canvas()
    cv.gradient((90, 14, 28), (40, 6, 16), bands=8)
    cv.stars(25, 4, 50, (255, 170, 150))
    rolling = n - 5
    r = random.Random(100 + i)
    if i < rolling:
        v = r.randint(1, 6)
        jitter = 14 - int(12 * i / rolling)
        dx, dy = r.randint(-jitter, jitter), -abs(int(14 * math.sin(i * 0.9)))
    else:
        v, dx, dy = roll, 0, 0
        for k, (sx, sy) in enumerate(((122, 24), (24, 22), (140, 62), (30, 66))):
            if (i + k) % 2 == 0:
                sparkle(cv, sx, sy, GOLD)
    die(cv, 64 + dx, 32 + dy, v, 32)
    _title(cv, "DICE", 3, 2)
    return cv


# ---------------- slots ----------------
def _cherry(cv, x, y):
    cv.line([(x + 6, y), (x + 3, y + 7)], (40, 120, 40), 1)
    cv.line([(x + 6, y), (x + 9, y + 7)], (40, 120, 40), 1)
    cv.ell(x, y + 6, 6, 6, (210, 30, 50), (120, 10, 20))
    cv.ell(x + 7, y + 6, 6, 6, (210, 30, 50), (120, 10, 20))
    cv.px(x + 2, y + 8, WHITE)
    cv.px(x + 9, y + 8, WHITE)


def _symbol(cv, k, x, y):
    """k = SLOT_SYMBOLS-ийн дугаар: 0 интоор, 1 нимбэг, 2 усан үзэм, 3 хонх, 4 алмаз, 5 долоо."""
    if k == 5:
        cv.ctext(x + 10, y + 9, "7", (210, 30, 40), 3, shadow=(100, 10, 20))
    elif k == 0:
        _cherry(cv, x + 3, y + 8)
    elif k == 1:
        cv.ell(x + 2, y + 9, 16, 11, (250, 224, 60), (170, 130, 10))
        cv.rect(x + 17, y + 13, 2, 3, (250, 224, 60))
        cv.px(x + 6, y + 12, (255, 250, 190))
        cv.rect(x + 9, y + 7, 3, 3, (60, 150, 50))
    elif k == 2:
        cv.rect(x + 9, y + 3, 2, 4, (60, 150, 50))
        for dx, dy in ((3, 7), (8, 7), (13, 7), (5, 12), (10, 12), (8, 17)):
            cv.ell(x + dx, y + dy, 5, 5, (150, 56, 200), (80, 20, 120))
    elif k == 3:
        cv.poly([(x + 10, y + 5), (x + 15, y + 10), (x + 17, y + 19), (x + 3, y + 19), (x + 5, y + 10)], (244, 196, 48))
        cv.rect(x + 2, y + 19, 16, 2, (200, 140, 20))
        cv.ell(x + 8, y + 21, 4, 3, (150, 100, 10))
        cv.px(x + 7, y + 11, (255, 240, 170))
    else:
        cv.poly([(x + 10, y + 6), (x + 17, y + 14), (x + 10, y + 22), (x + 3, y + 14)], (60, 220, 240))
        cv.poly([(x + 10, y + 6), (x + 17, y + 14), (x + 10, y + 14)], (170, 250, 255))


def slots(i, n, reels=(5, 5, 5)):
    cv = Canvas()
    cv.gradient((30, 14, 60), (12, 6, 30), bands=8)
    cv.stars(30, 11)
    cv.box(36, 4, 88, 72, (190, 28, 44), (90, 8, 20))
    cv.rect(38, 6, 84, 3, (240, 90, 100))
    cv.box(44, 10, 72, 11, (30, 14, 40), GOLD)
    cv.ctext(80, 13, "SLOTS", GOLD, 1)
    stops = (n - 12, n - 7, n - 3)
    won = i >= stops[-1]
    for k in range(10):
        on = (k + i) % 2 == 0 if not won else (i % 2 == 0)
        cv.ell(46 + k * 7, 22, 4, 4, (255, 240, 140) if on else (150, 110, 30))
    cv.box(44, 28, 72, 34, (12, 10, 22), (230, 200, 90))
    for r in range(3):
        x = 47 + r * 23
        sub = Canvas(20, 28, (250, 248, 240))
        if i >= stops[r]:
            off = 0
        else:
            off = (i * 9 + r * 14) % (6 * 28)
        for cell in range(-1, 7):
            yy = cell * 28 - off
            if -28 < yy < 28:
                _symbol(sub, (cell + reels[r]) % 6, 0, yy)
        if i < stops[r]:  # хурдтай эргэхэд бүдгэрсэн зураас
            for ly in range(0, 28, 4):
                sub.px((ly * 3 + i) % 20, ly, (225, 222, 214))
        cv.im.paste(sub.im, (x, 31))
        cv.d.rectangle([x - 1, 30, x + 20, 59], outline=(120, 110, 100))
    cv.rect(44, 64, 72, 8, (120, 16, 30))
    for k in range(3):
        cv.ell(66 + k * 12, 66, 5, 5, GOLD if (won or (i // 2 + k) % 2) else (150, 110, 30))
    lever = 0 if i % 8 > 2 else 6
    cv.rect(125, 26 + lever, 3, 24 - lever, (170, 170, 180))
    cv.ell(122, 18 + lever, 9, 9, (230, 40, 50), (120, 10, 20))
    if won:
        for k, (sx, sy) in enumerate(((20, 20), (140, 60), (20, 60), (142, 22), (80, 74))):
            if (i + k) % 3 == 0:
                sparkle(cv, sx, sy, GOLD)
    return cv


# ---------------- minefield ----------------
def minefield(i, n):
    cv = Canvas()
    cv.gradient((34, 36, 44), (16, 18, 24), bands=8)
    gx, gy = 28, 16
    seq = [(0, 2), (1, 1), (2, 3), (0, 4), (1, 0), (2, 1), (0, 0), (2, 5)]
    bomb = (1, 3)
    steps = i // 2
    opened = set(seq[:min(steps, len(seq))])
    boom = steps > len(seq)
    for r in range(3):
        for c in range(6):
            x, y = gx + c * 21, gy + r * 19
            if (r, c) in opened:
                cv.box(x, y, 19, 17, (22, 24, 30), (60, 64, 76))
                cv.poly([(x + 9, y + 3), (x + 15, y + 8), (x + 9, y + 14), (x + 3, y + 8)], (60, 220, 240))
                cv.poly([(x + 9, y + 3), (x + 15, y + 8), (x + 9, y + 8)], (170, 250, 255))
                if (i + r + c) % 5 == 0:
                    sparkle(cv, x + 14, y + 3, WHITE)
            elif (r, c) == bomb and boom:
                cv.box(x, y, 19, 17, (22, 24, 30), (60, 64, 76))
                cv.ell(x + 4, y + 5, 11, 11, (20, 20, 24), (90, 90, 100))
                cv.px(x + 6, y + 7, WHITE)
                cv.line([(x + 12, y + 6), (x + 15, y + 2)], (200, 170, 110))
                if i % 2:
                    cv.poly([(x + 9, y - 6), (x + 12, y + 1), (x + 20, y + 3), (x + 13, y + 6), (x + 15, y + 15), (x + 9, y + 9),
                             (x + 3, y + 15), (x + 5, y + 6), (x - 2, y + 3), (x + 6, y + 1)], (255, 190, 60))
                    cv.ell(x + 5, y + 2, 9, 9, (255, 240, 150))
                else:
                    sparkle(cv, x + 16, y + 2, (255, 190, 60))
            else:
                press = (steps < len(seq) and (r, c) == seq[steps] and i % 2)
                cv.box(x, y, 19, 17, (80, 86, 98) if press else (110, 118, 132), (60, 64, 76))
                if not press:
                    cv.rect(x + 1, y + 1, 17, 2, (160, 168, 182))
                    cv.rect(x + 1, y + 14, 17, 2, (80, 86, 98))
    _title(cv, "MINEFIELD", 0, 1, (255, 150, 90))
    return cv


# ---------------- duel / draw ----------------
def _cowboy(cv, x, y, face_right, hat, vest):
    d = 1 if face_right else -1
    cv.rect(x - 3, y + 16, 3, 10, (50, 40, 36)); cv.rect(x + 1, y + 16, 3, 10, (50, 40, 36))
    cv.rect(x - 3, y + 25, 4, 2, (30, 20, 16)); cv.rect(x + 1, y + 25, 4, 2, (30, 20, 16))
    cv.rect(x - 5, y + 6, 10, 11, vest)
    cv.rect(x - 1, y + 6, 2, 11, shade(vest, 0.7))
    cv.rect(x - 3, y, 6, 6, (232, 186, 144))
    cv.rect(x - 6, y - 1, 12, 2, hat); cv.rect(x - 3, y - 4, 6, 4, hat)
    ax = x + d * 5
    cv.rect(ax if d > 0 else ax - 8, y + 9, 8, 2, (232, 186, 144))
    gx = x + d * 12 if d > 0 else x - 16
    cv.rect(gx, y + 7, 5, 3, (40, 40, 48)); cv.rect(gx + (3 if d > 0 else 0), y + 9, 2, 3, (40, 40, 48))
    return (gx + (5 if d > 0 else -1), y + 8)  # амсрын цэг


def _burst(cv, x, y, r=7):
    pts = []
    for k in range(10):
        a = k * math.pi / 5
        rr = r if k % 2 == 0 else r // 2
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    cv.poly(pts, (255, 190, 60))
    cv.ell(x - r // 2, y - r // 2, r, r, (255, 244, 170))


def duel(i, n, title="DUEL", flash=False):
    cv = Canvas()
    cv.gradient((250, 120, 60), (120, 40, 110), bands=10, y1=48)
    cv.ell(60, 34, 40, 40, (255, 210, 110))
    cv.ell(66, 40, 28, 28, (255, 240, 170))
    cv.rect(0, 48, 160, 32, (150, 80, 50))
    cv.rect(0, 48, 160, 2, (190, 110, 70))
    for x, h in ((12, 20), (146, 24)):
        cv.rect(x, 48 - h + 12, 3, h, (40, 90, 50))
        cv.rect(x - 3, 48 - h + 18, 3, 7, (40, 90, 50)); cv.rect(x + 3, 48 - h + 15, 3, 7, (40, 90, 50))
    for k in range(10):
        cv.px(6 + k * 16, 60 + (k * 5) % 12, (120, 60, 38))
    # өвс бөмбөрнө
    tx = (i * 11) % 190 - 15
    ty = 58 + int(abs(math.sin(i * 0.8)) * -5)
    cv.ell(tx, ty, 9, 9, (150, 110, 60), (100, 70, 30))
    cv.line([(tx + 1, ty + 4), (tx + 8, ty + 4)], (100, 70, 30)); cv.line([(tx + 4, ty + 1), (tx + 4, ty + 8)], (100, 70, 30))
    bob = 1 if (i // 3) % 2 else 0
    m1 = _cowboy(cv, 42, 34 + bob, True, (80, 50, 30), (180, 40, 40))
    m2 = _cowboy(cv, 118, 34 + bob, False, (40, 40, 56), (40, 90, 170))
    shot = i >= n - 5
    if shot and i < n - 2:
        _burst(cv, m1[0] + 3, m1[1], 9)
        _burst(cv, m2[0] - 3, m2[1], 9)
        cv.ctext(80, 30, "BANG!", (255, 250, 200), 2, shadow=(120, 20, 20))
    elif i >= n - 2:
        for k in range(3):
            cv.ell(m1[0] + 2 + k * 3, m1[1] - 4 - k * 3, 5 + k, 4 + k, (225, 225, 230))
            cv.ell(m2[0] - 6 - k * 3, m2[1] - 4 - k * 3, 5 + k, 4 + k, (225, 225, 230))
    _title(cv, title, 3, 2, WHITE)
    return cv


# ---------------- dately ----------------
def _heart(cv, x, y, c, s=1):
    cv.suit(x, y, "heart", c, s)


def dately(i, n):
    cv = Canvas()
    cv.gradient((255, 150, 190), (150, 70, 160), bands=10)
    r = random.Random(8)
    for k in range(18):
        x0 = r.randrange(4, 150)
        y0 = r.randrange(0, 80)
        y = (y0 - i * (2 + k % 3)) % 88 - 8
        _heart(cv, x0, y, (255, 220, 235), 1)
    cv.box(58, 6, 44, 70, (30, 24, 44), (14, 10, 22))
    cv.box(61, 10, 38, 62, (255, 232, 242))
    cv.rect(72, 7, 16, 2, (60, 54, 80))
    cv.ell(65, 16, 14, 14, (210, 150, 130), (120, 70, 60)); cv.rect(65, 12, 14, 7, (60, 36, 28))
    cv.ell(81, 16, 14, 14, (232, 190, 150), (120, 70, 60)); cv.rect(81, 12, 14, 6, (28, 24, 34))
    big = (i // 2) % 2
    if big:
        _heart(cv, 72, 33, (230, 40, 90), 3)
    else:
        _heart(cv, 74, 34, (230, 40, 90), 2)
    ok_on = (i // 4) % 2 == 0
    cv.box(65, 52, 14, 9, (60, 190, 100) if ok_on else (40, 110, 70), (20, 100, 50)); cv.ctext(72, 54, "OK", WHITE)
    cv.box(81, 52, 14, 9, (230, 70, 80) if not ok_on else (140, 50, 56), (130, 20, 30)); cv.ctext(88, 54, "NO", WHITE)
    # мессеж бөмбөлөг ээлжлэн гарна
    if ok_on:
        cv.box(8, 22, 38, 12, (255, 255, 255), (150, 70, 160)); cv.ctext(21, 26, "OK", (200, 30, 90)); _heart(cv, 31, 25, (230, 40, 90), 1)
    else:
        cv.box(114, 40, 38, 12, (255, 255, 255), (150, 70, 160)); cv.ctext(133, 44, "NAHH", (120, 40, 160))
    return cv


# ---------------- үр дүнгийн banner (WIN / LOST) ----------------
def money_short(n: int) -> str:
    n = int(abs(n))
    for lim, suf in ((10 ** 9, "B"), (10 ** 6, "M"), (10 ** 3, "K")):
        if n >= lim:
            v = f"{n / lim:.2f}".rstrip("0").rstrip(".")
            return v + suf
    return str(n)


def _banner(base: Image.Image, outcome: str, amount: int, detail: str, sp: int = 0) -> Image.Image:
    dark = Image.blend(base, Image.new("RGB", base.size, (0, 0, 0)), 0.58)
    cv = Canvas(base.size[0], base.size[1])
    cv.im.paste(dark)
    col, edge, txt = {
        "win": ((120, 255, 160), (30, 150, 80), "WIN"),
        "lost": ((255, 90, 90), (170, 30, 40), "LOST"),
        "push": ((220, 220, 230), (120, 120, 140), "PUSH"),
    }[outcome]
    cv.box(18, 12, 124, 56, (14, 14, 22), edge)
    cv.ctext(80, 17, txt, col, 4, shadow=(0, 0, 0))
    if outcome == "win":
        amt = "+" + money_short(amount)
    elif outcome == "lost":
        amt = "-" + money_short(amount)
    else:
        amt = "BET BACK"
    cv.ctext(80, 41, amt, (255, 235, 140) if outcome == "win" else col, 2, shadow=(0, 0, 0))
    if detail:
        cv.ctext(80, 58, detail[:28], (190, 190, 205), 1)
    if outcome == "win":
        for k, (qx, qy) in enumerate(((10, 10), (150, 12), (12, 66), (148, 68), (80, 6))):
            if (sp + k) % 2:
                sparkle(cv, qx, qy, GOLD)
    return cv.im


def play_gif(kind: str, outcome: str | None = None, amount: int = 0, detail: str = "", hold: int = 1600, **kw) -> bytes:
    """Бодит үр дүнтэй GIF: тоглоомын хөдөлгөөн + төгсгөлд WIN/LOST banner."""
    fn, n, ms = SCENES[kind]
    ims = [fn(i, n, **kw).im for i in range(n)]
    durs = [ms] * n
    if outcome:
        for sp in range(2):
            ims.append(_banner(ims[-1 - sp] if sp == 0 else ims[n - 1], outcome, amount, detail, sp))
            durs.append(hold)
    return encode_gif(ims, durs)


def play_len(kind: str) -> float:
    """Banner гарахаас өмнөх хөдөлгөөний үргэлжлэх хугацаа (секунд)."""
    _, n, ms = SCENES[kind]
    return n * ms / 1000


# ---------------- blackjack ширээ (бодит хөзрөөр) ----------------
_SUIT_NAME = {"♠": "spade", "♥": "heart", "♦": "diamond", "♣": "club"}


def _bj_card(cv, x, y, c, w=22, h=30):
    rank, suit = c
    card(cv, x, y, rank, _SUIT_NAME[suit], suit in ("♥", "♦"), w, h)


def _bj_back(cv, x, y, w=22, h=30):
    cv.box(x, y, w, h, (40, 70, 160), (230, 230, 240))
    for yy in range(y + 3, y + h - 3, 3):
        for xx in range(x + 3 + ((yy - y) // 3 % 2) * 2, x + w - 3, 4):
            cv.px(xx, yy, (130, 160, 230))


def blackjack_table(i, n, player, dealer, pv, dv, hide, new):
    cv = Canvas()
    _felt(cv)
    cv.ctext(20, 4, "DEALER", (200, 230, 210), 1)
    cv.ctext(20, 13, "?" if hide else (str(dv) if dv <= 21 else "BUST"), WHITE if dv <= 21 or hide else (255, 90, 90), 2, shadow=(0, 20, 10))
    cv.ctext(20, 46, "YOU", (200, 230, 210), 1)
    cv.ctext(20, 55, str(pv) if pv <= 21 else "BUST", WHITE if pv <= 21 else (255, 90, 90), 2, shadow=(0, 20, 10))
    for k, c in enumerate(dealer):
        x = 44 + k * 18
        if k == 1 and hide:
            _bj_back(cv, x, 6)
        else:
            _bj_card(cv, x, 6, c)
    for k, c in enumerate(player):
        x = 44 + k * 18
        if new and k == len(player) - 1:
            t = _ease(i / (n - 2))
            x = int(170 + (x - 170) * t)
        _bj_card(cv, x, 44, c)
    chips(cv, 140, 76, (200, 30, 40), 3)
    chips(cv, 152, 74, GOLD, 3)
    return cv


def blackjack_gif(player, dealer, pv, dv, hide, new=False, outcome=None, amount=0, detail="") -> bytes:
    n = 6 if new else 2
    ims = [blackjack_table(i, n, player, dealer, pv, dv, hide, new).im for i in range(n)]
    durs = [70] * n if new else [400] * n
    if outcome:
        for sp in range(2):
            ims.append(_banner(ims[n - 1], outcome, amount, detail, sp))
            durs.append(1600)
    return encode_gif(ims, durs)


SCENES = {
    "roulette": (roulette, 36, 80), "blackjack": (blackjack, 18, 90),
    "horse": (horse_race, 36, 90), "coinflip": (coinflip, 22, 70), "dice": (dice, 20, 90),
    "slots": (slots, 30, 80), "minefield": (minefield, 22, 110),
    "duel": (lambda i, n, **kw: duel(i, n, "DUEL"), 18, 110),
    "draw": (lambda i, n, **kw: duel(i, n, "QUICK DRAW", True), 18, 110),
    "dately": (dately, 16, 100),
}
KINDS = list(SCENES)


def art_bytes(kind: str) -> bytes:
    if kind not in _cache:
        fn, n, ms = SCENES[kind]
        frames = [fn(i, n).im for i in range(n)]
        _cache[kind] = encode_gif(frames, ms)
    return _cache[kind]


def warm():
    """Бүх GIF-ийг урьдчилан үүсгэнэ (асаахад нэг удаа, thread дотор дуудна)."""
    for k in KINDS:
        art_bytes(k)


def art_file(kind: str) -> discord.File:
    return discord.File(io.BytesIO(art_bytes(kind)), filename=f"{kind}.gif")


def stamp(embed: discord.Embed, kind: str) -> discord.Embed:
    embed.set_image(url=f"attachment://{kind}.gif")
    return embed
