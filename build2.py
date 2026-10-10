# -*- coding: utf-8 -*-
"""
MAX × МИЭМ НИУ ВШЭ — генератор статического сайта.
python3 build.py
Создаёт:
  index.html   — хаб (о компании, путь сообщения, о программе, сетка вакансий, контакты)
  about.html   — источники и методика
  spec/*.html  — по странице на каждую вакансию (26 файлов)
  assets/style.css, assets/app.js
"""
# ВНИМАНИЕ: папка site/ доработана руками (favicon assets/maks.png, логотип в шапке,
# дисциплины на страницах вакансий, ссылки на вакансии, растянутая шкала соответствия).
# Повторный запуск build() перезапишет эти правки — сначала перенесите их сюда.
import os, html, shutil, re

OUT = "site"
SPEC = os.path.join(OUT, "spec")
ASSETS = os.path.join(OUT, "assets")

def esc(s):
    return html.escape(str(s), quote=True)

def clean():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(SPEC)
    os.makedirs(ASSETS)

# ============ HEADER / FOOTER ============
def page(title, body, active="", up=""):
    """up — префикс пути к корню сайта ('' для index.html, '../' для spec/*.html)."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%230b1120'/%3E%3Ctext x='50' y='68' font-size='52' font-family='Arial' font-weight='bold' fill='%2360a5fa' text-anchor='middle'%3EM%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<a class="skip" href="#main">К содержанию</a>
<div class="bg-aurora" aria-hidden="true"></div>
<div class="bg-grid" aria-hidden="true"></div>
<canvas id="particles" aria-hidden="true"></canvas>
<div class="scroll-progress" id="progress"></div>
<div class="cursor-dot" id="cDot"></div>
<div class="cursor-ring" id="cRing"></div>
<header class="topbar">
  <a class="brand" href="{up}index.html">
    <span class="brand-vk">VK</span>
    <span class="brand-text"><b>MAX</b>&nbsp;<span class="dim">× МИЭМ НИУ ВШЭ</span></span>
  </a>
  <nav class="topnav">
    <a href="{up}index.html#grid">Все специальности</a>
    <a href="{up}index.html#company">О компании</a>
    <a href="{up}index.html#program">О программе</a>
  </nav>
</header>
<main id="main" class="wrap">
{body}
</main>
<script src="{up}assets/app.js"></script>
</body>
</html>"""

# ============ HELPERS ============
def chips(arr, cls=""):
    return "".join(f'<span class="chip {cls}">{esc(t)}</span>' for t in arr)

def list_html(items, cls=""):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<ul class="list {cls}">{lis}</ul>'

