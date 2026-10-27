# -*- coding: utf-8 -*-
"""Внутренний портал ОГАУЗ «Медсанчасть ИАПО» — прототип по ТЗ ред. 11.
FastAPI + SQLite + Jinja2. Запуск: uvicorn app:app --host 0.0.0.0 --port 8000 (из папки portal)."""
import datetime, secrets, hashlib, os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from db import get_db, init_db, hash_pw, NS_CHARACTERS, NS_SEGMENT_HINT, HD_CATEGORIES

init_db()
app = FastAPI(title="Портал МСЧ ИАПО")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("PORTAL_SECRET", "dev-secret-change-in-prod"),
    max_age=8 * 3600,
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

TODAY = datetime.date(2026, 10, 28)

ROLE_NAMES = {
    "admin": "Администратор системы", "quality": "Менеджер качества", "hd_it": "Оператор HelpDesk IT",
    "hd_ahch": "Оператор HelpDesk АХЧ", "hd_mt": "Оператор HelpDesk МедТехника", "chief": "Главный врач",
    "deputy": "Заместитель главного врача", "head": "Руководитель подразделения", "employee": "Сотрудник",
    "hr": "Кадровая служба", "peo": "ПЭО / специалист по закупкам", "signer": "Подписант УКЭП",
    "mse": "Регистратор МСЭ", "pharmacy": "Аптека",
}

# какие «ролевые» разделы видны какой роли (пустой тег в меню = всем). "*" = все разделы.
ROLE_VIS = {
    "admin":   ["*"],
    "quality": ["НС", "Опросы", "Чек-листы аудитов", "Протоколы/поручения", "Согласование/УКЭП"],
    "hd_it":   ["HelpDesk", "IT-инфраструктура / медоборудование", "НС"],
    "hd_ahch": ["HelpDesk", "НС"],
    "hd_mt":   ["HelpDesk", "IT-инфраструктура / медоборудование", "НС"],
    "chief":   ["*"],
    "deputy":  ["Согласование/УКЭП", "Закупки", "Протоколы/поручения", "ГО и ЧС", "Опросы", "Аккредитация/допуски", "НС"],
    "head":    ["Согласование/УКЭП", "НС", "Протоколы/поручения", "Аккредитация/допуски", "Чек-листы аудитов", "HelpDesk"],
    "employee":["HelpDesk", "НС", "Согласование/УКЭП"],
    "hr":      ["HR", "Аккредитация/допуски"],
    "peo":     ["Закупки", "Согласование/УКЭП"],
    "signer":  ["Согласование/УКЭП", "Закупки"],
    "mse":     ["МСЭ"],
    "pharmacy":["Формуляр ЛС"],
}

ROLE_MENU = [
    ("", "Главная", "/"),
    ("", "Телефонный справочник", "/phonebook"),
    ("", "Приказы", "/orders"),
    ("", "СОПы", "/sops"),
    ("", "Нормативные документы", "/docs"),
    ("HelpDesk", "Заявки HelpDesk", "/helpdesk"),
    ("НС", "Нежелательные события", "/ns"),
    ("Согласование/УКЭП", "Согласование и ходатайства", "/requests"),
    ("Закупки", "Договоры и закупки", "/procurement"),
    ("", "Бронирование залов", "/halls"),
    ("", "Объявления", "/notices"),
    ("", "Дежурства и календарь", "/calendar"),
    ("ГО и ЧС", "ГО и ЧС", "/go-chs"),
    ("Протоколы/поручения", "Протоколы и поручения", "/protocols"),
    ("Аккредитация/допуски", "Сроки документов", "/deadlines"),
    ("HR", "HR-модуль", "/hr"),
    ("Опросы", "Опросы", "/surveys"),
    ("Чек-листы аудитов", "Аудиты", "/audits"),
    ("Формуляр ЛС", "Формуляр лекарств", "/drugs"),
    ("МСЭ", "Документы МСЭ", "/mse"),
    ("IT-инфраструктура / медоборудование", "Учёт техники", "/assets"),
    ("", "Я новенький", "/newbie"),
    ("Мои показатели", "Личный кабинет", "/dashboard"),
    ("Уведомления", "Уведомления", "/notifications"),
    ("Администрирование", "Админ-панель", "/admin"),
]

def current_user(request):
    uid = request.session.get("uid")
    if not uid:
        return None
    con = get_db()
    u = con.execute("SELECT * FROM users WHERE id=? AND active=1", (uid,)).fetchone()
    con.close()
    return u

def ctx(request, user=None, template=None, **kw):
    if user is None:
        user = current_user(request)
    unread = 0
    if user:
        con = get_db()
        unread = con.execute("SELECT COUNT(*) c FROM notification WHERE user_id=? AND read=0", (user["id"],)).fetchone()["c"]
        con.close()
    kw.setdefault("q", "")
    kw.setdefault("flash", "")
    data = dict(user=user, unread=unread, today=str(TODAY), menu=ROLE_MENU,
                role_names=ROLE_NAMES, role_vis=ROLE_VIS, **kw)
    name = template if template else (kw.get("section", "index").lower().replace(" ", "_") + ".html")
    return templates.TemplateResponse(request=request, name=name, context=data)

