from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = r"E:\ENSAI\djamal_site\images\blog"
os.makedirs(OUT, exist_ok=True)

W, H = 800, 420

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def gradient_img(c1, c2):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    return img, d

def save_with_overlay(img, label, fname, accent_rgb, shapes_fn=None):
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    if shapes_fn:
        shapes_fn(od, accent_rgb)
    # label pill at bottom-left
    pill_w = len(label) * 12 + 32
    od.rounded_rectangle([28, H-62, 28+pill_w, H-24], radius=18,
                          fill=accent_rgb+(100,), outline=accent_rgb+(180,))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    od.text((42, H-52), label, font=font, fill=(255,255,255,230))
    composite = Image.alpha_composite(img.convert('RGBA'), overlay)
    composite.convert('RGB').save(os.path.join(OUT, fname))
    print(f"  -> {fname}")

# --- shapes per post ---
def shapes_clip(d, a):
    for r in [120, 80, 40]:
        d.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], outline=a+(80,), width=2)
    d.ellipse([W//2-16, H//2-16, W//2+16, H//2+16], fill=a+(120,))
    for i in range(-5, 6):
        d.line([(W//2+i*60, 20), (W//2+i*60+30, H-20)], fill=a+(35,), width=1)

def shapes_surrogate(d, a):
    cx = W // 2
    d.line([(cx, H-50), (cx, H//2)], fill=a+(140,), width=3)
    d.line([(cx, H//2), (cx-W//4, H//4)], fill=a+(110,), width=2)
    d.line([(cx, H//2), (cx+W//4, H//4)], fill=a+(110,), width=2)
    for ox in [-W//4, W//4]:
        d.line([(cx+ox, H//4), (cx+ox-W//8, 45)], fill=a+(80,), width=1)
        d.line([(cx+ox, H//4), (cx+ox+W//8, 45)], fill=a+(80,), width=1)
    d.ellipse([cx-7, H//2-7, cx+7, H//2+7], fill=a+(220,))

def shapes_bayopt(d, a):
    for x in range(0, W-1):
        y1 = int(H//2 + 80*math.sin(x/50.0) - 50*math.exp(-((x-400)**2)/18000.0))
        y2 = int(H//2 + 80*math.sin((x+1)/50.0) - 50*math.exp(-(((x+1)-400)**2)/18000.0))
        d.line([(x, y1), (x+1, y2)], fill=a+(130,), width=2)
    d.ellipse([394, int(H//2-50)-6, 406, int(H//2-50)+6], fill=(255,80,80,220))
    for i in range(11):
        bx = 50 + i*70
        bh = int(60*abs(math.sin(i*1.2+0.5)))
        d.line([(bx, H-45), (bx, H-45-bh)], fill=a+(60,), width=7)

def shapes_bayexp(d, a):
    for x in range(0, W-1):
        y1 = int(H//2 - 130*math.exp(-((x-W//2)**2)/9000))
        y2 = int(H//2 - 130*math.exp(-(((x+1)-W//2)**2)/9000))
        d.line([(x, y1), (x+1, y2)], fill=a+(150,), width=2)
    d.line([(60, H//2), (W-60, H//2)], fill=a+(50,), width=1)
    d.line([(W//2, 40), (W//2, H-40)], fill=(255,255,80,50), width=1)

def shapes_sig(d, a):
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=a+(25,), width=1)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=a+(25,), width=1)
    d.polygon([(190,75),(490,55),(615,175),(575,320),(340,375),(145,275)],
              fill=a+(55,), outline=a+(190,))
    d.polygon([(510,95),(670,85),(715,195),(595,215)],
              fill=a+(40,), outline=a+(140,))

def shapes_gd(d, a):
    for x in range(0, W-1):
        y1 = int(75 + (H-130)*((x/W)**2))
        y2 = int(75 + (H-130)*(((x+1)/W)**2))
        d.line([(x, y1), (x+1, y2)], fill=a+(160,), width=3)
    for i in range(1, 5):
        px = int(i*(W//4.5))
        py = int(75 + (H-130)*((px/W)**2))
        d.ellipse([px-6, py-6, px+6, py+6], fill=(255,200,100,230))
    d.line([(50, H-45), (W-50, H-45)], fill=a+(50,), width=1)
    d.line([(70, 20), (70, H-30)], fill=a+(50,), width=1)

def shapes_quarto(d, a):
    d.rounded_rectangle([70, 70, W-70, H-70], radius=16, fill=a+(25,), outline=a+(110,))
    d.rounded_rectangle([110, 100, W-110, 145], radius=8, fill=a+(70,))
    d.rounded_rectangle([110, 160, W//2-10, 180], radius=4, fill=(255,255,255,40))
    d.rounded_rectangle([110, 192, 3*W//4, 207], radius=4, fill=(255,255,255,30))
    d.rounded_rectangle([110, 218, W//2+40, 233], radius=4, fill=(255,255,255,22))
    d.rounded_rectangle([110, H-148, W-110, H-108], radius=10, fill=a+(55,), outline=a+(85,))

posts = [
    ("#0f1c40", "#2a1060", "CLIP & DINOv2", "clip-dinov2.png", "#9b59f5", shapes_clip),
    ("#1a0c00", "#3d1200", "Surrogate Models", "surrogate-models.png", "#f47c2b", shapes_surrogate),
    ("#060b22", "#112244", "Optimisation Bayésienne", "bayesian-optim.png", "#00c8d4", shapes_bayopt),
    ("#060f1c", "#0c1e3a", "Expérience Bayésienne", "bayesian-experience.png", "#4f8cff", shapes_bayexp),
    ("#081a0f", "#0d3020", "Cartographie SIG avec R", "sig-carto.png", "#27ae60", shapes_sig),
    ("#1a0800", "#301500", "Descente de Gradient", "gradient-descent.png", "#e67e22", shapes_gd),
    ("#0a0a1a", "#101030", "Présentations Quarto & R", "quarto-presentations.png", "#a855f7", shapes_quarto),
]

print("Generating blog thumbnails...")
for c1, c2, label, fname, accent_hex, shapes_fn in posts:
    img, _ = gradient_img(hex_to_rgb(c1), hex_to_rgb(c2))
    save_with_overlay(img, label, fname, hex_to_rgb(accent_hex), shapes_fn)

print("Done.")
