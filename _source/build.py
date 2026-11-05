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
    return '\n<hr>\n'.join(out), pieces


DOC = '<svg class="doc" viewBox="0 0 16 16" aria-hidden="true"><path d="M4.35 1.5h4.9l3.25 3.25v8.4c0 .75-.6 1.35-1.35 1.35h-6.8c-.75 0-1.35-.6-1.35-1.35V2.85c0-.75.6-1.35 1.35-1.35Z" fill="none" stroke="currentColor" stroke-width="1.1"/><path d="M9 1.7v3.3h3.3M5.5 8.2h5M5.5 10.6h5" fill="none" stroke="currentColor" stroke-width="1.1"/></svg>'
PEN = '<svg class="pen" viewBox="0 0 24 24" aria-hidden="true"><path d="M15.2 3.6a2.2 2.2 0 0 1 3.1 0l2.1 2.1a2.2 2.2 0 0 1 0 3.1L9.5 19.7l-5.6 1.1 1.1-5.6L15.2 3.6Z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="m13.5 5.3 5.2 5.2" stroke="currentColor" stroke-width="1.6"/></svg>'


def crumbs(trail):
    parts = ['<a href="index.html">' + PEN.replace('class="pen"','class="pen sm"') + SITE + '</a>']
    for href, title in trail:
        parts.append(f'<a href="{href}">{title}</a>' if href else f'<span>{title}</span>')
    return '<header class="top">' + '<span class="sl">/</span>'.join(parts) + '</header>'


def pagelink(href, title, sub=None):
    s2 = f' <span class="g">— {sub}</span>' if sub else ''
    return f'<a class="pagelink" href="{href}">{DOC}<span class="pl">{title}</span>{s2}</a>'


def page(title, body, trail=(), desc=INTRO):
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
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✒</text></svg>">
</head>
<body>
{crumbs(trail)}
<main>
{body}
</main>
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
        head = f'<h1 class="title">{s["title"]}</h1>'
        (OUT / f'{s["slug"]}.html').write_text(page(s["title"], head + body, [(None, s["title"])]))

    # long index + pages
    items = ""
    for t in LONG:
        md = (C / t["file"]).read_text()
        body, _ = render(md)
        sub = f'<p class="g sub"><i>{t["sub"]}</i></p>' if t["sub"] else ""
        head = f'<h1 class="title">{t["title"]}</h1>{sub}<p class="g by">Алексей Шимульский</p>'
        (OUT / f'{t["slug"]}.html').write_text(page(t["title"], head + body, [("long.html", "Long"), (None, t["title"])], first_line(md)))
        items += pagelink(f'{t["slug"]}.html', t["title"])
    counts["long"] = len(LONG)
    head = '<h1 class="title">Long</h1>'
    (OUT / "long.html").write_text(page("Long", head + items, [(None, "Long")]))

    # index
    secs = "".join(pagelink(f'{s["slug"]}.html', s["title"]) for s in SECTIONS)
    body = f'<div class="icon">{PEN}</div><h1 class="title">{SITE}</h1><p>{INTRO}</p><p class="gap"></p>{secs}'
    (OUT / "index.html").write_text(page(SITE, body))
    print("built", sorted(os.listdir(OUT)), counts)


main()