@app.exception_handler(HTTPException)
async def http_exc_page(request: Request, exc: HTTPException):
    """Страница ошибки вместо JSON — с навигацией портала, если пользователь авторизован."""
    u = current_user(request)
    return templates.TemplateResponse(request, "error.html",
        dict(user=u, unread=0, today=str(TODAY), menu=ROLE_MENU, role_names=ROLE_NAMES,
             role_vis=ROLE_VIS, q="", flash="", code=exc.status_code, detail=exc.detail),
        status_code=exc.status_code)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    con = get_db()
    u = con.execute("SELECT * FROM users WHERE username=? AND active=1", (username,)).fetchone()
    ok = u and u["pw_hash"] == hash_pw(password, u["salt"])[0]
    if not u or not ok:
        con.execute("INSERT INTO security_log VALUES(NULL,datetime('now','localtime'),?, 'неудачный вход', ?)",
                    (username, request.client.host if request.client else "-"))
        con.commit(); con.close()
        return templates.TemplateResponse(request, "login.html", {"error": "Неверный логин или пароль"}, status_code=401)
    fails = con.execute("SELECT COUNT(*) c FROM security_log WHERE user=? AND action='неудачный вход' AND ts > datetime('now','localtime','-15 minutes')", (username,)).fetchone()["c"]
    if fails >= 5:
        con.close()
        return templates.TemplateResponse(request, "login.html", {"error": "Учётная запись временно заблокирована на 15 минут (политика паролей, п. 6 ТЗ)"}, status_code=423)
    con.execute("INSERT INTO security_log VALUES(NULL,datetime('now','localtime'),?, 'вход', ?)", (username, request.client.host if request.client else "-"))
    con.commit(); con.close()
    request.session["uid"] = u["id"]
    if u["must_change_pw"]:
        return RedirectResponse("/change-password?first=1", status_code=302)
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

@app.get("/change-password", response_class=HTMLResponse)
def change_page(request: Request, first: int = 0):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(request, "change_password.html",
        {"user": u, "first": first, "menu": ROLE_MENU, "role_names": ROLE_NAMES, "role_vis": ROLE_VIS,
         "unread": 0, "today": str(TODAY), "q": "", "flash": ""})

@app.post("/change-password")
def change_post(request: Request, old: str = Form(...), new: str = Form(...)):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    base_ctx = {"user": u, "menu": ROLE_MENU, "role_names": ROLE_NAMES, "role_vis": ROLE_VIS,
                "unread": 0, "today": str(TODAY), "q": "", "flash": ""}
    if len(new) < 8 or new.islower() or new.isupper() or not any(c.isdigit() for c in new):
        return templates.TemplateResponse(request, "change_password.html",
            {**base_ctx, "first": 0, "error": "Пароль должен быть не менее 8 символов, содержать разные регистры и цифры (п. 6 ТЗ)"}, status_code=400)
    con = get_db()
    if u["pw_hash"] != hash_pw(old, u["salt"])[0]:
        con.close()
        return templates.TemplateResponse(request, "change_password.html",
            {**base_ctx, "first": 0, "error": "Текущий пароль указан неверно"}, status_code=400)
    h, s = hash_pw(new)
    con.execute("UPDATE users SET pw_hash=?, salt=?, must_change_pw=0 WHERE id=?", (h, s, u["id"]))
    con.commit(); con.close()
    return RedirectResponse("/?pwd=ok", status_code=302)

# ---------- Главная ----------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    news = con.execute("SELECT * FROM news ORDER BY created_at DESC").fetchall()
    duty = con.execute("SELECT * FROM duty WHERE day=?", (str(TODAY),)).fetchall()
    links = con.execute("SELECT * FROM ext_links").fetchall()
    bdays = con.execute("SELECT fio, birth_month_day FROM users WHERE substr(birth_month_day,1,2)=? ORDER BY birth_month_day", (f"{TODAY.month:02d}",)).fetchall()
    events = con.execute("SELECT * FROM booking WHERE bdate>=? ORDER BY bdate,btime LIMIT 5", (str(TODAY),)).fetchall()
    con.close()
    return ctx(request, news=news, duty=duty, links=links, bdays=bdays, events=events, template="index.html", section="Главная")

# ---------- Поиск ----------
@app.get("/search", response_class=HTMLResponse)
def search(request: Request, q: str = ""):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    res = []
    if q:
        like = f"%{q}%"
        con = get_db()
        for t, sql in [("Заявка", "SELECT summary FROM ticket WHERE summary LIKE ? OR description LIKE ?"),
                       ("НС", "SELECT description FROM ns_event WHERE description LIKE ? OR character LIKE ?"),
                       ("СОП", "SELECT title FROM sop WHERE title LIKE ? OR code LIKE ?"),
                       ("Приказ", "SELECT title FROM orders WHERE title LIKE ? OR num LIKE ?"),
                       ("Подразделение", "SELECT name FROM departments WHERE name LIKE ?"),
                       ("Справочник", "SELECT fio FROM phonebook WHERE fio LIKE ? OR phone LIKE ?")]:
            n = sql.count("?")
            for r in con.execute(sql, (like,) * n).fetchall():
                res.append((t, list(r)[0]))
        con.close()
    return ctx(request, q=q, results=res[:50], template="search.html", section="Поиск")

# ---------- Телефонный справочник ----------
@app.get("/phonebook", response_class=HTMLResponse)
def phonebook(request: Request, q: str = "", dept: int = 0):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    sql = """SELECT p.*, d.name dept_name FROM phonebook p LEFT JOIN departments d ON d.id=p.dept_id WHERE 1=1"""
    args = []
    if q:
        sql += " AND (p.fio LIKE ? OR p.phone LIKE ? OR p.room LIKE ?)"; args += [f"%{q}%"] * 3
    if dept:
        sql += " AND p.dept_id=?"; args.append(dept)
    rows = con.execute(sql + " ORDER BY d.name, p.fio", args).fetchall()
    depts = con.execute("SELECT * FROM departments ORDER BY name").fetchall()
    con.close()
    return ctx(request, rows=rows, depts=depts, q=q, dept=dept, template="phonebook.html", section="Телефонный справочник")