# ============ HUB ============
def hub_body(D):
    C = D["company"]
    P = D["program"]
    roles = D["roles"]
    dirs = D["directions"]

    hero_stats = f"""<div class="hero-stats">
      <div class="hstat"><div class="hstat-v">{len(roles)}</div><div class="hstat-k">вакансий в каталоге</div></div>
      <div class="hstat"><div class="hstat-v">{C.get('total_professions', 59)}</div><div class="hstat-k">профессий в MAX</div></div>
      <div class="hstat"><div class="hstat-v">300+</div><div class="hstat-k">человек в команде</div></div>
      <div class="hstat"><div class="hstat-v">240 з.е.</div><div class="hstat-k">объём программы / 4 года</div></div>
    </div>"""

    facts = "".join(
        f'<div class="fact"><div class="fact-k">{esc(f[0])}</div><div class="fact-v">{esc(f[1])}</div></div>'
        for f in C["facts"]
    )

    why = "".join(f"<li><b>{esc(w[0])}:</b> {esc(w[1])}</li>" for w in C["why_interesting"])

    # путь сообщения
    journey = ""
    if D.get("messageJourney"):
        journey_steps = []
        for s in D["messageJourney"]:
            role_spans = "".join(f'<span class="j-role">{esc(r)}</span>' for r in s["roles"])
            journey_steps.append(
                f'<div class="j-step"><div class="j-num">{s["n"]}</div><div class="j-body"><div class="j-title">{esc(s["title"])}</div><div class="j-desc">{esc(s["desc"])}</div><div class="j-roles">{role_spans}</div></div></div>'
            )
        steps = "".join(journey_steps)
        journey = f"""
    <section class="card card-glow reveal" id="journey">
      <p class="kicker">Как работает MAX · путь одного сообщения</p>
      <h2>Путь сообщения через MAX: 7 этапов</h2>
      <p class="p">Одно сообщение в мессенджере проходит путь от нажатия «отправить» до аналитики — на каждом этапе работают разные специалисты. В компании {C.get("team_size", "более 300 человек")} на {C.get("specialties_count", 42)} специальностей.</p>
      <div class="journey">{steps}</div>
    </section>"""

    # о программе
    stats = "".join(
        f'<div class="stat"><div class="stat-v">{esc(s[0])}</div><div class="stat-k">{esc(s[1])}</div></div>'
        for s in P["stats"] if "бюджет" not in s[1].lower()
    )
    pfacts = "".join(
        f'<div class="fact"><div class="fact-k">{esc(f[0])}</div><div class="fact-v">{esc(f[1])}</div></div>'
        for f in P["facts"] if "125" not in f[1] and "бюджетн" not in f[1].lower()
    )
    # 8 предметов-приоритетов; к каждому — ссылки на вакансии, где он работает
    disc_roles = {}
    for rr in roles:
        for c in rr["courses"]:
            disc_roles.setdefault(c[0], []).append(rr)
    courses = "".join(
        f'<div class="map-row" id="disc-{i}"><div class="map-course">{esc(c[0])}</div>'
        f'<div class="map-why">{esc(c[1])}<br><span class="dim" style="font-size:.82rem">Вакансии: '
        + ", ".join(
            f'<a class="lnk" href="spec/{rr["id"]}.html">{esc(rr["title"])}</a>'
            for rr in disc_roles.get(c[0], [])
        )
        + "</span></div></div>"
        for i, c in enumerate(P["courses"], 1)
    )

    # сетка
    tiles = "".join(tile_html(r, dirs) for r in roles)
    filters = "".join(
        f'<button class="filter" data-filter="{d[0]}">{d[1]} · {sum(1 for r in roles if r["d"]==d[0])}</button>'
        for d in dirs
    )

    # контакты
    cc = "".join(
        f'<div class="contact"><div class="contact-kind">{esc(c[0])}</div><div class="contact-val"><a class="lnk" href="{esc(c[2])}" target="_blank" rel="noopener noreferrer">{esc(c[1])}</a></div><div class="contact-note">{esc(c[3])}</div></div>'
        for c in D["contactsCompany"]
    )
    cu = "".join(
        f'<div class="contact"><div class="contact-kind">{esc(c[0])}</div><div class="contact-val"><a class="lnk" href="{esc(c[2])}" target="_blank" rel="noopener noreferrer">{esc(c[1])}</a></div><div class="contact-note">{esc(c[3])}</div></div>'
        for c in D["contactsUniversity"]
    )

    return f"""
  <section class="hero reveal">
    <div class="hero-head">
      <div>
        <p class="kicker">Каталог вакансий</p>
        <h1><span class="accent">MAX</span> <span class="gradient-text">× МИЭМ НИУ ВШЭ</span></h1>
        <p class="lead">{esc(C["about_short"])}</p>
        <p class="p" style="margin-top:1rem;max-width:68ch">{esc(C["about_full"])}</p>
      </div>
      <div class="hero-side">
        <div class="badge">{len(roles)} вакансий MAX</div>
        <div class="badge ghost">{len(dirs)} направлений</div>
        <div class="badge status-max">каталог вакансий</div>
      </div>
    </div>
    {hero_stats}
    <div class="hero-actions">
      <a class="btn" href="#grid">Выбрать специальность →</a>
      <a class="btn ghost" href="#company">Что такое MAX</a>
      <a class="btn ghost" href="#program">Что даёт программа</a>
    </div>
  </section>

  <section class="card card-glow reveal" id="company">
    <p class="kicker">Шаг 1 · Понять компанию</p>
    <h2>Что за компания MAX</h2>
    <div class="facts">{facts}</div>
    <h3>Почему MAX интересен как работодатель</h3>
    <ul class="list check">{why}</ul>
    <div class="chips" style="margin-top:1.4rem">
      <span class="dim" style="font-size:.78rem;width:100%;margin-bottom:-.3rem">Технологический стек MAX:</span>
      {chips(C["stack"], "tech")}
    </div>
  </section>

  {journey}

  <section class="card card-glow reveal" id="program">
    <p class="kicker">Шаг 2 · Понять свою программу</p>
    <h2>ОП «{esc(P["name"])}» — {esc(P["school"])}</h2>
    <p class="p">{esc(P["form"])} · кампус: {esc(P["campus"])}</p>
    <div class="stats">{stats}</div>
    <div class="facts">{pfacts}</div>
    <h3>Топ полезных предметов и навыки</h3>
    <p class="hint" style="margin-top:.5rem">Это приоритет для подготовки к MAX, а не оценка качества предметов.</p>
    <div class="map">{courses}</div>
    <p class="hint">Связка «дисциплина → требование вакансии» — аналитическая интерпретация, а не официальная позиция НИУ ВШЭ или VK. <a class="lnk" href="{esc(P["url"])}" target="_blank" rel="noopener noreferrer">Страница программы →</a></p>
  </section>

  <section class="card card-glow reveal" id="grid">
    <p class="kicker">Шаг 3 · Выбрать специальность</p>
    <h2>{len(roles)} вакансий MAX — нажмите на плитку</h2>
    <p class="p">Все {len(roles)} ролей — реальные открытые вакансии MAX (по данным каталога VK). Плитки можно фильтровать по направлениям и искать по стеку.</p>
    <div class="toolbar">
      <input id="q" class="search" type="search" placeholder="Поиск: Java, Kubernetes, аналитик, безопасность…" aria-label="Поиск по специальностям">
      <div class="filters" id="filters">
        <button class="filter on" data-filter="all">Все · {len(roles)}</button>
        {filters}
      </div>
    </div>
    <div class="grid" id="tiles">{tiles}</div>
    <p class="empty" id="empty" hidden>Ничего не нашлось — попробуйте другой запрос.</p>
  </section>

  <section class="card reveal">
    <p class="kicker">Как пользоваться</p>
    <h2>Три сценария</h2>
    <div class="scenarios">
      <div class="scenario"><b>Я выбираю трек</b><span>Открой 3–4 плитки из разных направлений, сравни блоки «Компетенции» и «Рост» — так видно, чем роли отличаются на самом деле.</span></div>
      <div class="scenario"><b>Я готовлюсь к отклику</b><span>Возьми со страницы блоки «Требования», «Стек» и «Рост» — это готовый чек-лист для резюме и пет-проекта.</span></div>
      <div class="scenario"><b>Я выбираю дисциплины</b><span>Блок «Какие компетенции ОП работают» показывает, какие дисциплины МИЭМ усиливают конкретную роль.</span></div>
    </div>
  </section>

  <section class="card reveal">
    <p class="kicker">Шаг 4 · Выйти на контакт</p>
    <h2>Стажировки, вакансии, отклик</h2>
    <div class="contacts">{cc}</div>
    <h3>Университет: вопросы по программе</h3>
    <div class="contacts">{cu}</div>
  </section>
"""

