# -*- coding: utf-8 -*-
"""
=========================================================
 ASCII ART PRO - محوّل الصور إلى رسم ASCII احترافي
=========================================================
نسخة محسّنة بالكامل مع:
  - قياس كثافة كل رمز تلقائياً من الخط نفسه (Character Density)
  - دعم أحرف لاتينية + روسية + يونانية + رموز + Box Drawing
  - تقسيم الصورة إلى Blocks واختيار أقرب رمز لكل Block
  - Auto Contrast + Equalize + Adaptive (Local) Contrast
  - Sobel Edge Detection لإبراز الحواف والتفاصيل
  - Sharpen + Gaussian Blur خفيف لإزالة النويز
  - إخراج: نص عادي (.txt) + ملون HTML (.html) + ANSI ملون (.ansi)
  - واجهة رسومية بنفس ألوان أداة MASTER MERGER
  - دعم تحويل صورة واحدة أو مجلد كامل دفعة واحدة
=========================================================
"""

import os
import sys
import tkinter as tk

from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import numpy as np

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


# =========================================================
# [1] الإعدادات العامة - عدّل القيم هنا بسهولة
# =========================================================

APP_TITLE = "ASCII ART PRO"

FONT_FILE = "consola.ttf"            # اسم الخط الأحادي العروض المدمج داخل البرنامج
DEFAULT_WIDTH = 200                  # العرض الافتراضي بالأعمدة
MIN_WIDTH, MAX_WIDTH = 40, 500       # حدود شريط تغيير العرض

# --- إعدادات معالجة الصورة ---
EDGE_WEIGHT = 0.35                   # قوة إبراز الحواف (0 = بدون، 1 = قوي جداً)
LOCAL_CONTRAST = 0.45                # قوة التباين المحلي (Adaptive Contrast)
DENOISE = 0.35                       # نصف قطر Gaussian Blur الخفيف (تقليل النويز)
SHARPEN = 0.9                        # قوة زيادة الحدة (Sharpness)
GLOBAL_CONTRAST = 1.15               # تضخيم التباين النهائي بعد كل المعالجات

IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
OUTPUT_FOLDER_NAME = "ASCII_Art"     # اسم مجلد النتائج في وضع تحويل المجلد


# =========================================================
# [2] بناء مجموعة الرموز (لاتيني + روسي + يوناني + رموز)
# =========================================================

def build_charset():
    """مجموعة كبيرة من الرموز - سيقيس البرنامج درجة سواد كل واحد بنفسه"""
    return list(
        "abcdefghijklmnopqrstuvwxyz"            # إنجليزي صغير
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"            # إنجليزي كبير
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"     # روسي صغير
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"     # روسي كبير
        "αβγδεζηθικλμνξοπρστυφχψω"              # يوناني
        "0123456789"                            # أرقام
        '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'     # رموز شائعة
        "░▒▓█▄▀■□▪▫▲▼◄►"                       # كتل وتظليل (رائعة للـ ASCII)
        "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"               # خطوط Box Drawing
        "←↑→↓↔↕∞≈≡≠≤≥±×÷√∑∫∏∂°"               # أسهم ورموز رياضية
    )


# =========================================================
# [3] إيجاد ملف الخط (يعمل مع الـ exe المُجمّع أيضاً)
# =========================================================

def resolve_font_path():
    """يبحث عن الخط أولاً داخل حزمة الـ exe ثم في نظام ويندوز"""
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        p = os.path.join(bundle, FONT_FILE)
        if os.path.exists(p):
            return p

    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), FONT_FILE),
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


# =========================================================
# [4] قياس كثافة الرموز (Character Density Measurement)
# =========================================================

def measure_characters(chars, font_path, render_size=48):
    """
    يرسم كل رمز بالخط الحقيقي ويحسب نسبة البكسلات الغامقة فيه.
    النتيجة: ترتيب دقيق من الأخف للأغمق يختلف حسب الخط المستخدم.
    """
    font = ImageFont.truetype(font_path, render_size)
    asc, desc = font.getmetrics()
    cell_h = asc + desc                                   # ارتفاع سطر واحد
    cell_w = int(round(font.getlength("M")))              # عرض الرمز (أحادي العروض)

    entries = []
    seen = set()

    for ch in chars:
        img = Image.new("L", (cell_w, cell_h), 255)
        ImageDraw.Draw(img).text((0, 0), ch, font=font, fill=0)

        mask = np.asarray(img) < 128
        ink = int(mask.sum())

        if ink == 0:
            continue          # الرمز لا يُرسم بالخط -> نتجاهله

        sig = mask.tobytes()  # بصمة شكل الرمز
        if sig in seen:
            continue          # رمز مشابه تماماً لرمز سابق -> نحتفظ بواحد فقط
        seen.add(sig)

        density = ink / float(cell_w * cell_h)   # نسبة السواد من 0 إلى 1
        entries.append((density, ch))

    entries.sort()                                # من الأخف للأغمق
    chars_sorted = [e[1] for e in entries]
    densities = np.array([e[0] for e in entries], dtype=np.float64)

    return chars_sorted, densities, cell_w, cell_h