# ---------- Приказы + ознакомление ----------
@app.get("/orders", response_class=HTMLResponse)
def orders(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM orders ORDER BY odate DESC").fetchall()
    mz = con.execute("""SELECT m.*, o.num inner_num FROM minzdrav_order m LEFT JOIN orders o ON o.id=m.inner_order_id""").fetchall()
    read_ids = {r["doc_id"] for r in con.execute("SELECT doc_id FROM read_log WHERE doc_kind='order' AND user_id=?", (u["id"],)).fetchall()}
    con.close()
    return ctx(request, rows=rows, mz=mz, read_ids=read_ids, template="orders.html", section="Приказы организации")

@app.post("/orders/{oid}/read")
def order_read(request: Request, oid: int):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    if not con.execute("SELECT 1 FROM read_log WHERE doc_kind='order' AND doc_id=? AND user_id=?", (oid, u["id"])).fetchone():
        con.execute("INSERT INTO read_log(doc_kind,doc_id,user_id,read_at) VALUES('order',?,?,datetime('now','localtime'))", (oid, u["id"]))
        con.commit()
    con.close()
    return RedirectResponse("/orders", status_code=302)

# ---------- СОПы ----------
@app.get("/sops", response_class=HTMLResponse)
def sops(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM sop ORDER BY effective_date DESC").fetchall()
    read_ids = {r["doc_id"] for r in con.execute("SELECT doc_id FROM read_log WHERE doc_kind='sop' AND user_id=?", (u["id"],)).fetchall()}
    linked_ns = {}
    for r in rows:
        linked_ns[r["id"]] = con.execute("SELECT id,description,status FROM ns_event WHERE sop_id=?", (r["id"],)).fetchall()
    con.close()
    return ctx(request, rows=rows, read_ids=read_ids, linked_ns=linked_ns, template="sops.html", section="СОПы",
               statuses={"registered": "зарегистрировано", "processing": "в отработке",
                         "analyzed": "проанализировано", "closed": "закрыто"})

@app.post("/sops/{sid}/read")
def sop_read(request: Request, sid: int):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    if not con.execute("SELECT 1 FROM read_log WHERE doc_kind='sop' AND doc_id=? AND user_id=?", (sid, u["id"])).fetchone():
        con.execute("INSERT INTO read_log(doc_kind,doc_id,user_id,read_at) VALUES('sop',?,?,datetime('now','localtime'))", (sid, u["id"]))
        con.commit()
    con.close()
    return RedirectResponse("/sops", status_code=302)

# ---------- НД библиотека ----------
@app.get("/docs", response_class=HTMLResponse)
def docs(request: Request, q: str = ""):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM md_doc WHERE title LIKE ? ORDER BY effective_date DESC", (f"%{q}%",)).fetchall()
    con.close()
    return ctx(request, rows=rows, q=q, template="docs.html", section="Библиотека нормативных документов")

# ---------- HelpDesk ----------
SEG_TITLES = {"it": "IT (АСУ)", "ahch": "АХЧ", "mt": "МедТехника"}
OP_ROLE = {"it": "hd_it", "ahch": "hd_ahch", "mt": "hd_mt"}

@app.get("/helpdesk", response_class=HTMLResponse)
def helpdesk(request: Request, seg: str = ""):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    mine = con.execute("SELECT * FROM ticket WHERE author_id=? ORDER BY created_at DESC", (u["id"],)).fetchall()
    queue = []
    if u["role_key"] in OP_ROLE.values():
        myseg = [k for k, v in OP_ROLE.items() if v == u["role_key"]][0]
        queue = con.execute("SELECT * FROM ticket WHERE segment=? AND status NOT IN ('closed') ORDER BY created_at", (myseg,)).fetchall()
    elif u["role_key"] == "admin":
        queue = con.execute("SELECT * FROM ticket WHERE status NOT IN ('closed') ORDER BY created_at").fetchall()
    all_t = con.execute("""SELECT t.*, d.name dept_name, a.fio author_fio FROM ticket t
                          LEFT JOIN departments d ON d.id=t.dept_id LEFT JOIN users a ON a.id=t.author_id
                          ORDER BY t.created_at DESC""").fetchall()
    if seg:
        all_t = [t for t in all_t if t["segment"] == seg]
    cats = HD_CATEGORIES
    con.close()
    return ctx(request, mine=mine, queue=queue, tickets=all_t, cats=cats, seg=seg,
               seg_titles=SEG_TITLES, statuses={"created": "создана", "accepted": "принята", "in_work": "в работе",
                                                "done": "выполнена", "closed": "закрыта", "returned": "возвращена"}, template="helpdesk.html", section="HelpDesk")

@app.post("/helpdesk/new")
def hd_new(request: Request, segment: str = Form(...), summary: str = Form(...),
           description: str = Form(""), room: str = Form(""), asset_ref: str = Form("")):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    cats = HD_CATEGORIES.get(segment)
    if not cats:
        raise HTTPException(400, "Неизвестный сегмент заявки")
    category = cats[0]
    con = get_db()
    cur_ins = con.execute("""INSERT INTO ticket(segment,category,summary,description,dept_id,room,asset_ref,author_id,status,sla_hours,created_at)
                   VALUES(?,?,?,?,?,?,?,?,'created',24,datetime('now','localtime'))""",
                (segment, category, summary, description, u["dept_id"], room, asset_ref, u["id"]))
    tid = cur_ins.lastrowid
    op_role = OP_ROLE[segment]
    op = con.execute("SELECT id FROM users WHERE role_key=? AND active=1 LIMIT 1", (op_role,)).fetchone()
    if op:
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (op["id"], f"Новая заявка #{tid} [{SEG_TITLES[segment]}]: {summary}", "/helpdesk"))
    con.commit(); con.close()
    return RedirectResponse("/helpdesk?tab=mine", status_code=302)

@app.post("/helpdesk/{tid}/status")
def hd_status(request: Request, tid: int, status: str = Form(...)):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    t = con.execute("SELECT * FROM ticket WHERE id=?", (tid,)).fetchone()
    allowed = u["role_key"] in OP_ROLE.values() or u["role_key"] == "admin"
    if not allowed:
        con.close(); raise HTTPException(403, "Менять статус заявки могут только операторы сегментов")
    con.execute("UPDATE ticket SET status=?, closed_at=CASE WHEN ?='closed' THEN datetime('now','localtime') ELSE closed_at END WHERE id=?",
                (status, status, tid))
    if status == "closed" and t["ns_id"]:
        ns = con.execute("SELECT author_id FROM ns_event WHERE id=?", (t["ns_id"],)).fetchone()
        if ns:
            con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                        (ns["author_id"], f"Связанная заявка #{tid} закрыта — проверьте карточку НС №{t['ns_id']}", "/ns"))
    con.commit(); con.close()
    return RedirectResponse("/helpdesk", status_code=302)