def tile_html(r, dirs):
    d = next((x for x in dirs if x[0] == r["d"]), None)
    dn = d[1] if d else r["d"]
    stack = ", ".join(r["stack"][:4])
    st = (r["title"] + " " + r.get("short", "") + " " + " ".join(r["stack"]) + " " + dn).lower()
    return f"""<a class="tile tile-max reveal" href="spec/{r['id']}.html" data-cat="{r['d']}" data-text="{esc(st)}">
      <span class="tile-num">{r['num']}</span>
      <span class="tile-title">{esc(r['title'])}</span>
      <span class="tile-tag">{esc(dn)} · {esc(r['level'])}</span>
      <span class="tile-stack">{esc(stack)}</span>
      <span class="tile-status">вакансия MAX</span>
      <span class="tile-go">Открыть →</span>
    </a>"""

# ============ SPEC PAGE ============
def spec_body(D, r):
    P = D["program"]
    dirs = D["directions"]
    d = next((x for x in dirs if x[0] == r["d"]), None)
    dn = d[1] if d else r["d"]
    related = [D["roles"][x] for x in range(len(D["roles"])) if D["roles"][x]["id"] in r.get("related", [])]

    tasks = list_html(r["tasks"]) if r.get("tasks") else ""
    req = list_html(r["req"]) if r.get("req") else ""
    plus = f'<h3>Будет плюсом</h3>{list_html(r["plus"], "check")}' if r.get("plus") else ""
    stack = chips(r["stack"], "tech")
    courses = "".join(
        f'<div class="map-row"><div class="map-course">{esc(c[0])}</div><div class="map-why">{esc(c[1])}</div></div>'
        for c in r["courses"]
    )
    # дисциплины-приоритеты этой вакансии со ссылкой на блок-описание на главной
    disc_no = {c[0]: i for i, c in enumerate(P["courses"], 1)}
    disc = "".join(
        f'<span class="chip"><a href="../index.html#disc-{disc_no.get(c[0], 1)}">{esc(c[0])}</a></span>'
        for c in r["courses"]
    )
    growth = list_html(r["growth"], "arrow") if r.get("growth") else ""
    rel = "".join(
        f'<a class="rel" href="{rr["id"]}.html"><b>{esc(rr["title"])}</b><span>{esc(rr["short"])}</span></a>'
        for rr in related
    )

    return f"""
  <nav class="crumbs"><a href="../index.html">Все специальности</a><span>/</span><span>{esc(r["title"])}</span></nav>

  <section class="hero reveal">
    <div class="hero-head">
      <div>
        <p class="kicker">{esc(dn)} · {esc(r["level"])}</p>
        <h1>{esc(r["title"])}</h1>
        <p class="lead">{esc(r["short"])}</p>
      </div>
      <div class="hero-side">
        <div class="badge">{esc(dn)}</div>
        <div class="badge ghost">грейд: {esc(r["level"])}</div>
        <div class="badge status-max">вакансия MAX</div>
      </div>
    </div>
    <div class="fit">
      <div class="fit-label">Насколько роль ложится на ОП ИВТ</div>
      <div class="fit-bar"><span data-width="{r["fit"]}"></span></div>
      <div class="fit-note">{fit_note(r["fit"])}</div>
    </div>
    <div class="hiring role-status-max" style="margin-top:1.2rem">
      <span class="hiring-dot"></span>
      <div><b>Статус найма:</b> подтверждённая вакансия MAX уровня {esc(r["level"])}</div>
    </div>
  </section>

  {f'<section class="card card-glow reveal" id="what"><p class="kicker">Чем занимается</p><h2>Задачи и что реально делают руками</h2>{tasks}</section>' if tasks else ''}

  <section class="card card-glow reveal" id="req">
    <p class="kicker">Что нужно знать</p>
    <h2>Требования</h2>
    {req}
    {plus}
  </section>

  <section class="card card-glow reveal" id="stack">
    <p class="kicker">Инструменты</p>
    <h2>Технологический стек</h2>
    <div class="chips">{stack}</div>
  </section>

  <section class="card card-glow reveal" id="program">
    <p class="kicker">Связка с ОП ИВТ</p>
    <h2>Какие компетенции ОП МИЭМ на это работают</h2>
    <div class="map">{courses}</div>
    <p class="disc-label"><b>Дисциплины программы, которые работают на эту вакансию:</b></p>
    <p class="disc">{disc}</p>
    <div class="fit" style="margin-top:1rem">
      <div class="fit-label">Соответствие программе</div>
      <div class="fit-bar"><span data-width="{r["fit"]}"></span></div>
    </div>
  </section>

  <section class="card card-glow reveal" id="growth">
    <p class="kicker">Карьера</p>
    <h2>Как выглядит рост в роли</h2>
    {growth}
  </section>

  <section class="card reveal">
    <p class="kicker">Куда ещё смотреть</p>
    <h2>Похожие роли</h2>
    <div class="related">{rel}</div>
  </section>

  <div class="pager">
    <a class="btn" href="../index.html">← Ко всем специальностям</a>
  </div>
"""