# =========================================================
# [5] معالجات الصورة (باستخدام NumPy لسرعة عالية)
# =========================================================

def autocontrast(a, lo_pct=1.0, hi_pct=99.0):
    """Auto Contrast: توزيع السطوع على كامل المدى حسب النسب المئوية"""
    lo, hi = np.percentile(a, (lo_pct, hi_pct))
    if hi - lo < 1e-6:
        return a
    return np.clip((a - lo) / (hi - lo), 0.0, 1.0)


def equalize(a):
    """Equalize: توزيع متوازن لسطوع البكسلات (Histogram Equalization)"""
    a = np.clip(a, 0.0, 1.0)
    hist, _ = np.histogram(a, bins=256, range=(0.0, 1.0))
    cdf = hist.cumsum()
    cdf = cdf / cdf[-1]
    bins = np.linspace(0.0, 1.0, 256)
    return np.interp(a, bins, cdf)


def to_image(a):
    """تحويل مصفوفة 0..1 إلى صورة PIL"""
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def local_contrast(arr, gain=LOCAL_CONTRAST, radius_frac=0.08):
    """Adaptive Contrast: طرح الإضاءة البطيئة لإظهار التفاصيل في كل منطقة"""
    img = to_image(arr)
    radius = max(1, int(radius_frac * min(img.size)))
    low = img.filter(ImageFilter.GaussianBlur(radius=radius))
    low = np.asarray(low, np.float64) / 255.0
    return np.clip(arr + (arr - low) * gain, 0.0, 1.0)


def sharpen(arr, amount=SHARPEN):
    """زيادة الحدة عبر Unsharp Mask"""
    img = to_image(arr)
    bl = np.asarray(img.filter(ImageFilter.GaussianBlur(radius=1.0)), np.float64) / 255.0
    return np.clip(arr + (arr - bl) * amount, 0.0, 1.0)


def sobel_magnitude(a):
    """كشف الحواف بطريقة Sobel - يبرز حدود الوجه والشعر والتفاصيل"""
    a = np.asarray(a, np.float64)
    gx = np.zeros_like(a)
    gy = np.zeros_like(a)

    gx[1:-1, 1:-1] = (
        (a[2:, 2:] + 2 * a[2:, 1:-1] + a[2:, :-2])
        - (a[:-2, 2:] + 2 * a[:-2, 1:-1] + a[:-2, :-2])
    )
    gy[1:-1, 1:-1] = (
        (a[:-2, 2:] + 2 * a[1:-1, 2:] + a[2:, 2:])
        - (a[:-2, :-2] + 2 * a[1:-1, :-2] + a[2:, :-2])
    )

    mag = np.hypot(gx, gy)
    mx = float(mag.max())
    if mx > 1e-9:
        mag = mag / mx
    return mag


def preprocess(arr):
    """سلسلة المعالجة الكاملة للصورة قبل التحويل"""
    arr = autocontrast(arr)                          # 1) Auto Contrast
    arr = equalize(arr)                              # 2) Equalize
    arr = local_contrast(arr, gain=LOCAL_CONTRAST)   # 3) تباين محلي (Adaptive)
    arr = np.asarray(
        to_image(arr).filter(ImageFilter.GaussianBlur(radius=DENOISE)),
        np.float64,
    ) / 255.0                                        # 4) Gaussian Blur خفيف
    arr = sharpen(arr, amount=SHARPEN)               # 5) Sharpness
    arr = autocontrast(arr, 0.5, 99.5)               # 6) تباين أخير
    arr = np.clip((arr - 0.5) * GLOBAL_CONTRAST + 0.5, 0.0, 1.0)
    return arr


# =========================================================
# [6] محرك التحويل الأساسي
# =========================================================

