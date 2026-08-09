"""Generate academic project thumbnails."""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

OUT = r"E:\ENSAI\djamal_site\images\academic"
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
        r = int(c1[0]+(c2[0]-c1[0])*t)
        g = int(c1[1]+(c2[1]-c1[1])*t)
        b = int(c1[2]+(c2[2]-c1[2])*t)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def label_img(img, text, accent_rgb):
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    pill_w = min(len(text)*11+28, W-60)
    od.rounded_rectangle([28, H-60, 28+pill_w, H-24], radius=16,
                          fill=accent_rgb+(110,), outline=accent_rgb+(200,))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19)
    except:
        font = ImageFont.load_default()
    od.text((40, H-50), text, font=font, fill=(255,255,255,235))
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

def save(img, fname):
    img.save(os.path.join(OUT, fname))
    print(f"  -> {fname}")

# ─── P1: Medical NLP / SciBERT clusters ────────────────────────────────────
def make_nlp():
    img = gradient_img(hex_to_rgb("#06101e"), hex_to_rgb("#0e1f3a"))
    d = ImageDraw.Draw(img)
    # Word cloud effect
    rng = random.Random(42)
    sizes = [36,28,24,20,18,16,14,12]
    words = ["SciBERT","HDBSCAN","UMAP","Cluster","NLP","Embeddings",
             "Cancer","Maternal","Abstract","Theme","Noise","DBCV"]
    colors = [(109,168,255),(64,200,160),(200,120,80),(160,100,200)]
    try:
        fonts = [ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", s) for s in sizes]
    except:
        fonts = [ImageFont.load_default()]*len(sizes)
    for i, word in enumerate(words):
        x = rng.randint(40, W-150)
        y = rng.randint(30, H-80)
        fi = min(i, len(fonts)-1)
        c = colors[i % len(colors)]
        d.text((x, y), word, font=fonts[fi], fill=c+(180,))
    # Cluster circles
    centers = [(200,180),(420,140),(620,200),(300,290)]
    cluster_colors = [(64,200,160),(109,168,255),(200,120,80),(160,100,200)]
    for (cx,cy), cc in zip(centers, cluster_colors):
        for r in [50,35,20]:
            alpha = 30 + (50-r)
            overlay = Image.new('RGBA', (W,H), (0,0,0,0))
            od = ImageDraw.Draw(overlay)
            od.ellipse([cx-r,cy-r,cx+r,cy+r], fill=cc+(alpha,))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            d = ImageDraw.Draw(img)
    return label_img(img, "Medical NLP · SciBERT + HDBSCAN", (109,168,255))

# ─── P2: Network / inauthentic diffusion ───────────────────────────────────
def make_network():
    img = gradient_img(hex_to_rgb("#0a060f"), hex_to_rgb("#1a0d2e"))
    d = ImageDraw.Draw(img)
    rng = random.Random(7)
    # Draw network nodes + edges
    nodes = [(rng.randint(80,W-80), rng.randint(60,H-80)) for _ in range(22)]
    # Some highlighted cluster
    cluster = nodes[:7]
    for i,(x1,y1) in enumerate(nodes):
        for j,(x2,y2) in enumerate(nodes):
            if i<j and rng.random()>0.75:
                d.line([(x1,y1),(x2,y2)], fill=(155,89,245,40), width=1)
    for i,(x1,y1) in enumerate(cluster):
        for j,(x2,y2) in enumerate(cluster):
            if i<j:
                d.line([(x1,y1),(x2,y2)], fill=(255,80,120,80), width=2)
    for nx,ny in nodes:
        d.ellipse([nx-5,ny-5,nx+5,ny+5], fill=(155,89,245,160))
    for nx,ny in cluster:
        d.ellipse([nx-8,ny-8,nx+8,ny+8], fill=(255,80,120,200))
    return label_img(img, "Inauthentic Diffusion · CLIP + Network", (155,89,245))

# ─── P3: FuelTrack / architecture layers ───────────────────────────────────
def make_fueltrack():
    img = gradient_img(hex_to_rgb("#06120a"), hex_to_rgb("#0c2215"))
    d = ImageDraw.Draw(img)
    layers = [
        ("CLI / User Interface", (39,174,96)),
        ("Service Layer", (46,204,113)),
        ("DAO / Repository", (22,160,133)),
        ("Database (PostgreSQL)", (21,152,124)),
    ]
    y0 = 70
    for label, c in layers:
        rect_y = y0
        overlay = Image.new('RGBA', (W,H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([80, rect_y, W-80, rect_y+52], radius=10,
                              fill=c+(50,), outline=c+(160,))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        d = ImageDraw.Draw(img)
        try:
            f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
        except:
            f = ImageFont.load_default()
        d.text((100, rect_y+17), label, font=f, fill=(220,255,230,220))
        # Arrow down
        if rect_y + 52 < 350:
            d.line([(W//2, rect_y+52),(W//2, rect_y+72)], fill=(39,174,96,100), width=2)
            d.polygon([(W//2-6, rect_y+66),(W//2+6, rect_y+66),(W//2, rect_y+76)],
                      fill=(39,174,96,120))
        y0 += 72
    return label_img(img, "FuelTrack · FastAPI + Layered Architecture", (39,174,96))

# ─── P4: NBA / regression + predictions ─────────────────────────────────────
def make_nba():
    img = gradient_img(hex_to_rgb("#06080f"), hex_to_rgb("#0d1525"))
    d = ImageDraw.Draw(img)
    # Scatter plot style
    rng = random.Random(1)
    for _ in range(60):
        x = rng.randint(60, W-60)
        y = rng.randint(60, H-80)
        r = rng.randint(3,8)
        alpha = rng.randint(100,200)
        d.ellipse([x-r,y-r,x+r,y+r], fill=(79,140,255,alpha))
    # Regression line
    d.line([(60, H-100),(W-60, 80)], fill=(255,200,80,160), width=3)
    # Prediction band
    for i in range(0, W-120, 2):
        x = 60+i
        y_mid = int(H-100 + (80-(H-100))*i/(W-120))
        band = 30
        d.line([(x, y_mid-band),(x, y_mid+band)], fill=(255,200,80,20), width=1)
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
    except:
        f = ImageFont.load_default()
    d.text((W//2-80, 28), "Career Length (years)", font=f, fill=(200,220,255,200))
    return label_img(img, "NBA Career Prediction · Ridge + Uncertainty", (79,140,255))

# ─── P5: Gaming & health / statistics ────────────────────────────────────
def make_gaming():
    img = gradient_img(hex_to_rgb("#0f0618"), hex_to_rgb("#1e0c30"))
    d = ImageDraw.Draw(img)
    # Bar chart comparing groups
    groups = [("Non-joueurs","#9b59f5",0.4),("Joueurs modérés","#e74c3c",0.62),
              ("Joueurs intensifs","#f39c12",0.78)]
    bar_w = 110
    x0 = 80
    max_h = 220
    for label, color, val in groups:
        bh = int(val*max_h)
        c = hex_to_rgb(color)
        overlay = Image.new('RGBA',(W,H),(0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([x0, H-80-bh, x0+bar_w, H-80], radius=8,
                              fill=c+(140,), outline=c+(200,))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        d = ImageDraw.Draw(img)
        try:
            f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
        except:
            f = ImageFont.load_default()
        d.text((x0+5, H-78), label, font=f, fill=(220,200,255,200))
        x0 += bar_w + 40
    # X axis
    d.line([(60, H-80),(W-60, H-80)], fill=(160,120,255,80), width=2)
    return label_img(img, "Gaming & Adolescent Health · MCA + R", (155,89,245))

# ─── P6: Survey methodology ──────────────────────────────────────────────
def make_survey():
    img = gradient_img(hex_to_rgb("#060f1a"), hex_to_rgb("#0c2035"))
    d = ImageDraw.Draw(img)
    # Clipboard + form lines
    overlay = Image.new('RGBA',(W,H),(0,0,0,0))
    od = ImageDraw.Draw(overlay)
    # Clipboard shape
    od.rounded_rectangle([W//2-120, 40, W//2+120, H-60], radius=14,
                          fill=(20,60,100,80), outline=(79,140,255,140))
    od.rounded_rectangle([W//2-50, 28, W//2+50, 60], radius=10,
                          fill=(79,140,255,100), outline=(79,140,255,180))
    # Form lines
    line_y = 80
    for i in range(8):
        lw = 180 - i*8
        alpha = 120 - i*10
        od.rounded_rectangle([W//2-100, line_y, W//2-100+lw, line_y+12],
                              radius=4, fill=(140,190,255,alpha))
        line_y += 26
    # Checkbox
    od.rounded_rectangle([W//2-100, line_y+10, W//2-80, line_y+30], radius=3,
                          fill=(39,174,96,140), outline=(39,174,96,200))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return label_img(img, "Survey Methodology · Sampling + R", (79,140,255))

# ─── P7: HICP / time series ───────────────────────────────────────────────
def make_hicp():
    img = gradient_img(hex_to_rgb("#060c12"), hex_to_rgb("#0d1a2a"))
    d = ImageDraw.Draw(img)
    # Time series line with forecast
    rng = random.Random(99)
    pts = []
    y_val = H//2
    for i in range(55):
        y_val += rng.randint(-18, 18)
        y_val = max(80, min(H-100, y_val))
        pts.append((30 + i*11, y_val))
    # Historical line (blue)
    for i in range(len(pts)-1):
        d.line([pts[i], pts[i+1]], fill=(79,140,255,180), width=2)
    # Forecast (orange dashed)
    last = pts[-1]
    forecast = []
    yf = last[1]
    for i in range(1, 16):
        yf -= rng.randint(2,10)
        yf = max(80, min(H-100, yf))
        forecast.append((last[0]+i*11, yf))
    for i in range(len(forecast)-1):
        if i % 2 == 0:
            d.line([forecast[i], forecast[i+1]], fill=(243,156,18,180), width=2)
    # CI band
    for i, (fx,fy) in enumerate(forecast):
        band = 10 + i*3
        d.line([(fx,fy-band),(fx,fy+band)], fill=(243,156,18,40), width=2)
    # Points
    for px,py in pts[-5:]:
        d.ellipse([px-4,py-4,px+4,py+4], fill=(79,140,255,200))
    # Vertical separator
    d.line([(last[0],40),(last[0],H-70)], fill=(255,255,255,40), width=1)
    return label_img(img, "HICP Forecasting · ARIMA/SARIMA + R", (79,140,255))

tasks = [
    (make_nlp,      "nlp-scibert.png"),
    (make_network,  "network-diffusion.png"),
    (make_fueltrack,"fueltrack.png"),
    (make_nba,      "nba-career.png"),
    (make_gaming,   "gaming-health.png"),
    (make_survey,   "survey.png"),
    (make_hicp,     "hicp-forecast.png"),
]

print("Generating academic thumbnails...")
for fn, fname in tasks:
    save(fn(), fname)
print("Done.")