# ---------- НС ----------
@app.get("/ns", response_class=HTMLResponse)
def ns_list(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("""SELECT n.*, d.name dept_name, a.fio author_fio, s.code sop_code FROM ns_event n
                          LEFT JOIN departments d ON d.id=n.dept_id LEFT JOIN users a ON a.id=n.author_id
                          LEFT JOIN sop s ON s.id=n.sop_id ORDER BY n.created_at DESC""").fetchall()
    mine = con.execute("SELECT * FROM ns_event WHERE author_id=? ORDER BY created_at DESC", (u["id"],)).fetchall()
    stats = con.execute("SELECT character, COUNT(*) c FROM ns_event GROUP BY character ORDER BY c DESC").fetchall()
    by_dept = con.execute("""SELECT d.name, COUNT(*) c FROM ns_event n JOIN departments d ON d.id=n.dept_id GROUP BY d.name""").fetchall()
    sops = con.execute("SELECT * FROM sop ORDER BY title").fetchall()
    chars = NS_CHARACTERS; hints = NS_SEGMENT_HINT
    is_quality = u["role_key"] in ("quality", "admin", "chief")
    depts = con.execute("SELECT id,name FROM departments ORDER BY name").fetchall()
    users_q = con.execute("SELECT id,fio FROM users WHERE active=1 ORDER BY fio").fetchall()
    con.close()
    return ctx(request, rows=rows, mine=mine, stats=stats, by_dept=by_dept, sops=sops, chars=chars, hints=hints,
               is_quality=is_quality, depts=depts, all_users=users_q, hd_cats=HD_CATEGORIES, seg_titles=SEG_TITLES,
               statuses={"registered": "зарегистрировано", "processing": "в отработке",
                                                "closed": "закрыто"}, template="ns.html", section="Нежелательные события")

@app.post("/ns/new")
def ns_new(request: Request, event_date: str = Form(...), dept_id: int = Form(0), character: str = Form(...),
           description: str = Form(...), persons: str = Form(""), sop_id: int = Form(0),
           make_ticket: str = Form(""), ticket_segment: str = Form("")):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    cur = con.execute("""INSERT INTO ns_event(event_date,dept_id,character,description,persons,sop_id,author_id,status,created_at)
                         VALUES(?,?,?,?,?,?,?, 'registered', datetime('now','localtime'))""",
                      (event_date, dept_id or None, character, description, persons, sop_id or None, u["id"]))
    nsid = cur.lastrowid
    # менеджер качества получает уведомление
    q = con.execute("SELECT id FROM users WHERE role_key='quality' LIMIT 1").fetchone()
    if q:
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (q["id"], f"Зарегистрировано новое НС №{nsid} ({character})", "/ns"))
    if make_ticket == "yes" and ticket_segment in HD_CATEGORIES:
        ct = con.execute("""INSERT INTO ticket(segment,category,summary,description,dept_id,author_id,status,sla_hours,created_at,ns_id)
                            VALUES(?,?,?,?,?,?, 'created', 24, datetime('now','localtime'), ?)""",
                         (ticket_segment, character, f"Заявка из НС №{nsid}", description, dept_id or None, u["id"], nsid))
        con.execute("UPDATE ns_event SET linked_ticket_id=? WHERE id=?", (ct.lastrowid, nsid))
    con.commit(); con.close()
    return RedirectResponse("/ns", status_code=302)