class AsciiEngine:
    """يقيس الرموز مرة واحدة ثم يحوّل أي عدد من الصور"""

    def __init__(self, font_path=None, log=None):
        self.log = log or (lambda msg, tag="info": None)
        self.font_path = font_path or resolve_font_path()
        if not self.font_path:
            raise RuntimeError("لم يتم العثور على خط أحادي العروض")

        self.log("⌨️  جاري قياس كثافة الرموز من الخط نفسه...", "info")
        self.chars, self.densities, self.cell_w, self.cell_h = \
            measure_characters(build_charset(), self.font_path)
        self.log(
            f"✅ تم تحميل {len(self.chars)} رمزاً بمستويات سواد مُقاسة فعلياً",
            "success",
        )

    def convert(self, image_path, width=DEFAULT_WIDTH):
        """يحوّل صورة واحدة ويعيد: نص + ألوان + شبكة الأحرف"""
        img = Image.open(image_path)

        # معالجة الشفافية (بدّلها على خلفية بيضاء)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            rgba = img.convert("RGBA")
            bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, rgba).convert("RGB")
        else:
            img = img.convert("RGB")

        rgb = img.convert("RGB")
        w, h = img.size

        # --- المعالجة التحضيرية ---
        gray = img.convert("L")
        arr = np.asarray(gray, np.float64) / 255.0
        arr = preprocess(arr)

        # --- خريطة الحواف ---
        edge = sobel_magnitude(arr)

        # --- أبعاد شبكة الرموز مع مراعاة نسبة أبعاد الخط ---
        out_w = int(width)
        out_h = max(1, int(round(out_w * (h / w) * (self.cell_w / self.cell_h))))

        # --- اختزال الصورة إلى شبكة كتل (Blocks) ---
        bright = np.asarray(
            to_image(arr).resize((out_w, out_h), Image.Resampling.LANCZOS),
            np.float64,
        ) / 255.0
        edge_small = np.asarray(
            Image.fromarray((edge * 255).astype(np.uint8))
            .resize((out_w, out_h), Image.Resampling.LANCZOS),
            np.float64,
        ) / 255.0

        # --- دمج الحواف مع السطوع (الحواف تظهر برموز أغمق) ---
        eff = np.clip(bright - EDGE_WEIGHT * edge_small, 0.0, 1.0)
        target = 1.0 - eff  # 0 = أفتح رمز، 1 = أغمق رمز

        # --- اختيار أقرب رمز لكل Block حسب كثافته المقاسة ---
        flat = target.ravel()
        idx = np.searchsorted(self.densities, flat)
        idx = np.clip(idx, 0, len(self.densities) - 1)
        left = np.maximum(idx - 1, 0)
        gap_l = np.abs(flat - self.densities[left])
        gap_r = np.abs(flat - self.densities[idx])
        idx = np.where(gap_l <= gap_r, left, idx)

        chars_grid = "".join(self.chars[i] for i in idx)
        lines = [
            chars_grid[i:i + out_w]
            for i in range(0, len(chars_grid), out_w)
        ]

        # --- ألوان الكتل من الصورة الأصلية (للوضع الملون) ---
        colors = np.asarray(
            rgb.resize((out_w, out_h), Image.Resampling.LANCZOS),
            np.int32,
        )

        return {
            "txt": "\n".join(lines),
            "lines": lines,
            "colors": colors,
            "out_w": out_w,
            "out_h": out_h,
        }


# =========================================================
# [7] إخراج HTML ملون + ANSI ملون
# =========================================================

def html_escape(ch):
    return {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}.get(ch, ch)


def make_html(result, title):
    """صفحة HTML ملونة (كل رمز بلون الكتلة المقابلة له من الصورة)"""
    spans = []
    lines, colors = result["lines"], result["colors"]
    for li, line in enumerate(lines):
        for ci, ch in enumerate(line):
            r, g, b = (int(v) for v in colors[li, ci])
            spans.append(f'<span style="color:#{r:02x}{g:02x}{b:02x}">{html_escape(ch)}</span>')
        spans.append("\n")

    return f"""<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="utf-8">
<title>{html_escape(title)} - ASCII Art</title>
<style>
  body {{ background:#0a0a0a; color:#e0e0e0; margin:24px;
         font-family:'Consolas','Courier New',monospace; }}
  pre {{ line-height:1.05; letter-spacing:0; font-size:11px;
        color:#ffffff; }}
  h1 {{ color:#00adb5; font-family:'Segoe UI',sans-serif; }}
  .info {{ color:#888; font-family:'Segoe UI',sans-serif; font-size:12px; }}
</style>
</head>
<body>
<h1>ASCII ART PRO</h1>
<p class="info">المصدر: {html_escape(title)} &nbsp;|&nbsp; الأبعاد: {result['out_w']} x {result['out_h']} رمز</p>
<pre>{''.join(spans)}</pre>
</body>
</html>
"""


