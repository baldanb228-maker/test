"""Pixel-art chibi дүр (кодоор зурсан). 4 фрэймтэй алхалтын GIF + тэжээвэр амьтан."""
import io

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from petart import render_pet

LW, LH = 46, 110  # логик (pixel) хэмжээ: 8 толгойн realistic пропорц
SCALE = 5
DEFAULT_OUTFIT = {"top": ("tee", "#9ca3af"), "bottom": ("pants", "#374151"), "shoes": ("sneaker", "#e5e7eb")}


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def _sh(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))), 255)


class Cv:
    def __init__(self):
        self.im = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def r(self, x, y, w, h, c):
        if w > 0 and h > 0:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)

    def p(self, x, y, c):
        self.d.point((x, y), fill=c)


HAIR = {"male": "#2b1b12", "female": "#3a2314"}

# ---------- үсний засалт (16 хэв маяг) ----------
HAIR_STYLES = [  # (түлхүүр, нэр, emoji)
    ("default", "Ердийн", "🙂"), ("buzz", "Богино", "💈"), ("side", "Хажуу сугалсан", "😎"),
    ("long", "Урт шулуун", "👩"), ("pigtails", "Хоёр гэзэг", "👧"), ("ponytail", "Нэг гэзэг", "🐴"),
    ("mohawk", "Хуйх (Mohawk)", "🦜"), ("afro", "Афро", "🧑‍🦱"), ("bun", "Зангилаа", "🍙"),
    ("bob", "Каре (Bob)", "💁"), ("spiky", "Сэртэгнэсэн", "⚡"), ("curly", "Буржгар", "🌀"),
    ("bald", "Халзан", "🥚"), ("middle", "Голоор нь хуваасан", "🧖"), ("braids", "Монгол сүлд", "🎀"),
    ("undercut", "Андеркат", "✂️"), ("bangs", "Хүйтэн хөмсөг (Bangs)", "🌸"),
]
HAIR_COLORS = [  # (түлхүүр, нэр, hex)
    ("black", "Хар", "#1a1a1d"), ("darkbrown", "Бараан хүрэн", "#2b1b12"), ("brown", "Хүрэн", "#5a3825"),
    ("chestnut", "Туулайн хүрэн", "#7a4a2a"), ("blonde", "Шар", "#d6b25e"), ("platinum", "Цагаавтар", "#e8e0c8"),
    ("red", "Улаан", "#b3402a"), ("ginger", "Улбар шар", "#c8662b"), ("pink", "Ягаан", "#e879a8"),
    ("blue", "Цэнхэр", "#3b82f6"), ("purple", "Нил ягаан", "#8b5cf6"), ("green", "Ногоон", "#22c55e"),
    ("white", "Цагаан", "#f3f4f6"), ("teal", "Номин", "#14b8a6"),
]
HAIR_HEX = {k: h for k, _, h in HAIR_COLORS}

# ---------- Makeup ----------
MAKEUP_LIPS = [  # (түлхүүр, нэр, hex)
    ("red", "Улаан", "#d1243a"), ("pink", "Ягаан", "#ec6fa0"), ("nude", "Нүцгэн (nude)", "#c98a7a"),
    ("berry", "Нэрс", "#8e2a5a"), ("coral", "Шүрэн", "#f0725c"), ("purple", "Нил ягаан", "#7a3bb0"),
    ("black", "Хар", "#26202c"), ("gold", "Алт", "#e2b53c"),
]
MAKEUP_EYES = [
    ("blue", "Цэнхэр", "#3b82f6"), ("purple", "Нил ягаан", "#8b5cf6"), ("pink", "Ягаан", "#f472b6"),
    ("green", "Ногоон", "#22c55e"), ("gold", "Алт", "#eab308"), ("smoky", "Утаан (smoky)", "#4b5563"),
    ("teal", "Номин", "#14b8a6"), ("red", "Улаан", "#ef4444"),
]
MAKEUP_BLUSH = [
    ("peach", "Тоорын", "#f8a58b"), ("pink", "Ягаан", "#f472b6"), ("rose", "Сарнай", "#e11d6a"),
    ("red", "Улаан", "#dc2626"), ("purple", "Нил ягаан", "#a855f7"), ("coral", "Шүрэн", "#fb7185"),
]
MAKEUP_EXTRAS = [  # (түлхүүр, нэр, emoji)
    ("freckles", "Сорви (freckles)", "🟤"), ("mole", "Хар хэвлий (beauty mark)", "⚫"),
    ("liner", "Нүдний шугам (eyeliner)", "🖊️"), ("lashes", "Сормуус", "👁️"),
    ("star", "Одон гялгар (face gem)", "⭐"), ("warpaint", "Дайны будаг", "🔥"),
    ("tears", "Нулимсны дусал", "💧"),
]
MAKEUP_HEX = {
    "lips": {k: h for k, _, h in MAKEUP_LIPS},
    "eyes": {k: h for k, _, h in MAKEUP_EYES},
    "blush": {k: h for k, _, h in MAKEUP_BLUSH},
}


def parse_makeup(text):
    """'lips:red|eyes:blue|blush:pink|extra:freckles,liner' -> dict. Хоосон бол {}."""
    out = {}
    for part in (text or "").split("|"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        if k == "extra":
            out[k] = [x for x in v.split(",") if x in {e[0] for e in MAKEUP_EXTRAS}]
        elif k in MAKEUP_HEX and v in MAKEUP_HEX[k]:
            out[k] = v
    if not out.get("extra"):
        out.pop("extra", None)
    return out


def dump_makeup(mk: dict) -> str:
    parts = [f"{k}:{mk[k]}" for k in ("lips", "eyes", "blush") if mk.get(k)]
    if mk.get("extra"):
        parts.append("extra:" + ",".join(mk["extra"]))
    return "|".join(parts)


def _mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)