def fit_note(p):
    if p >= 75: return "Прямое попадание: дисциплины ОП закрывают большую часть требований — остальное добирается на практике и стажировке."
    if p >= 60: return "Хорошее соответствие: база из программы есть, конкретный стек осваивается на практике."
    if p >= 50: return "Частичное соответствие: часть требований закрывается программой, часть — майнором, пет-проектом и стажировкой."
    return "Базовое соответствие: программа даёт фундамент, специфика роли добирается самостоятельно."

# ============ ONE-PAGE (всё в одном файле) ============
def inner_ids(body, rid):
    """Уникализируем id внутри страницы вакансии (program встречается на хабе)."""
    return re.sub(r'id="(what|req|stack|program|growth)"', lambda m: f'id="spec-{rid}-{m.group(1)}"', body)

def local_links(body):
    """Внешние ссылки между страницами -> якоря внутри одного документа."""
    body = re.sub(r'href="(?:\.\./)?index\.html(#[^"]*)?"', lambda m: f'href="{m.group(1) or "#grid"}"', body)
    body = re.sub(r'href="(?:\.\./)?spec/([a-z0-9\-]+)\.html"', r'href="#spec-\1"', body)
    body = re.sub(r'href="(?!https?:|#|mailto:|tel:)([a-z0-9\-]+)\.html"', r'href="#spec-\1"', body)
    return body