def make_ansi(result):
    """نص ملون برموز ANSI (24-bit True Color) - يُفتح في الطرفية الداعمة"""
    parts = []
    lines, colors = result["lines"], result["colors"]
    for li, line in enumerate(lines):
        for ci, ch in enumerate(line):
            r, g, b = (int(v) for v in colors[li, ci])
            parts.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
        parts.append("\x1b[0m\n")
    parts.append("\x1b[0m")
    return "".join(parts)


# =========================================================
# [8] الحفظ في ملفات
# =========================================================

def save_results(result, folder, stem):
    """يحفظ النتيجة كـ .txt و .html و .ansi داخل folder"""
    os.makedirs(folder, exist_ok=True)

    txt_path = os.path.join(folder, stem + ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["txt"])

    html_path = os.path.join(folder, stem + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(make_html(result, stem))

    ansi_path = os.path.join(folder, stem + ".ansi")
    with open(ansi_path, "w", encoding="utf-8") as f:
        f.write(make_ansi(result))

    return txt_path, html_path, ansi_path


# =========================================================
# [9] الواجهة الرسومية (نفس ألوان وأسلوب MASTER MERGER)
# =========================================================

root = None
log_text = None
entry_path = None
mode_var = None
width_var = None
engine = None


def log_message(msg, tag="info"):
    """يكتب سطراً ملوناً في نافذة اللوج"""
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, msg + "\n", tag)
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)
    root.update()


def browse():
    """يختار صورة أو مجلد حسب الوضع المحدد"""
    if mode_var.get() == 0:
        path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[("الصور", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"), ("كل الملفات", "*.*")],
        )
    else:
        path = filedialog.askdirectory(title="اختر مجلد الصور")

    if path:
        entry_path.config(state=tk.NORMAL)
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)
        entry_path.config(state="readonly")


def convert_one(path, width):
    """تحويل صورة واحدة"""
    name = os.path.splitext(os.path.basename(path))[0]
    out_folder = os.path.join(os.path.dirname(os.path.abspath(path)), name + "_ascii")

    log_message(f"⚙️  تحويل: {os.path.basename(path)}")
    result = engine.convert(path, width)
    txt_path, html_path, ansi_path = save_results(result, out_folder, name)

    log_message(f"✅ تم إنشاء الملفات بنجاح", "success")
    log_message(f"📄  {txt_path}", "info")
    log_message(f"🌐  {html_path}", "info")
    log_message(f"🎨  {ansi_path}", "info")
    return 1


def convert_folder(folder, width):
    """تحويل كل الصور داخل مجلد"""
    files = sorted(
        f for f in os.listdir(folder)
        if f.lower().endswith(IMG_EXTS)
    )
    if not files:
        log_message("❌ لا توجد صور داخل هذا المجلد", "error")
        return 0

    out_root = os.path.join(folder, OUTPUT_FOLDER_NAME)
    os.makedirs(out_root, exist_ok=True)
    log_message(f"📁  مجلد النتائج: {out_root}", "info")

    ok = 0
    for f in files:
        try:
            log_message(f"⚙️  تحويل: {f}")
            stem = os.path.splitext(f)[0]
            result = engine.convert(os.path.join(folder, f), width)
            save_results(result, out_root, stem)
            ok += 1
            log_message(f"✅  {f}", "success")
        except Exception as e:
            log_message(f"❌  {f} — {e}", "error")

    log_message(f"🎯  تم تحويل {ok} من أصل {len(files)} صورة", "success")
    return ok


def start_process():
    """البداية: قراءة الإعدادات ثم التحويل"""
    path = entry_path.get().strip()
    if not path:
        messagebox.showerror("خطأ", "اختر صورة أو مجلد أولاً")
        return
    if not os.path.exists(path):
        messagebox.showerror("خطأ", "المسار غير صالح")
        return

    try:
        width = int(width_var.get())
    except Exception:
        width = DEFAULT_WIDTH
    width = max(MIN_WIDTH, min(MAX_WIDTH, width))

    # تنظيف اللوج
    log_text.config(state=tk.NORMAL)
    log_text.delete(1.0, tk.END)
    log_text.config(state=tk.DISABLED)

    log_message("⏳ بدء العملية...")

    try:
        if mode_var.get() == 0:
            if os.path.isdir(path):
                messagebox.showerror("خطأ", "اخترت مجلداً لكن الوضع مضبوط على «صورة واحدة»")
                return
            count = convert_one(path, width)
        else:
            if not os.path.isdir(path):
                messagebox.showerror("خطأ", "اخترت ملفاً لكن الوضع مضبوط على «مجلد كامل»")
                return
            count = convert_folder(path, width)

        log_message(f"\n🎉 انتهى! تم إنشاء {count} نتيجة بنجاح", "success")
        messagebox.showinfo("تم بنجاح", f"اكتملت العملية!\nتم إنشاء {count} نتيجة")
    except Exception as e:
        log_message(f"❌ خطأ: {e}", "error")
        messagebox.showerror("خطأ", str(e))


