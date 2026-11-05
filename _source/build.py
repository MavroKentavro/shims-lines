import html, re, os, shutil, pathlib

ROOT = pathlib.Path(__file__).parent
C = ROOT / "content"
OUT = ROOT / "site"

SITE = "Shim’s Lines"
INTRO = ("Привет, я Алексей Шимульский, а эти тексты — мое «безответственное творчество». "
         "Формат, в котором мне можно абсолютно все. Я разрешил себе писать сколь угодно пошло, "
         "любительски, наплевательски, исключительно для собственного удовольствия.")

LONG = [
    dict(slug="sobaka-mordoy-vverh", file="sobaka.md", title="Собака мордой вверх", sub=None),
    dict(slug="ona", file="ona.md", title="Она", sub=None),
    dict(slug="sramnye-gramoty", file="gramoty.md", title="Срамные грамоты", sub="или берестяной секстинг"),
]
SECTIONS = [
    dict(slug="places", file="places.md", title="Places", ru="Места"),
    dict(slug="side-notes", file="side-notes.md", title="Side Notes", ru="На полях"),
    dict(slug="shorts", file="shorts.md", title="Shorts", ru="Короткое"),
    dict(slug="long", file=None, title="Long", ru="Длинное"),
    dict(slug="bare-lines", file="bare-lines.md", title="Bare Lines", ru="Голые строки"),
]


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def block(b):
    lines = b.split("\n")
    if lines[0].startswith("## "):
        t = lines[0][3:].strip()
        return f'<h2 id="{slugify(t)}">{inline(t)}</h2>'
    if all(l.startswith("> ") for l in lines):
        return '<p class="cue">' + "<br>".join(inline(l[2:]) for l in lines) + "</p>"
    if all(l.startswith("- ") for l in lines):
        return "<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "</ul>"
    if all(re.match(r"\d+\. ", l) for l in lines):
        return "<ol>" + "".join(f"<li>{inline(l.split('. ',1)[1])}</li>" for l in lines) + "</ol>"
    if all(l.startswith("✓") for l in lines):
        return '<ul class="checks">' + "".join(f"<li>{inline(l[1:].strip())}</li>" for l in lines) + "</ul>"
    if lines[0].startswith("~ "):
        return f'<p class="sign">{inline(lines[0][2:])}</p>'
    return "<p>" + "<br>".join(inline(l) for l in lines) + "</p>"


TRANSLIT = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","ts","ch","sh","sch","","y","","e","yu","ya"]))


def slugify(t):
    t = t.lower()
    t = "".join(TRANSLIT.get(ch, ch) for ch in t)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def render(md):
    pieces = [p.strip() for p in re.split(r"^\*\*\*$", md, flags=re.M) if p.strip()]
    out = []
    for p in pieces:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", p) if b.strip()]
        out.append('<article class="piece">' + "\n".join(block(b) for b in blocks) + "</article>")
    return '\n<div class="orn" aria-hidden="true">⁂</div>\n'.join(out), pieces


def nav(active):
    items = "".join(
        f'<a href="{s["slug"]}.html"{" class=on" if s["slug"]==active else ""}>{s["title"]}</a>'
        for s in SECTIONS)
    return f'<header class="top"><a class="brand" href="index.html">{SITE}</a><nav>{items}</nav></header>'


def page(title, body, active=None, desc=INTRO):
    full = f"{title} — {SITE}" if title != SITE else SITE
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc[:180])}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(desc[:180])}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✒</text></svg>">
</head>
<body>
{nav(active)}
<main>
{body}
</main>
<footer class="foot">© Алексей Шимульский</footer>
</body>
</html>"""


def prevnext(slug):
    i = [s["slug"] for s in SECTIONS].index(slug)
    a = SECTIONS[i-1] if i > 0 else None
    b = SECTIONS[i+1] if i < len(SECTIONS)-1 else None
    l = f'<a href="{a["slug"]}.html">← {a["title"]}</a>' if a else "<span></span>"
    r = f'<a href="{b["slug"]}.html">{b["title"]} →</a>' if b else "<span></span>"
    return f'<div class="pn">{l}{r}</div>'


def first_line(md):
    for l in md.splitlines():
        l = l.strip()
        if l and not l.startswith((">", "#", "~")):
            l = re.sub(r"\*+", "", l)
            return (l[:140] + "…") if len(l) > 140 else l
    return ""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "style.css", OUT / "style.css")

    counts = {}
    for s in SECTIONS:
        if s["file"] is None:
            continue
        md = (C / s["file"]).read_text()
        body, pieces = render(md)
        counts[s["slug"]] = len(pieces)
        toc = ""
        if s["slug"] == "places":
            heads = re.findall(r"^## (.+)$", md, flags=re.M)
            toc = '<ul class="toc">' + "".join(f'<li><a href="#{slugify(h)}">{h}</a></li>' for h in heads) + "</ul>"
        head = f'<div class="sec-head"><h1>{s["title"]}</h1><p class="ru">{s["ru"]}</p>{toc}</div>'
        (OUT / f'{s["slug"]}.html').write_text(page(s["title"], head + body + prevnext(s["slug"]), s["slug"]))

    # long index + pages
    items = ""
    for t in LONG:
        md = (C / t["file"]).read_text()
        body, _ = render(md)
        sub = f'<p class="sub">{t["sub"]}</p>' if t["sub"] else ""
        head = f'<div class="sec-head long-head"><a class="back" href="long.html">← Long</a><h1>{t["title"]}</h1>{sub}<p class="by">Алексей Шимульский</p></div>'
        (OUT / f'{t["slug"]}.html').write_text(page(t["title"], head + body, "long", first_line(md)))
        items += f'<li><a href="{t["slug"]}.html"><span class="t">{t["title"]}</span>{"<span class=s>"+t["sub"]+"</span>" if t["sub"] else ""}<span class="ex">{html.escape(first_line(md))}</span></a></li>'
    counts["long"] = len(LONG)
    head = '<div class="sec-head"><h1>Long</h1><p class="ru">Длинное</p></div>'
    (OUT / "long.html").write_text(page("Long", head + f'<ul class="longlist">{items}</ul>' + prevnext("long"), "long"))

    # index
    def plural(n):
        if n % 10 == 1 and n % 100 != 11: return "текст"
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return "текста"
        return "текстов"
    secs = "".join(
        f'<li><a href="{s["slug"]}.html"><span class="t">{s["title"]}</span><span class="ru">{s["ru"]}</span><span class="n">{counts[s["slug"]]} {plural(counts[s["slug"]])}</span></a></li>'
        for s in SECTIONS)
    body = f'<section class="hero"><h1>{SITE}</h1><p class="intro">{INTRO}</p></section><ul class="sections">{secs}</ul>'
    (OUT / "index.html").write_text(page(SITE, body))
    print("built", sorted(os.listdir(OUT)), counts)


main()