@app.post("/ns/{nid}/process")
def ns_process(request: Request, nid: int, responsible_id: int = Form(0), due_date: str = Form(""),
               conclusion: str = Form(""), measures: str = Form(""), status: str = Form("processing")):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    if u["role_key"] not in ("quality", "admin"):
        raise HTTPException(403, "Отработка НС — права менеджера качества")
    con = get_db()
    con.execute("""UPDATE ns_event SET responsible_id=?, due_date=?, conclusion=?, measures=?, status=? WHERE id=?""",
                (responsible_id or None, due_date or None, conclusion or None, measures or None, status, nid))
    ev = con.execute("SELECT author_id FROM ns_event WHERE id=?", (nid,)).fetchone()
    if ev:
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (ev["author_id"], f"НС №{nid}: статус изменён на «{status}»", "/ns"))
    con.commit(); con.close()
    return RedirectResponse("/ns", status_code=302)

# ---------- Согласования и ходатайства (маршруты + УКЭП) ----------
STAGE_NAMES = {"initiator": "Инициатор", "executor": "Исполнитель", "head": "Заведующий отделением",
               "deputy": "Заместитель гл. врача", "chief": "Главный врач", "procurement": "Специалист по закупкам",
               "accounting": "Бухгалтерия", "peo": "ПЭО", "commission": "Комиссия по способу закупки",
               "head_mid": "Главная медицинская сестра"}

@app.get("/requests", response_class=HTMLResponse)
def requests_list(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("""SELECT r.*, d.name dept_name, a.fio author_fio FROM request r
                          LEFT JOIN departments d ON d.id=r.dept_id LEFT JOIN users a ON a.id=r.author_id
                          ORDER BY r.life_threatening DESC, r.created_at DESC""").fetchall()
    steps = {}
    for r in rows:
        steps[r["id"]] = con.execute("SELECT * FROM approval_step WHERE request_id=? ORDER BY step_no", (r["id"],)).fetchall()
    certs = con.execute("SELECT * FROM cert_registry WHERE fio=?", (u["fio"],)).fetchall()
    con.close()
    def cur_stage(r):
        st = r["route"].split("|")
        return st[min(r["stage"], len(st) - 1)]
    def can_act(r):
        stage = cur_stage(r)
        if u["role_key"] == "admin":
            return True
        if stage in ("initiator", "executor"):
            return u["id"] == r["author_id"]
        rights = {"head": ("head",), "deputy": ("deputy", "chief"), "chief": ("chief",),
                  "procurement": ("peo",), "accounting": ("signer",), "peo": ("peo",),
                  "commission": ("peo", "chief"), "head_mid": ("head", "chief"), "hr": ("hr",)}
        return u["role_key"] in rights.get(stage, ())
    return ctx(request, rows=rows, steps=steps, stage_names=STAGE_NAMES, certs=certs,
               cur_stage=cur_stage, can_act=can_act, has_ukiep=bool(certs and any(c["valid_until"] >= str(TODAY) for c in certs)),
               statuses={"on_route": "в маршруте", "signed": "подписано (УКЭП)", "rejected": "отклонено", "rework": "на доработке"},
               template="requests.html", section="Согласование документов и ходатайства")

@app.post("/requests/new")
def req_new(request: Request, kind: str = Form(...), subject: str = Form(...), life_threatening: str = Form("")):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    routes = {
        "ходатайство_товар": "initiator|procurement|accounting|peo|commission",
        "ходатайство_работы": "initiator|accounting|peo|commission",
        "ходатайство_медоборудование": "deputy|head_mid",
        "ходатайство_изменение_договора": "initiator|peo|commission",
        "ходатайство_общая": "initiator|head|deputy|peo",
        "согласование_приказ": "executor|head|deputy|chief",
    }
    route = routes.get(kind, "executor|head|deputy|chief")
    lt = 1 if life_threatening == "yes" else 0
    con = get_db()
    con.execute("""INSERT INTO request(kind,subject,dept_id,author_id,route,stage,status,created_at,life_threatening)
                   VALUES(?,?,?,?,?,0,?, datetime('now','localtime'), ?)""",
                (kind, subject, u["dept_id"], u["id"], route, "on_route", lt))
    rid = con.execute("SELECT max(id) FROM request").fetchone()[0]
    i = 1
    for st in route.split("|"):
        con.execute("INSERT INTO approval_step(request_id,step_no,approver_role) VALUES(?,?,?)", (rid, i, st))
        i += 1
    if lt:
        ch = con.execute("SELECT id FROM users WHERE role_key='chief' LIMIT 1").fetchone()
        if ch:
            con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                        (ch["id"], f"Ускоренный маршрут: ходатайство #{rid} — жизненно угрожающая ситуация", "/requests"))
    con.commit(); con.close()
    return RedirectResponse("/requests", status_code=302)