def build_gui():
    global root, log_text, entry_path, mode_var, width_var, engine

    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("650x560")
    root.configure(bg="#1e1e1e", padx=20, pady=20)

    # ---- التنسيق العام (نفس ألوان أداة MASTER MERGER) ----
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(".", background="#1e1e1e", foreground="#ffffff")
    style.configure("TLabel", background="#1e1e1e", foreground="#e0e0e0", font=("Segoe UI", 10))
    style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff", bordercolor="#3d3d3d")
    style.configure("TRadiobutton", background="#1e1e1e", foreground="#e0e0e0", font=("Segoe UI", 10))
    style.configure("TSpinbox", fieldbackground="#2d2d2d", foreground="#ffffff", arrowcolor="#00adb5")
    style.configure("TButton", background="#333333", foreground="#ffffff", font=("Segoe UI", 9, "bold"))
    style.map("TButton", background=[("active", "#444444")])

    # ---- العنوان ----
    lbl_title = tk.Label(
        root,
        text="ASCII ART PRO",
        bg="#1e1e1e",
        fg="#00adb5",
        font=("Segoe UI", 18, "bold"),
    )
    lbl_title.pack(pady=(0, 20))

    # ---- اختيار الوضع: صورة أو مجلد ----
    mode_var = tk.IntVar(value=0)
    frame_mode = ttk.Frame(root)
    frame_mode.pack(fill="x", pady=(0, 10))

    ttk.Radiobutton(frame_mode, text="🖼️  صورة واحدة", variable=mode_var, value=0).pack(side="left", padx=(0, 20))
    ttk.Radiobutton(frame_mode, text="📁  مجلد كامل", variable=mode_var, value=1).pack(side="left")

    # ---- اختيار المسار ----
    ttk.Label(root, text="مسار الصورة أو المجلد:").pack(anchor="w")
    frame_path = ttk.Frame(root)
    frame_path.pack(fill="x", pady=5)

    entry_path = ttk.Entry(frame_path, state="readonly")
    entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ttk.Button(frame_path, text="تصفح", command=browse).pack(side="right")

    # ---- العرض (الجودة) ----
    ttk.Label(root, text="عرض الناتج بالأعمدة (الجودة):").pack(anchor="w", pady=(10, 0))
    frame_width = ttk.Frame(root)
    frame_width.pack(fill="x", pady=5)

    width_var = tk.StringVar(value=str(DEFAULT_WIDTH))
    ttk.Spinbox(frame_width, from_=MIN_WIDTH, to=MAX_WIDTH, textvariable=width_var, width=10).pack(side="left")

    ttk.Label(
        frame_width,
        text="   (رقم أكبر = تفاصيل أدق لكن حجم أكبر)",
        foreground="#777777",
    ).pack(side="left")

    # ---- زر البدء ----
    btn_start = tk.Button(
        root,
        text="⚡ ابدأ التحويل الآن",
        command=start_process,
        bg="#00adb5",
        fg="#ffffff",
        activebackground="#007a80",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        cursor="hand2",
    )
    btn_start.pack(fill="x", pady=25)

    # ---- اللوج (الشاشة الصغيرة تحت) ----
    ttk.Label(root, text="حالة العمليات الحالية:").pack(anchor="w")

    log_text = ScrolledText(
        root,
        height=13,
        state=tk.DISABLED,
        bg="#0f111a",
        fg="#d6deeb",
        insertbackground="#ffffff",
        font=("Segoe UI", 11),
        relief="flat",
        padx=10,
        pady=10,
    )
    log_text.tag_config("info", foreground="#4FC3F7")
    log_text.tag_config("success", foreground="#00E676")
    log_text.tag_config("warning", foreground="#FFD54F")
    log_text.tag_config("error", foreground="#FF5252")
    log_text.pack(fill="both", expand=True, pady=5)

    # ---- إعداد المحرك وقياس الرموز ----
    try:
        engine = AsciiEngine(log=log_message)
    except Exception as e:
        log_message(f"❌ فشل تحميل الخط: {e}", "error")
        messagebox.showerror("خطأ", f"فشل تحميل الخط:\n{e}")

    root.mainloop()


if __name__ == "__main__":
    build_gui()
