import requests, sys, re
S = requests.Session()
BASE = "http://127.0.0.1:8000"

def login(user, pw):
    r = S.post(BASE + "/login", data={"username": user, "password": pw}, allow_redirects=False)
    if r.status_code == 302 and "change-password" in r.headers.get("Location", ""):
        r2 = S.post(BASE + "/change-password", data={"old": pw, "new": "Test12345"}, allow_redirects=True)
        assert r2.status_code == 200, "pwd change failed " + str(r2.status_code)
        S.cookies.clear()
        r = S.post(BASE + "/login", data={"username": user, "password": "Test12345"}, allow_redirects=True)
    return r.status_code

fails = []
def check(name, cond, extra=""):
    if not cond: fails.append(name + " | " + extra)
    print(("OK  " if cond else "FAIL"), name, extra[:150])

# ---------- employee ----------
check("login employee", login("sokolov.do", "sokolov.do123!") == 200)
for path in ["/", "/search?q=%D0%BF%D1%80%D0%B8%D0%BA%D0%B0%D0%B7", "/phonebook", "/orders", "/sops", "/docs",
             "/helpdesk", "/ns", "/requests", "/procurement", "/halls", "/calendar", "/notices", "/go-chs",
             "/protocols", "/deadlines", "/hr", "/surveys", "/audits", "/drugs", "/mse", "/assets",
             "/newbie", "/dashboard", "/notifications"]:
    r = S.get(BASE + path)
    check("GET " + path, r.status_code == 200, f"{r.status_code} {r.text[:100] if r.status_code != 200 else ''}")

r = S.post(BASE + "/helpdesk/new", data={"segment": "it", "summary": "Тестовая заявка принтер",
           "description": "не печатает", "room": "205", "asset_ref": ""}, allow_redirects=True)
check("POST helpdesk/new", r.status_code == 200 and "Тестовая заявка" in r.text, str(r.status_code))

r = S.get(BASE + "/orders"); m = re.search(r'/orders/(\d+)/read', r.text)
if m:
    r2 = S.post(BASE + f"/orders/{m.group(1)}/read", allow_redirects=True)
    check("POST orders read", r2.status_code == 200, str(r2.status_code))

r = S.post(BASE + "/ns/new", data={"event_date": "2026-10-28", "dept_id": "1", "character": "Осложнение",
           "description": "тестовое НС", "persons": "Иванов И.И.", "sop_id": "", "make_ticket": "yes",
           "ticket_segment": "medtech"}, allow_redirects=True)
check("POST ns/new", r.status_code == 200 and "тестовое НС" in r.text, str(r.status_code))

r = S.post(BASE + "/requests/new", data={"kind": "Ходатайство", "subject": "Закупка тонометра",
           "life_threatening": ""}, allow_redirects=True)
check("POST requests/new", r.status_code == 200 and "тонометр" in r.text.lower(), str(r.status_code))

r = S.post(BASE + "/hr/apply", data={"kind": "отпуск", "subject": "Ежегодный отпуск с 10.11"}, allow_redirects=True)
check("POST hr/apply", r.status_code == 200, str(r.status_code))

r = S.post(BASE + "/halls/book", data={"hall": "Конференц-зал", "bdate": "2026-11-05", "btime": "10:00",
           "duration": "1", "topic": "Лекция"}, allow_redirects=True)
check("POST halls/book", r.status_code == 200, str(r.status_code))

r = S.post(BASE + "/notices/new", data={"text": "Тестовое объявление"}, allow_redirects=True)
check("POST notices/new (allow 200/403)", r.status_code in (200, 403), str(r.status_code))
S.get(BASE + "/logout"); S.cookies.clear()

# ---------- admin ----------
check("login admin", login("smirnov.av", "smirnov.av123!") == 200)
r = S.get(BASE + "/admin"); check("GET /admin (admin)", r.status_code == 200, str(r.status_code))
r = S.post(BASE + "/admin/user/new", data={"fio": "Тестовый Тест Тестович", "username": "testov.tt",
           "role_key": "employee", "position": "Врач", "email": "t@t.ru", "dept_id": "1"}, allow_redirects=True)
check("POST admin user/new", r.status_code == 200 and "testov.tt" in r.text, str(r.status_code))
S.get(BASE + "/logout"); S.cookies.clear()

# ---------- quality manager ----------
check("login quality", login("kozlova.ip", "kozlova.ip123!") == 200)
r = S.get(BASE + "/ns"); m = re.search(r'/ns/(\d+)/process', r.text)
if m:
    r2 = S.post(BASE + f"/ns/{m.group(1)}/process", data={"responsible_id": "1", "due_date": "2026-11-15",
                "conclusion": "Разобрано", "measures": "Доп. инструктаж"}, allow_redirects=True)
    check("POST ns process", r2.status_code == 200, str(r2.status_code))
else:
    check("POST ns process", False, "no process form found")
S.get(BASE + "/logout"); S.cookies.clear()

# ---------- IT operator: work ticket ----------
check("login hd_it", login("novikov.sd", "novikov.sd123!") == 200)
r = S.get(BASE + "/helpdesk?seg=it"); m = re.search(r'/helpdesk/(\d+)/status', r.text)
if m:
    r2 = S.post(BASE + f"/helpdesk/{m.group(1)}/status", data={"status": "accepted"}, allow_redirects=True)
    check("POST hd status accepted", r2.status_code == 200, str(r2.status_code))
else:
    check("POST hd status accepted", False, "no ticket action found")
S.get(BASE + "/logout"); S.cookies.clear()

# ---------- chief: approve request ----------
check("login chief", login("belova.ms", "belova.ms123!") == 200)
r = S.get(BASE + "/requests"); m = re.search(r'/requests/(\d+)/act', r.text)
if m:
    r2 = S.post(BASE + f"/requests/{m.group(1)}/act", data={"action": "approve", "comment": "Согласовано",
                "sign": "UKEP-test"}, allow_redirects=True)
    check("POST request act (chief)", r2.status_code == 200, str(r2.status_code))
else:
    print("INFO no pending acts visible for chief on first step (route may start with head)")
S.get(BASE + "/logout"); S.cookies.clear()

# ---------- access control ----------
login("lebedeva.au", "lebedeva.au123!")
r = S.get(BASE + "/admin")
check("access /admin denied for employee", r.status_code == 403, str(r.status_code))

print("\n==== FAILURES:", len(fails))
for f in fails: print(" -", f)
sys.exit(1 if fails else 0)