@app.post("/requests/{rid}/act")
def req_act(request: Request, rid: int, action: str = Form(...), comment: str = Form(""), sign: str = Form("")):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    r = con.execute("SELECT * FROM request WHERE id=?", (rid,)).fetchone()
    stages = r["route"].split("|")
    stage = stages[min(r["stage"], len(stages) - 1)]
    # право действовать: текущий этап соответствует роли, либо автор на этапе initiator/executor
    can = (stage in ("initiator", "executor") and u["id"] == r["author_id"]) or \
          (stage == "head" and u["role_key"] == "head") or \
          (stage == "deputy" and u["role_key"] in ("deputy", "chief")) or \
          (stage == "chief" and u["role_key"] == "chief") or \
          (stage == "procurement" and u["role_key"] in ("peo", "admin")) or \
          (stage == "accounting" and u["role_key"] in ("signer", "admin")) or \
          (stage == "peo" and u["role_key"] in ("peo", "admin")) or \
          (stage == "commission" and u["role_key"] in ("peo", "chief", "admin")) or \
          (stage == "head_mid" and u["role_key"] in ("head", "chief", "admin")) or \
          (stage == "hr" and u["role_key"] in ("hr", "admin")) or \
          u["role_key"] == "admin"
    if not can:
        con.close(); raise HTTPException(403, f"Сейчас этап «{STAGE_NAMES.get(stage, stage)}» — действовать должен другой участник маршрута")
    if action == "ukiep":
        # проверка сертификата в реестре (раздел 4.5 ТЗ: сертификат должен быть действущ)
        cert = con.execute("SELECT * FROM cert_registry WHERE fio=? AND valid_until>=?", (u["fio"], str(TODAY))).fetchone()
        if not cert:
            con.close()
            raise HTTPException(403, f"У пользователя «{u['fio']}» нет действующего сертификата УКЭП в реестре — подписание невозможно (раздел 4.5 ТЗ). Обратитесь к администратору для обновления реестра сертификатов.")
        con.execute("""UPDATE approval_step SET action='signed_ukiep', comment=?, acted_at=datetime('now','localtime'),
                       signature_cert=? WHERE request_id=? AND step_no=?""",
                    (comment, f"{cert['serial']} (УКЭП, ГОСТ Р 34.10-2012)", rid, r["stage"] + 1))
        if r["stage"] + 1 >= len(stages):
            con.execute("UPDATE request SET status='signed' WHERE id=?", (rid,))
        else:
            con.execute("UPDATE request SET stage=? WHERE id=?", (r["stage"] + 1, rid))
    elif action == "agree":
        con.execute("""UPDATE approval_step SET action='agreed', comment=?, acted_at=datetime('now','localtime')
                       WHERE request_id=? AND step_no=?""", (comment, rid, r["stage"] + 1))
        if r["stage"] + 1 >= len(stages):
            con.execute("UPDATE request SET status='signed' WHERE id=?", (rid,))
        else:
            con.execute("UPDATE request SET stage=? WHERE id=?", (r["stage"] + 1, rid))
        # уведомить следующего
        nxt = stages[r["stage"] + 1] if r["stage"] + 1 < len(stages) else None
        role_map = {"deputy": "deputy", "chief": "chief", "head": "head", "peo": "peo", "procurement": "peo", "accounting": "signer", "hr": "hr"}
        if nxt in role_map:
            nu = con.execute("SELECT id FROM users WHERE role_key=? LIMIT 1", (role_map[nxt],)).fetchone()
            if nu:
                con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                            (nu["id"], f"На согласовании: «{r['subject']}» (этап: {STAGE_NAMES.get(nxt, nxt)})", "/requests"))
    elif action == "reject":
        con.execute("UPDATE request SET status='rejected' WHERE id=?", (rid,))
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (r["author_id"], f"Отклонено: «{r['subject']}». Комментарий: {comment}", "/requests"))
    elif action == "rework":
        con.execute("UPDATE request SET status='rework', stage=0 WHERE id=?", (rid,))
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (r["author_id"], f"На доработку: «{r['subject']}». Комментарий: {comment}", "/requests"))
    con.commit(); con.close()
    return RedirectResponse("/requests", status_code=302)

