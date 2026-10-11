<div align="center">

# 🎨 ASCII ART PRO

### محوّل الصور إلى فن ASCII — Image to ASCII Art Converter

[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-exe-0078D6?logo=windows&logoColor=white)](https://github.com/masterV00-hub/ascii-art-pro/releases/latest)

### ⬇️ [تحميل البرنامج — Download EXE](https://github.com/masterV00-hub/ascii-art-pro/releases/latest)

**حوّل أي صورة إلى لوحة ASCII ملوّنة (نص + HTML + ANSI) بضغطة واحدة.**

**Turn any image into colored ASCII art (text + HTML + ANSI) in one click.**

</div>

---

<div align="center">

## 🌍 اختار اللغة — Choose Language

### [🇪🇬 العربية](#-النسخة-العربية) &nbsp;&nbsp;|&nbsp;&nbsp; [🇬🇧 English](#-english-version)

</div>

---

<a id="-النسخة-العربية"></a>

<div dir="rtl">

## 🇪🇬 النسخة العربية

### 📖 الفكرة

**ASCII ART PRO** برنامج ويندوز بواجهة داكنة يحوّل الصور إلى فن ASCII: يقيس كثافة كل رمز بنفس الخط فعلياً ويختار الأنسب لكل جزء من الصورة، مع إبراز الحواف (Sobel) لتحافظ النتيجة على التفاصيل.

### ✨ المميزات

- 🔤 أكثر من 220 رمزاً: لاتيني + سيريلي + يوناني + أرقام + رموز + Box Drawing
- 🎯 قياس كثافة الرموز تلقائياً بدل الترتيب الثابت
- 🖼️ صورة واحدة أو مجلد كامل دفعة واحدة
- 📦 إخراج ثلاثي لكل صورة: `.txt` + `.html` ملوّن + `.ansi` ملوّن 24-bit
- ⚙️ عرض قابل للضبط (40–500 عمود)
- 🪟 نسخة exe لا تحتاج بايثون (الخط مدمج)

### 🚀 التشغيل

**الأسهل:** حمّل `ASCII_ART_PRO.exe` من [صفحة الإصدارات](https://github.com/masterV00-hub/ascii-art-pro/releases/latest) وشغّله.

**من المصدر:**

```bash
pip install -r requirements.txt
python main.py
```

**إعادة بناء الـ exe:**

```bash
pyinstaller --noconfirm --onefile --windowed --name ASCII_ART_PRO --icon icon.ico --add-data "consola.ttf;." main.py
```

### 📁 الهيكل

```
ascii-art-pro/
├── main.py               # البرنامج (المحرك + الواجهة)
├── consola.ttf           # الخط المدمج
├── icon.ico              # الأيقونة
├── ASCII_ART_PRO.spec    # إعداد PyInstaller
├── requirements.txt
└── README.md
```

### 🔧 الإعدادات

في بداية `main.py`:

| الثابت | الوظيفة | الافتراضي |
|---|---|---|
| `DEFAULT_WIDTH` | العرض بالأعمدة | 200 |
| `EDGE_WEIGHT` | قوة إبراز الحواف | 0.35 |
| `LOCAL_CONTRAST` | التباين المحلي | 0.45 |
| `SHARPEN` | الحدة | 0.9 |

</div>

---

<a id="-english-version"></a>

## 🇬🇧 English Version

### 📖 Overview

**ASCII ART PRO** is a Windows app with a dark UI that converts images to ASCII art: it measures each glyph's ink density with the actual font and picks the best match per image block, with Sobel edge enhancement to preserve detail.

### ✨ Features

- 🔤 220+ glyphs: latin + cyrillic + greek + digits + symbols + box drawing
- 🎯 Measured glyph density instead of fixed ordering
- 🖼️ Single image or whole folder batch mode
- 📦 Triple output per image: `.txt` + colored `.html` + 24-bit `.ansi`
- ⚙️ Adjustable width (40–500 columns)
- 🪟 Standalone exe, no Python needed (font bundled)

### 🚀 Run

**Easiest:** download `ASCII_ART_PRO.exe` from [Releases](https://github.com/masterV00-hub/ascii-art-pro/releases/latest) and run it.

**From source:**

```bash
pip install -r requirements.txt
python main.py
```

**Rebuild the exe:**

```bash
pyinstaller --noconfirm --onefile --windowed --name ASCII_ART_PRO --icon icon.ico --add-data "consola.ttf;." main.py
```

### 📁 Structure

```
ascii-art-pro/
├── main.py               # App (engine + GUI)
├── consola.ttf           # Bundled font
├── icon.ico              # Icon
├── ASCII_ART_PRO.spec    # PyInstaller config
├── requirements.txt
└── README.md
```

### 🔧 Settings

At the top of `main.py`:

| Constant | Purpose | Default |
|---|---|---|
| `DEFAULT_WIDTH` | Width in columns | 200 |
| `EDGE_WEIGHT` | Edge emphasis | 0.35 |
| `LOCAL_CONTRAST` | Local contrast | 0.45 |
| `SHARPEN` | Sharpness | 0.9 |

---

<div align="center">

### [⬆️ back to top / العودة للأعلى](#-ascii-art-pro)

MIT License.

</div>