def _px_rows(cv, rows, c):
    """rows: [(y, x0, x1_inclusive)]"""
    for y, x0, x1 in rows:
        if x1 >= x0:
            cv.r(x0, y, x1 - x0 + 1, 1, c)


def _lerp_profile(pts, y):
    """pts: [(y, a, b)] → (a, b) шугаман интерполяц."""
    if y <= pts[0][0]:
        return pts[0][1], pts[0][2]
    for (y0, a0, b0), (y1, a1, b1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / max(1, y1 - y0)
            return round(a0 + (a1 - a0) * t), round(b0 + (b1 - b0) * t)
    return pts[-1][1], pts[-1][2]


# ---- 8 толгойн realistic пропорц (толгой = 12px) ----
# y нь толгойн дээд ирмэгээс хойших зай: толгой 0-11, хүзүү 12-13, мөр 14, хөх 24, хүйс 36, өвдөг 70, шагай 90, улны ёроол 95
# (цээжний хагас өргөн) ; эрэгтэй / эмэгтэй
TORSO_M = [(14, 7), (16, 9), (22, 9), (26, 8), (34, 7), (40, 7), (46, 8)]
TORSO_F = [(14, 6), (16, 7), (22, 7), (26, 7), (34, 5), (40, 6), (46, 8)]
# хөл: (y, гадна, дотор) cx-ээс хэмжсэн зай
LEG_M = [(46, 8, 0), (56, 8, 1), (64, 8, 1), (70, 7, 1), (78, 7, 2), (86, 6, 2), (91, 5, 2)]
LEG_F = [(46, 8, 0), (56, 8, 1), (64, 7, 1), (70, 6, 1), (78, 6, 2), (86, 5, 2), (91, 4, 2)]


def _half(prof, y):
    if y <= prof[0][0]:
        return prof[0][1]
    for (y0, a), (y1, b) in zip(prof, prof[1:]):
        if y0 <= y <= y1:
            return round(a + (b - a) * (y - y0) / max(1, y1 - y0))
    return prof[-1][1]


def _makeup(cv, mk, hx, oy, skin):
    """Нүүрний будалт (толгой 10x12: нүд y+5, хамар y+7, ам y+9)."""
    if not mk:
        return
    lips, eyes, blush = mk.get("lips"), mk.get("eyes"), mk.get("blush")
    extra = mk.get("extra") or []
    ink = (20, 16, 28, 255)
    if blush:
        c = _mix(skin, _rgb(MAKEUP_HEX["blush"][blush]), 0.75)
        cv.r(hx + 1, oy + 7, 2, 2, c)
        cv.r(hx + 7, oy + 7, 2, 2, c)
    if eyes:
        c = _rgb(MAKEUP_HEX["eyes"][eyes])
        for ex in (hx + 2, hx + 6):
            cv.r(ex, oy + 4, 2, 1, c)
            cv.r(ex, oy + 6, 2, 1, _sh(c, 0.8))
    if "liner" in extra:
        for ex in (hx + 2, hx + 6):
            cv.r(ex, oy + 5, 2, 1, ink)
        cv.p(hx + 1, oy + 4, ink)
        cv.p(hx + 8, oy + 4, ink)
    if "lashes" in extra:
        cv.p(hx + 1, oy + 5, ink)
        cv.p(hx + 8, oy + 5, ink)
        cv.p(hx + 2, oy + 4, ink)
        cv.p(hx + 7, oy + 4, ink)
    if "freckles" in extra:
        fc = _sh(skin, 0.7)
        for fx, fy in ((hx + 2, oy + 7), (hx + 3, oy + 8), (hx + 6, oy + 8), (hx + 7, oy + 7), (hx + 1, oy + 8), (hx + 8, oy + 8)):
            cv.p(fx, fy, fc)
    if "mole" in extra:
        cv.p(hx + 7, oy + 9, (40, 24, 20, 255))
    if "star" in extra:
        cv.p(hx + 8, oy + 6, (255, 236, 120, 255))
        cv.p(hx + 8, oy + 5, (255, 255, 255, 255))
    if "warpaint" in extra:
        red = (200, 30, 40, 255)
        cv.r(hx, oy + 7, 3, 1, red)
        cv.r(hx, oy + 9, 3, 1, red)
        cv.r(hx + 7, oy + 7, 3, 1, red)
        cv.r(hx + 7, oy + 9, 3, 1, red)
    if "tears" in extra:
        cv.p(hx + 2, oy + 7, (120, 200, 255, 255))
        cv.p(hx + 2, oy + 8, (190, 230, 255, 255))
        cv.p(hx + 7, oy + 7, (120, 200, 255, 255))
    if lips:
        c = _rgb(MAKEUP_HEX["lips"][lips])
        cv.r(hx + 3, oy + 9, 4, 1, c)
        cv.r(hx + 4, oy + 10, 2, 1, _sh(c, 0.8))
        cv.p(hx + 4, oy + 9, _sh(c, 1.3))


def _cap(cv, hx, oy, h, hl, rows=3):
    """Толгойн оройн үс (хоёр талдаа)."""
    cv.r(hx + 2, oy - 1, 6, 1, hl)
    cv.r(hx + 1, oy, 8, 1, h)
    cv.r(hx, oy + 1, 10, rows - 1, h)


def _hair_back(cv, style, hx, oy, hair):
    """Бие, нүүрнээс ХАМГИЙН ЭХЭНД (ард) зурагдах үс."""
    if style == "long":
        cv.r(hx - 1, oy + 2, 12, 24, hair)
        cv.r(hx - 1, oy + 25, 12, 1, _sh(hair, 0.8))
    elif style == "bob":
        cv.r(hx - 1, oy + 2, 12, 11, hair)
    elif style == "afro":
        cv.r(hx - 3, oy - 5, 16, 14, hair)
        cv.r(hx - 2, oy + 8, 14, 2, hair)
    elif style == "braids":
        cv.r(hx - 1, oy + 2, 12, 9, hair)
    elif style == "bangs":
        cv.r(hx - 1, oy + 2, 12, 17, hair)
    elif style == "middle":
        cv.r(hx - 1, oy + 2, 12, 12, hair)
    elif style in (None, "default"):
        pass


def _hair_front(cv, style, hx, oy, hair, skin, fem):
    """Нүүр зурагдсаны дараа дээр нь зурагдах үс."""
    hl = _sh(hair, 1.4)
    dk = _sh(hair, 0.75)
    red = (230, 60, 90, 255)
    if style is None:
        _cap(cv, hx, oy, hair, hl)
        if fem:
            cv.r(hx - 1, oy + 3, 2, 18, hair)
            cv.r(hx + 9, oy + 3, 2, 18, hair)
            cv.r(hx - 1, oy + 2, 12, 1, hair)
            cv.r(hx + 2, oy + 3, 3, 1, hair)
            cv.r(hx + 6, oy + 3, 2, 1, hair)
            cv.r(hx - 2, oy + 5, 12 + 4, 16, hair) if False else None
            cv.r(hx - 2, oy + 4, 14, 15, hair) if False else None
            # ард үс (эмэгтэй анхдагч): мөрөн дээр хүртэл
            cv.r(hx - 1, oy + 12, 12, 8, hair)
        else:
            cv.r(hx, oy + 3, 1, 3, hair)
            cv.r(hx + 9, oy + 3, 1, 3, hair)
            cv.r(hx + 1, oy + 3, 3, 1, hair)
            cv.r(hx + 6, oy + 3, 3, 1, hair)
    elif style == "buzz":
        cv.r(hx + 1, oy, 8, 1, dk)
        cv.r(hx, oy + 1, 10, 2, dk)
        cv.r(hx + 2, oy - 1, 6, 1, hair)
    elif style == "side":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx, oy + 3, 6, 2, hair)
        cv.r(hx, oy + 3, 2, 5, hair)
        cv.r(hx + 9, oy + 3, 1, 3, hair)
    elif style == "long":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx - 1, oy + 3, 2, 20, hair)
        cv.r(hx + 9, oy + 3, 2, 20, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
    elif style == "pigtails":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx, oy + 3, 2, 3, hair); cv.r(hx + 8, oy + 3, 2, 3, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
        for tx in (hx - 4, hx + 10):
            cv.r(tx, oy + 4, 4, 18, hair)
            cv.r(tx, oy + 4, 4, 1, red)
    elif style == "ponytail":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx, oy + 3, 1, 3, hair); cv.r(hx + 9, oy + 3, 1, 3, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
        cv.r(hx + 10, oy + 1, 3, 3, hair)
        cv.r(hx + 11, oy + 4, 3, 20, hair)
        cv.r(hx + 10, oy + 2, 3, 1, red)
    elif style == "mohawk":
        cv.r(hx + 1, oy + 1, 8, 2, dk)
        cv.r(hx + 4, oy - 7, 2, 9, hair)
        cv.r(hx + 3, oy - 3, 4, 5, hair)
        cv.r(hx + 4, oy - 7, 2, 1, hl)
    elif style == "afro":
        cv.r(hx - 3, oy - 5, 16, 9, hair)
        cv.r(hx - 3, oy - 5, 16, 1, hl)
        cv.r(hx - 3, oy + 3, 3, 6, hair); cv.r(hx + 10, oy + 3, 3, 6, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
        for xx in range(hx - 2, hx + 12, 3):
            cv.p(xx, oy - 3, dk); cv.p(xx + 1, oy, dk)
    elif style == "bun":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx, oy + 3, 1, 2, hair); cv.r(hx + 9, oy + 3, 1, 2, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
        cv.r(hx + 3, oy - 6, 4, 5, hair)
        cv.r(hx + 3, oy - 6, 4, 1, hl)
    elif style == "bob":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx - 1, oy + 3, 2, 9, hair)
        cv.r(hx + 9, oy + 3, 2, 9, hair)
        cv.r(hx + 1, oy + 3, 8, 2, hair)
    elif style == "spiky":
        cv.r(hx, oy + 1, 10, 2, hair)
        for i in range(0, 10, 3):
            cv.r(hx + i, oy - 3 + (i // 3 % 2), 3, 4, hair)
            cv.p(hx + i + 1, oy - 3 + (i // 3 % 2), hl)
        cv.r(hx, oy + 3, 1, 3, hair); cv.r(hx + 9, oy + 3, 1, 3, hair)
    elif style == "curly":
        cv.r(hx - 1, oy - 2, 12, 6, hair)
        cv.r(hx - 1, oy + 3, 2, 6, hair); cv.r(hx + 9, oy + 3, 2, 6, hair)
        for xx in range(hx, hx + 10, 2):
            cv.p(xx, oy - 1, hl); cv.p(xx + 1, oy + 2, dk)
    elif style == "bald":
        cv.r(hx + 2, oy + 1, 2, 1, _sh(skin, 1.25))
    elif style == "middle":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx - 1, oy + 3, 2, 11, hair); cv.r(hx + 9, oy + 3, 2, 11, hair)
        cv.r(hx + 4, oy, 2, 3, dk)
        cv.r(hx + 1, oy + 3, 3, 1, hair); cv.r(hx + 6, oy + 3, 3, 1, hair)
    elif style == "braids":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx, oy + 3, 1, 3, hair); cv.r(hx + 9, oy + 3, 1, 3, hair)
        cv.r(hx + 1, oy + 3, 8, 1, hair)
        for bxx in (hx - 3, hx + 10):
            cv.r(bxx, oy + 4, 3, 28, hair)
            for yy in range(oy + 5, oy + 32, 3):
                cv.r(bxx, yy, 3, 1, dk)
            cv.r(bxx, oy + 32, 3, 1, (250, 204, 21, 255))
    elif style == "undercut":
        cv.r(hx + 1, oy - 2, 8, 4, hair)
        cv.r(hx + 1, oy - 2, 8, 1, hl)
        cv.r(hx, oy + 2, 10, 2, _sh(hair, 0.6))
    elif style == "bangs":
        _cap(cv, hx, oy, hair, hl)
        cv.r(hx - 1, oy + 3, 2, 14, hair); cv.r(hx + 9, oy + 3, 2, 14, hair)
        cv.r(hx + 1, oy + 3, 8, 2, hair)
        for xx in range(hx + 2, hx + 9, 2):
            cv.p(xx, oy + 5, hair)


def _skin_shadows(cv, skin):
    return _sh(skin, 0.82), _sh(skin, 0.68)


def _character(frame, gender, skin_hex, outfit, dead=False):
    """Нэг фрэймийн дүр: 8 толгойн realistic пропорц (outline-тай, logical хэмжээ)."""
    cv = Cv()
    skin = _rgb(skin_hex)
    sk1, sk2 = _skin_shadows(cv, skin)
    hair_style, hair_hex = outfit.get("hair", (None, None))
    hair_style = hair_style if hair_style and hair_style != "default" else None
    hair = _rgb(hair_hex if isinstance(hair_hex, str) else HAIR.get(gender, "#2b1b12"))
    fem = gender == "female"
    top_style, top_c = outfit.get("top", DEFAULT_OUTFIT["top"])
    bot_style, bot_c = outfit.get("bottom", DEFAULT_OUTFIT["bottom"])
    sh_style, sh_c = outfit.get("shoes", DEFAULT_OUTFIT["shoes"])
    top_c = _rgb(top_c) if isinstance(top_c, str) else top_c
    bot_c = _rgb(bot_c) if isinstance(bot_c, str) else bot_c
    sh_c = _rgb(sh_c) if isinstance(sh_c, str) else sh_c
    bob = 1 if frame in (1, 3) and not dead else 0
    lift = (1 if frame == 0 else 0, 1 if frame == 2 else 0) if not dead else (0, 0)  # (зүүн, баруун) хөл
    swing = {0: (1, -1), 1: (0, 0), 2: (-1, 1), 3: (0, 0)}[frame] if not dead else (0, 0)
    cx = LW // 2
    oy = 13 - bob
    hx = cx - 5
    torso = TORSO_F if fem else TORSO_M
    legp = LEG_F if fem else LEG_M
    ARM_W = 3 if fem else 4

    def T(y):  # торсын хагас өргөн (oy-ээс хойших y)
        return _half(torso, y)

    # ---- ард зурагдах үс ----
    _hair_back(cv, hair_style, hx, oy, hair)
    if hair_style is None and fem:
        cv.r(hx - 1, oy + 3, 12, 18, hair)

    # ---- хөл ----
    long_bottom = bot_style in ("pants", "jeans")
    bot_dk = _sh(bot_c, 0.78)
    for side in (0, 1):  # 0 зүүн, 1 баруун
        lf = lift[side]
        for y in range(46, 96):
            yy = min(y, 91)
            outer, inner = _lerp_profile(legp, yy)[0], _lerp_profile(legp, yy)[1]
            x0 = cx - outer if side == 0 else cx + inner
            x1 = cx - inner - 1 if side == 0 else cx + outer - 1
            dy = -lf if y >= 78 else 0
            if y > 91:
                break
            leg_c = skin
            if long_bottom:
                leg_c = bot_c
            elif bot_style == "shorts" and y <= 64:
                leg_c = bot_c
            cv.r(x0, oy + y + dy, x1 - x0 + 1, 1, leg_c)
            # сүүдэр
            edge_x = x0 if side == 1 else x1
            cv.p(edge_x if side == 1 else x1, oy + y + dy, _sh(leg_c, 0.85) if leg_c != skin else sk1)
        # өвдөг
        kx = (cx - 4 if side == 0 else cx + 2)
        if not long_bottom and not (bot_style == "skirt"):
            cv.r(kx, oy + 70 - lf * 0, 2, 1, sk1)
        # гутал
        outer, inner = _lerp_profile(legp, 91)
        x0 = cx - outer if side == 0 else cx + inner
        w = outer - inner
        by = oy + 92 - lf
        st = sh_style
        if st in ("boot", "mongolboot"):
            cv.r(x0 - 1, by - 12, w + 2, 12 + 3, sh_c)
            cv.r(x0 - 1, by - 12, w + 2, 1, _sh(sh_c, 1.3))
            cv.r(x0 - 1, by + 2, w + 3, 2, _sh(sh_c, 0.7))
            if st == "mongolboot":
                cv.p(x0 + (w + 1 if side else -2), by + 1, sh_c)
                cv.p(x0 + (w + 1 if side else -2), by, sh_c)
                cv.r(x0 - 1, by - 8, w + 2, 1, (250, 204, 21, 255))
        elif st == "sandal":
            cv.r(x0 - 1, by, w + 2, 4, skin)
            cv.r(x0 - 1, by + 3, w + 2, 1, sh_c)
            cv.r(x0, by + 1, w, 1, sh_c)
        elif st == "dress":
            cv.r(x0 - 1, by, w + 3, 4, _sh(sh_c, 0.8))
            cv.r(x0 - 1, by, w + 3, 1, _sh(sh_c, 1.5))
            cv.r(x0 - 1, by + 3, w + 3, 1, _sh(sh_c, 0.5))
        else:  # sneaker
            cv.r(x0 - 1, by - 1, w + 3, 5, sh_c)
            cv.r(x0 - 1, by + 3, w + 3, 1, (245, 245, 245, 255) if sum(sh_c[:3]) < 650 else (150, 150, 160, 255))
            cv.r(x0 + 1, by, 2, 1, _sh(sh_c, 1.35))

    # ---- гар (хөдөлгөөнтэй) ----
    sleeves_long = top_style in ("hoodie", "shirt", "jacket", "sweater", "coat", "deel", "suit")
    sleeveless = top_style == "dress"
    sleeve_end = 28 if not sleeves_long else 49
    arm_hi = _sh(top_c, 1.15)
    for side, sw in ((0, swing[0]), (1, swing[1])):
        sx = cx - T(18) - ARM_W + 1 if side == 0 else cx + T(18) - 1
        # дээд гар
        cv.r(sx, oy + 15, ARM_W, 22, skin)
        # шуу ба бугуй
        fw = ARM_W - 1
        fx = sx if side == 0 else sx + 1
        cv.r(fx, oy + 37, fw, 12 + sw, skin)
        # гар
        hx_ = fx
        cv.r(hx_, oy + 49 + sw, fw, 6, skin)
        cv.r(hx_ + (0 if side == 0 else fw - 1), oy + 49 + sw, 1, 6, sk1)
        cv.r(hx_, oy + 54 + sw, fw, 1, sk1)
        # тохойн сүүдэр
        cv.p(fx + (0 if side == 1 else fw - 1), oy + 36, sk1)
        # ханцуй
        if not sleeveless:
            ey = sleeve_end + (sw if sleeves_long else 0)
            cv.r(sx, oy + 15, ARM_W, min(ey, 37) - 15, top_c)
            if ey > 37:
                cv.r(fx, oy + 37, fw, ey - 37, top_c)
            cv.r(sx if side == 1 else sx + ARM_W - 1, oy + 16, 1, min(ey, 37) - 16, _sh(top_c, 0.8))
            cv.r(sx, oy + ey - 1 if ey <= 37 else oy + ey - 1, ARM_W if ey <= 37 else fw, 1, _sh(top_c, 0.7))
            cv.r(sx, oy + 15, ARM_W, 1, arm_hi)
            if top_style == "sweater":
                for yy in range(17, ey, 3):
                    cv.r(sx, oy + yy, ARM_W if yy <= 37 else fw, 1, _sh(top_c, 0.88))
        else:
            cv.r(sx + (0 if side == 0 else 0), oy + 15, ARM_W, 3, skin)
        # зөөлөн сүүдэр
        cv.r(sx if side == 0 else sx + ARM_W - 1, oy + 38, 1, 10, sk1) if not sleeves_long else None

    # ---- бие ----
    skin_top = skin  # хүзүү, цээж
    hem = {"tee": 45, "hoodie": 47, "shirt": 47, "jacket": 50, "sweater": 46, "coat": 74, "deel": 86, "suit": 52, "dress": 70}.get(top_style, 45)
    # хүзүү
    cv.r(cx - 2, oy + 12, 4, 3, skin)
    cv.r(cx - 2, oy + 12, 4, 1, sk2)
    # өмд/банзлын бэлхүүс
    if bot_style == "skirt":
        for y in range(40, 66):
            hw = 6 + (y - 40) * 5 // 25 if not fem else 6 + (y - 40) * 5 // 25
            cv.r(cx - hw, oy + y, hw * 2, 1, bot_c)
        cv.r(cx - 11, oy + 65, 22, 1, _sh(bot_c, 0.75))
        cv.r(cx - 7, oy + 41, 1, 24, _sh(bot_c, 0.85))
        cv.r(cx + 6, oy + 41, 1, 24, _sh(bot_c, 0.85))
    elif long_bottom or bot_style == "shorts":
        for y in range(40, 49):
            hw = T(y) if y < 47 else 8
            cv.r(cx - hw, oy + y, hw * 2, 1, bot_c)
        cv.r(cx - T(40), oy + 40, T(40) * 2, 1, _sh(bot_c, 0.7))  # бүс
        cv.r(cx, oy + 41, 1, 8, _sh(bot_c, 0.7))
        if bot_style == "jeans":
            cv.r(cx - 5, oy + 42, 3, 1, _sh(bot_c, 1.3)); cv.r(cx + 2, oy + 42, 3, 1, _sh(bot_c, 1.3))
            cv.r(cx - 4, oy + 62, 1, 12, _sh(bot_c, 1.15)); cv.r(cx + 3, oy + 62, 1, 12, _sh(bot_c, 1.15))
    # цээж / торс
    for y in range(14, hem + 1):
        hw = T(y) if y <= 46 else (8 if y < 62 else 8)
        if top_style in ("coat", "deel") and y > 46:
            hw = 8 + (y - 46) // 8
        if top_style == "dress" and y > 38:
            hw = T(38) + 1 + (y - 38) * 6 // 32
        cv.r(cx - hw, oy + y, hw * 2, 1, top_c)
        cv.p(cx - hw, oy + y, _sh(top_c, 0.85))
        cv.p(cx + hw - 1, oy + y, _sh(top_c, 0.78))
    cv.r(cx - T(15), oy + 14, T(15) * 2, 1, _sh(top_c, 1.18))  # мөр
    cv.r(cx - T(hem) , oy + hem, T(hem) * 2 if hem <= 46 else 16, 1, _sh(top_c, 0.78)) if hem <= 46 else cv.r(cx - 8 - (hem - 46) // 8, oy + hem, 16 + (hem - 46) // 4, 1, _sh(top_c, 0.7))
    # хүзүүний нүх
    neck_open = {"tee": 3, "hoodie": 2, "shirt": 2, "jacket": 3, "sweater": 2, "coat": 2, "deel": 2, "suit": 2, "dress": 4}.get(top_style, 3)
    cv.r(cx - neck_open, oy + 14, neck_open * 2, 1, skin)
    if neck_open >= 3:
        cv.r(cx - neck_open + 1, oy + 15, neck_open * 2 - 2, 1, skin)
        cv.r(cx - neck_open + 1, oy + 15, 1, 1, sk1)
    if fem and top_style not in ("hoodie", "coat", "deel"):
        cv.r(cx - 5, oy + 29, 3, 1, _sh(top_c, 0.82)); cv.r(cx + 2, oy + 29, 3, 1, _sh(top_c, 0.82))
    # ---- хувцасны дэлгэрэнгүй ----
    if top_style == "hoodie":
        cv.r(cx - 4, oy + 12, 8, 3, _sh(top_c, 0.8))
        cv.r(cx - 2, oy + 12, 4, 2, skin)
        cv.r(cx - 5, oy + 36, 10, 8, _sh(top_c, 0.85))
        cv.r(cx - 5, oy + 36, 10, 1, _sh(top_c, 0.7))
        cv.p(cx - 2, oy + 16, (240, 240, 240, 255)); cv.p(cx - 2, oy + 17, (240, 240, 240, 255))
        cv.p(cx + 1, oy + 16, (240, 240, 240, 255)); cv.p(cx + 1, oy + 17, (240, 240, 240, 255))
    elif top_style == "shirt":
        cv.r(cx - 3, oy + 14, 2, 3, (245, 245, 245, 255)); cv.r(cx + 1, oy + 14, 2, 3, (245, 245, 245, 255))
        cv.r(cx, oy + 17, 1, 30, _sh(top_c, 0.7))
        for yy in range(20, 46, 5):
            cv.p(cx, oy + yy, (235, 235, 235, 255))
        cv.r(cx - 6, oy + 25, 3, 3, _sh(top_c, 0.85))
    elif top_style == "jacket":
        cv.r(cx - 2, oy + 16, 4, 31, _sh(top_c, 1.45) if sum(top_c[:3]) < 500 else _sh(top_c, 0.6))
        cv.r(cx - 3, oy + 16, 1, 31, _sh(top_c, 0.65)); cv.r(cx + 2, oy + 16, 1, 31, _sh(top_c, 0.65))
        cv.r(cx - 6, oy + 38, 4, 1, _sh(top_c, 0.7)); cv.r(cx + 2, oy + 38, 4, 1, _sh(top_c, 0.7))
    elif top_style == "sweater":
        for yy in range(16, 46, 3):
            for xx in range(-T(yy) + 1, T(yy) - 1, 2):
                cv.p(cx + xx, oy + yy, _sh(top_c, 0.9))
        cv.r(cx - T(44), oy + 44, T(44) * 2, 2, _sh(top_c, 0.85))
    elif top_style == "coat":
        cv.r(cx, oy + 15, 1, hem - 14, _sh(top_c, 0.55))
        for yy in (22, 30, 38, 46, 54):
            cv.p(cx - 2, oy + yy, (230, 230, 230, 255)); cv.p(cx + 2, oy + yy, (230, 230, 230, 255))
        cv.r(cx - 3, oy + 14, 2, 3, _sh(top_c, 0.75)); cv.r(cx + 1, oy + 14, 2, 3, _sh(top_c, 0.75))
        cv.r(cx - 7, oy + 50, 4, 1, _sh(top_c, 0.65)); cv.r(cx + 3, oy + 50, 4, 1, _sh(top_c, 0.65))
    elif top_style == "deel":
        gold = (250, 204, 21, 255)
        for k in range(0, 14):
            cv.p(cx - 2 + k // 2, oy + 14 + k, gold)
            cv.p(cx - 1 + k // 2, oy + 14 + k, gold)
        cv.r(cx - 6, oy + 36, 12, 3, gold)
        cv.r(cx + 2, oy + 38, 2, 5, _sh(gold, 0.85))
        cv.r(cx - 8, oy + hem - 1, 16 + (hem - 46) // 4, 1, gold)
        cv.r(cx + 3, oy + 28, 1, hem - 28 - 2, _sh(top_c, 0.75))
    elif top_style == "suit":
        cv.r(cx - 2, oy + 14, 4, 24, (245, 245, 245, 255))
        cv.r(cx - 1, oy + 15, 2, 22, (200, 30, 40, 255))
        cv.r(cx - 4, oy + 15, 2, 22, _sh(top_c, 0.65)); cv.r(cx + 2, oy + 15, 2, 22, _sh(top_c, 0.65))
        cv.r(cx + 4, oy + 25, 3, 1, (240, 240, 250, 255))
        cv.r(cx - 6, oy + 42, 4, 1, _sh(top_c, 0.65)); cv.r(cx + 2, oy + 42, 4, 1, _sh(top_c, 0.65))
        cv.r(cx, oy + 38, 1, 14, _sh(top_c, 0.6))
    elif top_style == "dress":
        cv.r(cx - 6, oy + 34, 12, 2, _sh(top_c, 0.78))
        cv.r(cx - 3, oy + 14, 1, 3, skin); cv.r(cx + 2, oy + 14, 1, 3, skin)
        cv.r(cx - 11, oy + hem - 1, 22, 1, _sh(top_c, 0.7))
        for xx in (-8, -4, 0, 4, 8):
            cv.r(cx + xx, oy + 50, 1, 20, _sh(top_c, 0.9))
    # ---- хүзүүнээс дээш: толгой ----
    head_rows = [(0, 2, 7), (1, 1, 8), (2, 0, 9), (3, 0, 9), (4, 0, 9), (5, 0, 9), (6, 0, 9), (7, 0, 9), (8, 1, 8), (9, 1, 8), (10, 2, 7), (11, 3, 6)]
    for y, a, b in head_rows:
        cv.r(hx + a, oy + y, b - a + 1, 1, skin)
    cv.r(hx - 1, oy + 5, 1, 3, skin); cv.r(hx + 10, oy + 5, 1, 3, skin)  # чих
    cv.r(hx + 1, oy + 9, 1, 1, sk1); cv.r(hx + 8, oy + 9, 1, 1, sk1)
    cv.r(hx + 3, oy + 11, 4, 1, sk1)  # эрүү
    # ---- үс (нүүрний өмнө) ----
    _hair_front(cv, hair_style, hx, oy, hair, skin, fem)
    # ---- нүүр ----
    if dead:
        red = (220, 38, 38, 255)
        for ex in (hx + 2, hx + 6):
            cv.p(ex, oy + 4, red); cv.p(ex + 2, oy + 4, red)
            cv.p(ex + 1, oy + 5, red)
            cv.p(ex, oy + 6, red); cv.p(ex + 2, oy + 6, red)
        cv.r(hx + 3, oy + 9, 4, 1, (60, 30, 30, 255))
    else:
        brow = _sh(hair, 0.7) if hair_style != "bald" else _sh(skin, 0.6)
        br_w = 3
        cv.r(hx + 1, oy + 3, br_w, 1, brow)
        cv.r(hx + 6, oy + 3, br_w, 1, brow)
        for ex in (hx + 2, hx + 6):
            cv.r(ex, oy + 5, 2, 1, (24, 18, 26, 255))
            cv.p(ex, oy + 5, (255, 255, 255, 255)) if False else None
            cv.p(ex + (0 if ex < cx else 1), oy + 4, _sh(skin, 0.88))
        if fem:
            cv.p(hx + 1, oy + 4, (24, 18, 26, 255)); cv.p(hx + 8, oy + 4, (24, 18, 26, 255))
        cv.r(hx + 4, oy + 7, 2, 1, sk1)  # хамар
        cv.p(hx + 4, oy + 8, sk2) if False else None
        cv.r(hx + 4, oy + 9, 2, 1, (176, 84, 84, 255) if not fem else (200, 96, 106, 255))
        _makeup(cv, outfit.get("makeup") or {}, hx, oy, skin)
    # ---- сэлбэг ----
    acc_style, acc_c = outfit.get("acc", (None, None))
    if acc_style:
        ac = _rgb(acc_c) if isinstance(acc_c, str) else acc_c
        if acc_style == "glasses":
            for ex in (hx + 1, hx + 6):
                cv.d.rectangle([ex, oy + 4, ex + 3, oy + 6], outline=ac)
            cv.r(hx + 5, oy + 5, 1, 1, ac)
            cv.p(hx, oy + 5, ac); cv.p(hx + 9, oy + 5, ac)
        elif acc_style == "necklace":
            cv.r(cx - 3, oy + 15, 6, 1, ac)
            cv.p(cx - 1, oy + 16, ac); cv.p(cx, oy + 17, (255, 230, 120, 255))
        elif acc_style == "scarf":
            cv.r(cx - 5, oy + 12, 10, 4, ac)
            cv.r(cx - 5, oy + 12, 10, 1, _sh(ac, 1.3))
            cv.r(cx + 1, oy + 16, 3, 10, ac)
        elif acc_style == "belt":
            cv.r(cx - T(37), oy + 37, T(37) * 2, 2, ac)
            cv.r(cx - 1, oy + 37, 3, 2, (250, 204, 21, 255))
        elif acc_style == "watch":
            cv.r(cx + T(18) - 1 + 1, oy + 46 + swing[1], 2, 2, ac)
            cv.p(cx + T(18) + 0, oy + 46 + swing[1], (255, 255, 255, 255))
        elif acc_style == "bag":
            cv.d.line([(cx - T(16), oy + 16), (cx + T(40), oy + 46)], fill=_sh(ac, 0.8))
            cv.r(cx + T(40) - 2, oy + 44, 7, 7, ac)
            cv.r(cx + T(40) - 2, oy + 44, 7, 1, _sh(ac, 1.3))
    # ---- малгай ----
    hat_style, hat_c = outfit.get("hat", (None, None))
    if hat_style:
        hc = _rgb(hat_c) if isinstance(hat_c, str) else hat_c
        hl = _sh(hc, 1.25)
        if hat_style == "cap":
            cv.r(hx - 1, oy - 2, 12, 5, hc); cv.r(hx - 1, oy - 2, 12, 1, hl)
            cv.r(hx + 4, oy + 3, 9, 1, _sh(hc, 0.8))
        elif hat_style == "beanie":
            cv.r(hx - 1, oy - 3, 12, 7, hc); cv.r(hx - 1, oy + 2, 12, 2, _sh(hc, 0.8))
            cv.r(hx + 4, oy - 5, 2, 2, hl)
        elif hat_style == "bucket":
            cv.r(hx, oy - 3, 10, 5, hc); cv.r(hx - 3, oy + 2, 16, 2, _sh(hc, 0.85))
        elif hat_style == "fedora":
            cv.r(hx + 1, oy - 5, 8, 7, hc); cv.r(hx - 3, oy + 2, 16, 2, _sh(hc, 0.85))
            cv.r(hx + 1, oy, 8, 1, (30, 30, 30, 255))
        elif hat_style == "tophat":
            cv.r(hx + 1, oy - 10, 8, 11, hc); cv.r(hx - 2, oy + 1, 14, 2, _sh(hc, 0.85))
            cv.r(hx + 1, oy - 1, 8, 1, (220, 38, 38, 255))
        elif hat_style == "mongolhat":
            cv.r(hx - 1, oy - 2, 12, 4, hc); cv.r(hx + 3, oy - 6, 4, 5, (220, 38, 38, 255))
            cv.r(hx + 4, oy - 7, 2, 1, (250, 204, 21, 255)); cv.r(hx - 2, oy + 2, 14, 2, _sh(hc, 0.8))

    # ---- outline ----
    a = cv.im.split()[3]
    grown = a.filter(ImageFilter.MaxFilter(3))
    ol = ImageChops.subtract(grown, a)
    outline = Image.new("RGBA", cv.im.size, (25, 20, 35, 255))
    outline.putalpha(ol)
    outline.alpha_composite(cv.im)
    if dead:
        g = outline.convert("LA").convert("RGBA")
        g.putalpha(outline.split()[3])
        outline = g
        d = ImageDraw.Draw(outline)
        d.ellipse([hx, oy - 6, hx + 10, oy - 3], outline=(250, 250, 250, 255))
    return outline


def _background(w, h):
    bg = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(int(70 - 30 * t), int(90 - 30 * t), int(150 - 60 * t)))
    d.rectangle([0, int(h * 0.9), w, h], fill=(52, 98, 62))
    d.rectangle([0, int(h * 0.9), w, int(h * 0.9) + 6], fill=(72, 128, 80))
    for sx, sy in ((30, 24), (110, 50), (250, 20), (300, 66), (190, 14)):
        d.rectangle([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    return bg


def render_scene(gender, skin_hex, outfit, dead=False, pet_key=None, name_tag=None):
    """-> (bytes, 'gif'|'png'). outfit: {slot: (style, hex)}"""
    W, H = 380, LH * SCALE
    frames = []
    bg = _background(W, H).convert("RGBA")
    pets = [render_pet(pet_key, 120, 0), render_pet(pet_key, 120, 1)] if pet_key else None
    pet_img = pets
    n = 1 if dead else 4
    for f in range(n):
        ch = _character(f, gender, skin_hex, outfit, dead)
        big = ch.resize((LW * SCALE, LH * SCALE), Image.NEAREST)
        fr = bg.copy()
        sh = ImageDraw.Draw(fr)
        shadow = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse([30, H - 30, 220, H - 6], fill=(0, 0, 0, 70))
        fr.alpha_composite(shadow)
        fr.alpha_composite(big, (0, 0))
        if pet_img is not None:
            bounce = 0
            p = pet_img[f % 2 if not dead else 0]
            if dead:
                p = pet_img[0].convert("LA").convert("RGBA")
                p.putalpha(pet_img[0].split()[3])
            sh2 = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh2).ellipse([236, H - 30, 366, H - 10], fill=(0, 0, 0, 70))
            fr.alpha_composite(sh2)
            fr.alpha_composite(p, (240, H - 128 - bounce))
        frames.append(fr.convert("RGB"))
    from pix import fit
    frames = [fit(f) for f in frames]
    buf = io.BytesIO()
    if n == 1:
        frames[0].save(buf, "PNG")
        return buf.getvalue(), "png"
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    pal[0].save(buf, "GIF", save_all=True, append_images=pal[1:], duration=220, loop=0, disposal=2)
    return buf.getvalue(), "gif"


def render_preview(gender, skin_hex, outfit, scale: int = 8) -> bytes:
    """Үс сонгох үеийн тогтмол PNG (толгой, мөр хүртэл)."""
    ch = _character(1, gender, skin_hex, outfit, False)
    ch = ch.crop((0, 0, LW, 40))
    big = ch.resize((ch.width * scale, ch.height * scale), Image.NEAREST)
    bg = Image.new("RGBA", big.size, (58, 64, 104, 255))
    bg.alpha_composite(big)
    from pix import fit
    buf = io.BytesIO()
    fit(bg.convert("RGB")).save(buf, "PNG")
    return buf.getvalue()