def onepage_body(D):
    parts = ['<a id="top"></a>', local_links(hub_body(D))]
    for r in D["roles"]:
        rid = r["id"]
        body = local_links(inner_ids(spec_body(D, r), rid))
        parts.append(
            f'\n  <div class="onepage-sep" aria-hidden="true"></div>\n'
            f'  <section class="onepage-spec" id="spec-{rid}">{body}</section>'
        )
    return "\n".join(parts)

def onepage(D):
    with open(os.path.join(ASSETS, "style.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ASSETS, "app.js"), encoding="utf-8") as f:
        js = f.read()
    nav = "".join(
        f'<a href="#spec-{r["id"]}">{esc(r["title"])}</a>' for r in D["roles"]
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAX × МИЭМ НИУ ВШЭ — весь сайт одним файлом</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%230b1120'/%3E%3Ctext x='50' y='68' font-size='52' font-family='Arial' font-weight='bold' fill='%2360a5fa' text-anchor='middle'%3EM%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<a class="skip" href="#main">К содержанию</a>
<div class="bg-aurora" aria-hidden="true"></div>
<div class="bg-grid" aria-hidden="true"></div>
<canvas id="particles" aria-hidden="true"></canvas>
<div class="scroll-progress" id="progress"></div>
<div class="cursor-dot" id="cDot"></div>
<div class="cursor-ring" id="cRing"></div>
<header class="topbar">
  <a class="brand" href="#top">
    <span class="brand-vk">VK</span>
    <span class="brand-text"><b>MAX</b>&nbsp;<span class="dim">× МИЭМ НИУ ВШЭ</span></span>
  </a>
  <nav class="topnav">
    <a href="#grid">Все специальности</a>
    <a href="#company">О компании</a>
    <a href="#program">О программе</a>
  </nav>
</header>
<nav class="onepage-nav" aria-label="Быстрый переход к вакансиям">
  <span class="onepage-nav-t">Вакансии:</span>{nav}
</nav>
<main id="main" class="wrap">
{onepage_body(D)}
</main>
<script>
{js}
</script>
</body>
</html>"""

# ============ BUILD ============
def build(D):
    clean()
    # assets: style.css и app.js лежат в корне проекта (assets/)
    for name in ("style.css", "app.js"):
        src, dst = os.path.join("assets", name), os.path.join(ASSETS, name)
        if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
            shutil.copyfile(src, dst)
    # хаб
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("MAX × МИЭМ НИУ ВШЭ — вакансии и компетенции ОП ИВТ", hub_body(D)))
    # spec страницы
    for r in D["roles"]:
        body = spec_body(D, r)
        with open(os.path.join(SPEC, f"{r['id']}.html"), "w", encoding="utf-8") as f:
            f.write(page(f"{r['title']} в MAX — требования, стек, компетенции ОП ИВТ", body, up="../"))
    # всё в одном файле
    with open(os.path.join(OUT, "all.html"), "w", encoding="utf-8") as f:
        f.write(onepage(D))
    print(f"OK: index.html + {len(D['roles'])} spec-страниц + all.html (всё в одном)")

if __name__ == "__main__":
    from data import DATA
    build(DATA)