# ---------- Закупки ----------
@app.get("/procurement", response_class=HTMLResponse)
def procurement(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    contracts = con.execute("SELECT * FROM contract ORDER BY end_date").fetchall()
    con.close()
    return ctx(request, contracts=contracts, template="procurement.html", section="Реестр договоров")

# ---------- Залы / календарь ----------
@app.get("/halls", response_class=HTMLResponse)
def halls(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM booking ORDER BY bdate,btime").fetchall()
    con.close()
    return ctx(request, bookings=rows, template="halls.html", section="Бронирование залов")

@app.post("/halls/book")
def hall_book(request: Request, hall: str = Form(...), bdate: str = Form(...), btime: str = Form(...),
              duration: int = Form(1), topic: str = Form(...)):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    clash = con.execute("SELECT 1 FROM booking WHERE hall=? AND bdate=? AND btime=?", (hall, bdate, btime)).fetchone()
    if clash:
        con.close()
        raise HTTPException(409, "Пересечение: зал уже забронирован на это время")
    con.execute("INSERT INTO booking VALUES(NULL,?,?,?,?,?,?)", (hall, bdate, btime, duration, topic, u["fio"]))
    con.commit(); con.close()
    return RedirectResponse("/halls", status_code=302)

@app.get("/calendar", response_class=HTMLResponse)
def calendar(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    events = con.execute("SELECT * FROM booking WHERE bdate>=? ORDER BY bdate,btime", (str(TODAY),)).fetchall()
    duties = con.execute("SELECT * FROM duty WHERE day>=? ORDER BY day", (str(TODAY),)).fetchall()
    con.close()
    return ctx(request, events=events, duties=duties, template="calendar.html", section="Календарь и дежурства")

# ---------- Объявления ----------
@app.get("/notices", response_class=HTMLResponse)
def notices(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM notice ORDER BY created_at DESC").fetchall()
    con.close()
    return ctx(request, notices=rows, can_post=u["role_key"] in ("head", "admin", "chief", "deputy"), template="notices.html", section="Доска объявлений")

@app.post("/notices/new")
def notice_new(request: Request, text: str = Form(...)):
    u = current_user(request)
    if not u or u["role_key"] not in ("head", "admin", "chief", "deputy"):
        raise HTTPException(403, "Публиковать объявления могут руководители подразделений и администраторы")
    con = get_db()
    con.execute("INSERT INTO notice(dept_id,text,author,created_at) VALUES(?,?,?,?)", (u["dept_id"], text, u["fio"], str(TODAY)))
    con.commit(); con.close()
    return RedirectResponse("/notices", status_code=302)

# ---------- ГО и ЧС ----------
@app.get("/go-chs", response_class=HTMLResponse)
def go_chs(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM go_chs").fetchall()
    con.close()
    return ctx(request, items=rows, template="gochs.html", section="ГО и ЧС")

# ---------- Протоколы и поручения ----------
@app.get("/protocols", response_class=HTMLResponse)
def protocols(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    protos = con.execute("SELECT * FROM proto ORDER BY pdate DESC").fetchall()
    tasks = con.execute("""SELECT t.*, a.fio assignee_fio, CASE WHEN t.due_date<? AND t.status!='done' THEN 1 ELSE 0 END overdue
                           FROM task t LEFT JOIN users a ON a.id=t.assignee_id ORDER BY t.due_date""", (str(TODAY),)).fetchall()
    mine_tasks = [t for t in tasks if t["assignee_id"] == u["id"]]
    con.close()
    return ctx(request, protos=protos, tasks=tasks, mine_tasks=mine_tasks,
               statuses={"in_work": "в работе", "done": "выполнено", "overdue": "просрочено"}, template="protocols.html", section="Протоколы и поручения")

@app.post("/protocols/task/{tid}/done")
def task_done(request: Request, tid: int):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    con.execute("UPDATE task SET status='done' WHERE id=? AND (assignee_id=? OR ? IN ('admin','chief'))", (tid, u["id"], u["role_key"]))
    con.commit(); con.close()
    return RedirectResponse("/protocols", status_code=302)

# ---------- Сроки документов ----------
@app.get("/deadlines", response_class=HTMLResponse)
def deadlines(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    if u["role_key"] in ("hr", "admin", "chief", "head"):
        rows = con.execute("""SELECT dl.*, a.fio, d.name dept_name FROM deadline dl JOIN users a ON a.id=dl.user_id
                              LEFT JOIN departments d ON d.id=a.dept_id ORDER BY dl.end_date""").fetchall()
    else:
        rows = con.execute("SELECT * FROM deadline WHERE user_id=? ORDER BY end_date", (u["id"],)).fetchall()
    con.close()
    def days_left(dt):
        return (datetime.date.fromisoformat(dt) - TODAY).days
    return ctx(request, rows=rows, days_left=days_left, template="deadlines.html", section="Контроль сроков (аккредитация, допуски, сертификаты)")

# ---------- HR ----------
@app.get("/hr", response_class=HTMLResponse)
def hr(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    leave = con.execute("""SELECT r.*, a.fio FROM request r JOIN users a ON a.id=r.author_id
                           WHERE r.kind IN ('отпуск','справка') ORDER BY r.created_at DESC""").fetchall()
    con.close()
    return ctx(request, leave=leave, template="hr.html", section="HR-модуль (заявки на отпуск и справки)")

@app.post("/hr/apply")
def hr_apply(request: Request, kind: str = Form(...), subject: str = Form(...)):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    if kind not in ("отпуск", "справка"):
        raise HTTPException(400, "Допустимые виды заявок: отпуск или справка (раздел 4.15 ТЗ)")
    con = get_db()
    con.execute("""INSERT INTO request(kind,subject,dept_id,author_id,route,stage,status,created_at)
                   VALUES(?,?,?,?,'hr',0,'on_route',datetime('now','localtime'))""", (kind, subject, u["dept_id"], u["id"]))
    hr_u = con.execute("SELECT id FROM users WHERE role_key='hr' LIMIT 1").fetchone()
    if hr_u:
        con.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                    (hr_u["id"], f"Кадровая заявка: {subject}", "/hr"))
    con.commit(); con.close()
    return RedirectResponse("/hr", status_code=302)

# ---------- Опросы ----------
@app.get("/surveys", response_class=HTMLResponse)
def surveys(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM survey").fetchall()
    con.close()
    show_results = u["role_key"] in ("quality", "chief", "admin")
    return ctx(request, surveys=rows, show_results=show_results, template="surveys.html", section="Опросы сотрудников")

@app.post("/surveys/{sid}/vote")
def survey_vote(request: Request, sid: int, vote: str = Form(...)):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    col = "votes_a" if vote == "a" else "votes_b"
    con.execute(f"UPDATE survey SET {col}={col}+1 WHERE id=?", (sid,))
    con.commit(); con.close()
    return RedirectResponse("/surveys", status_code=302)

# ---------- Аудиты ----------
@app.get("/audits", response_class=HTMLResponse)
def audits(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM audit_checklist ORDER BY check_date DESC").fetchall()
    con.close()
    return ctx(request, audits=rows, template="audits.html", section="Чек-листы аудитов")

# ---------- Формуляр ЛС ----------
@app.get("/drugs", response_class=HTMLResponse)
def drugs(request: Request, q: str = ""):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM drug_form WHERE name LIKE ? ORDER BY name", (f"%{q}%",)).fetchall()
    con.close()
    return ctx(request, drugs=rows, q=q, template="drugs.html", section="Формуляр лекарственных средств")

# ---------- МСЭ ----------
@app.get("/mse", response_class=HTMLResponse)
def mse(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    files = ["msel_2026-10-27_001.pdf", "msel_2026-10-27_002.pdf", "msel_2026-10-28_001.pdf"]
    return ctx(request, mse_files=files, is_registrar=u["role_key"] in ("mse", "admin"), template="mse.html", section="Обработка документов МСЭ (каталог ViPNet)")

# ---------- Учёт техники ----------
@app.get("/assets", response_class=HTMLResponse)
def assets(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    pcs = con.execute("""SELECT p.*, d.name dept_name FROM pc_asset p LEFT JOIN departments d ON d.id=p.dept_id""").fetchall()
    eq = con.execute("""SELECT e.*, d.name dept_name, CAST(julianday(e.verification_date)-julianday(?) AS INT) vdays
                        FROM med_equipment e LEFT JOIN departments d ON d.id=e.dept_id""", (str(TODAY),)).fetchall()
    con.close()
    return ctx(request, pcs=pcs, equipment=eq, template="assets.html", section="Учёт IT-инфраструктуры и медоборудования")

# ---------- Я новенький ----------
@app.get("/newbie", response_class=HTMLResponse)
def newbie(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM newbie").fetchall()
    links = con.execute("SELECT * FROM ext_links").fetchall()
    con.close()
    return ctx(request, steps=rows, links=links, template="newbie.html", section="Я новенький")

# ---------- Личный кабинет ----------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    dls = con.execute("SELECT * FROM deadline WHERE user_id=? ORDER BY end_date", (u["id"],)).fetchall()
    tasks = con.execute("SELECT * FROM task WHERE assignee_id=? AND status!='done'", (u["id"],)).fetchall()
    tickets = con.execute("SELECT status, COUNT(*) c FROM ticket WHERE author_id=? GROUP BY status", (u["id"],)).fetchall()
    ns_cnt = con.execute("SELECT COUNT(*) c FROM ns_event WHERE author_id=?", (u["id"],)).fetchone()["c"]
    reqs = con.execute("SELECT COUNT(*) c FROM request WHERE author_id=?", (u["id"],)).fetchone()["c"]
    upcoming = con.execute("SELECT * FROM booking WHERE bdate>=? ORDER BY bdate LIMIT 3", (str(TODAY),)).fetchall()
    con.close()
    def days_left(dt):
        return (datetime.date.fromisoformat(dt) - TODAY).days
    return ctx(request, dls=dls, tasks=tasks, tickets=tickets, ns_cnt=ns_cnt, reqs=reqs, upcoming=upcoming,
               days_left=days_left, template="dashboard.html", section="Личный кабинет")

# ---------- Уведомления ----------
@app.get("/notifications", response_class=HTMLResponse)
def notifications(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    con = get_db()
    rows = con.execute("SELECT * FROM notification WHERE user_id=? ORDER BY created_at DESC", (u["id"],)).fetchall()
    con.execute("UPDATE notification SET read=1 WHERE user_id=?", (u["id"],))
    con.commit(); con.close()
    return ctx(request, notes=rows, template="notifications.html", section="Центр уведомлений")

# ---------- Админ-панель ----------
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    u = current_user(request)
    if not u:
        return RedirectResponse("/login", status_code=302)
    if u["role_key"] != "admin":
        raise HTTPException(403, "Доступ только для администратора системы")
    con = get_db()
    users = con.execute("""SELECT a.*, d.name dept_name, r.name role_name FROM users a
                           LEFT JOIN departments d ON d.id=a.dept_id LEFT JOIN roles r ON r.key=a.role_key ORDER BY a.fio""").fetchall()
    certs = con.execute("SELECT * FROM cert_registry ORDER BY valid_until").fetchall()
    seclog = con.execute("SELECT * FROM security_log ORDER BY ts DESC LIMIT 20").fetchall()
    depts = con.execute("""SELECT d.name, b.name block_name FROM departments d JOIN blocks b ON b.id=d.block_id ORDER BY b.name,d.name""").fetchall()
    con.close()
    return ctx(request, users=users, certs=certs, seclog=seclog, depts=depts,
               today_str=str(TODAY), template="admin.html", section="Административная панель")

@app.post("/admin/user/new")
def admin_user_new(request: Request, fio: str = Form(...), username: str = Form(...), role_key: str = Form(...),
                   position: str = Form(""), email: str = Form(""), dept_id: int = Form(0)):
    u = current_user(request)
    if not u or u["role_key"] != "admin":
        raise HTTPException(403)
    tmp = secrets.token_urlsafe(6) + "A1!"
    h, s = hash_pw(tmp)
    con = get_db()
    try:
        con.execute("""INSERT INTO users(fio,dept_id,position,email,role_key,username,pw_hash,salt,must_change_pw,active)
                       VALUES(?,?,?,?,?,?,?, ?,1,1)""", (fio, dept_id or None, position, email, role_key, username, h, s))
        con.execute("INSERT INTO security_log VALUES(NULL,datetime('now','localtime'),?, ?, ?)",
                    (u["username"], f"создан пользователь {username}", request.client.host if request.client else "-"))
        con.commit()
    finally:
        con.close()
    return ctx(request, flash=f"Пользователь создан. Временный пароль (передать лично): {tmp}", template="admin.html", section="Административная панель",
               users=get_db().execute("SELECT a.*, d.name dept_name, r.name role_name FROM users a LEFT JOIN departments d ON d.id=a.dept_id LEFT JOIN roles r ON r.key=a.role_key ORDER BY a.fio").fetchall(),
               certs=[], seclog=[], depts=[], today_str=str(TODAY))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
