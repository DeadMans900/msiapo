# -*- coding: utf-8 -*-
"""Слой данных портала ОГАУЗ «Медсанчасть ИАПО». SQLite, сид по ТЗ (ред. 11)."""
import sqlite3, os, hashlib, secrets

DB_PATH = os.path.join(os.path.dirname(__file__), "portal.db")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

ROLE_SEED = [
    ("admin", "Администратор системы"),
    ("quality", "Менеджер качества"),
    ("hd_it", "Оператор HelpDesk IT"),
    ("hd_ahch", "Оператор HelpDesk АХЧ"),
    ("hd_mt", "Оператор HelpDesk МедТехника"),
    ("chief", "Главный врач"),
    ("deputy", "Заместитель главного врача"),
    ("head", "Руководитель подразделения"),
    ("employee", "Сотрудник"),
    ("hr", "Кадровая служба"),
    ("peo", "ПЭО / специалист по закупкам"),
    ("signer", "Подписант УКЭП"),
    ("mse", "Регистратор МСЭ"),
    ("pharmacy", "Аптека"),
]

BLOCKS_SEED = [
    ("Амбулаторно-поликлиническая помощь", "зам. по АПУ"),
    ("Педиатрическая помощь", "зам. по педиатрии"),
    ("Акушерско-гинекологическая служба", "зам. по АГ службе"),
    ("Медицинская часть (стационар и диагностика)", "зам. по медчасти"),
    ("Управление и вспомогательные подразделения", "зам. по хозчасти"),
]

DEPTS_SEED = {
    "Амбулаторно-поликлиническая помощь": [
        "Поликлиника: регистратура", "1 терапевтическое отделение", "2 терапевтическое отделение",
        "Кабинет неотложной помощи (КНМП)", "Отделение медицинской профилактики (ОМП)",
        "Стоматологическое отделение", "Кабинеты ПСМП", "Травматология и ортопедия", "Кабинет КФД",
        "«Школа диабета»", "Смотровой кабинет",
        "Поликлиника п. Жилкино: регистратура", "КТУ (Жилкино)", "КПУ (Жилкино)",
        "Кабинеты ПСМП (Жилкино)", "КФД (Жилкино)", "Ортопедическая стоматология (Жилкино)",
        "Стерилизационный кабинет (Жилкино)", "Кабинет неотложной травматологии и ортопедии (травмпункт № 4)",
        "Процедурный кабинет (Жилкино)", "Врачебная амбулатория (Жилкино)",
        "Фельдшерские здравпункты (ФАП)",
    ],
    "Педиатрическая помощь": [
        "Детская поликлиника: 1 педиатрическое отделение", "Детская поликлиника: 2 педиатрическое отделение",
        "Детская поликлиника: регистратура", "Процедурный кабинет (детский)", "Профилактическое отделение",
        "Кабинет здорового ребёнка", "Отделение организации медпомощи несовершеннолетним",
        "Отделение медицинской реабилитации", "Дневной стационар (детский)",
        "Кабинет рентгеновской КТ (детский)", "КНМП детская", "Детское стоматологическое отделение",
        "Консультативно-диагностический центр (детский)",
    ],
    "Акушерско-гинекологическая служба": [
        "Женская консультация: регистратура", "Доврачебный приём (ЖК)", "Кабинеты акушеров-гинекологов",
        "Кабинет антенатальной охраны плода", "Процедурный кабинет (ЖК)", "Операционная (ЖК)",
        "Кабинет УЗИ (ЖК)", "Дежурный врач-акушер", "КФД (ЖК)",
        "Пост централизованной выписки (ЖК)", "Психопрофилактическая подготовка",
        "Гинекологическое отделение с дневным стационаром",
        "Родильный дом: отделение неонатального профиля", "Физиологическое отделение новорожденных (с палатой РИТ)",
        "Акушерский стационар: физиологическое отделение", "Анестезиология-реанимация для женщин",
        "Патология беременности",
    ],
    "Медицинская часть (стационар и диагностика)": [
        "Приёмное отделение", "Бактериологическая лаборатория", "Клинико-диагностическая лаборатория (КДЛ)",
        "Эндоскопический кабинет", "Патологоанатомическое отделение", "Отделение УЗД", "Кабинет КФД (стационар)",
        "Физиотерапевтическое отделение", "Аптека", "Централизованное стерилизационное отделение (ЦСО)",
        "Рентгеновское отделение", "Кабинет рентгеновской остеоденситометрии",
        "Терапевтические отделения стационара", "Хирургические отделения стационара",
        "ОРИТ для больных с ОНМК", "Отделение диализа",
    ],
    "Управление и вспомогательные подразделения": [
        "Бухгалтерия", "Отдел кадров", "Отдел АСУ", "Планово-экономический отдел (ПЭО)",
        "Административно-хозяйственная часть (АХЧ)", "Пищеблок", "Гараж",
        "Организационно-методическое отделение (ОМО)", "Отдел платных услуг", "Отдел качества и БМД",
    ],
}

NS_CHARACTERS = [
    "Поломка медицинского оборудования",
    "Неправильная работа систем жизнеобеспечения",
    "Инциденты с интернетом",
    "Инциденты с МИС (ЕЦП, L2, ТМК и др.)",
    "Нарушение правил безопасности (несанкционированный доступ)",
    "Утечка конфиденциальной информации",
    "Не работает СОП",
    "Несвоевременное/неверное выполнение назначений",
    "Иные события",
]

# Матрица автоподсказки сегмента заявки при регистрации НС (раздел 4.3)
NS_SEGMENT_HINT = {
    "Поломка медицинского оборудования": "mt",
    "Неправильная работа систем жизнеобеспечения": "mt",
    "Инциденты с интернетом": "it",
    "Инциденты с МИС (ЕЦП, L2, ТМК и др.)": "it",
    "Утечка конфиденциальной информации": "it",
    "Нарушение правил безопасности (несанкционированный доступ)": "it_or_ahch",
}

HD_CATEGORIES = {
    "it": ["Не работает ПК/принтер/СБИС", "Замена картриджа", "Доступы", "Телефония",
           "Расходные материалы для оргтехники"],
    "ahch": ["Электрика", "Сантехника", "Уборка", "Мебель", "Закупка хозматериалов", "Транспорт"],
    "mt": ["Поломка медицинского оборудования", "Плановое ТО", "Поверка/калибровка",
           "Подключение/установка/перемещение", "Консультация по эксплуатации", "Списание"],
}

FULL_SCHEMA = """
CREATE TABLE IF NOT EXISTS roles(id INTEGER PRIMARY KEY, key TEXT UNIQUE, name TEXT);
CREATE TABLE IF NOT EXISTS blocks(id INTEGER PRIMARY KEY, name TEXT, deputy TEXT);
CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY, block_id INTEGER REFERENCES blocks(id), name TEXT);
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY, fio TEXT, dept_id INTEGER REFERENCES departments(id),
  position TEXT, email TEXT, role_key TEXT REFERENCES roles(key),
  username TEXT UNIQUE, pw_hash TEXT, salt TEXT, must_change_pw INTEGER DEFAULT 0,
  active INTEGER DEFAULT 1, birth_month_day TEXT);
CREATE TABLE IF NOT EXISTS news(id INTEGER PRIMARY KEY, title TEXT, body TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS duty(id INTEGER PRIMARY KEY, service TEXT, fio TEXT, phone TEXT, day TEXT);
CREATE TABLE IF NOT EXISTS ext_links(id INTEGER PRIMARY KEY, name TEXT, url TEXT);
CREATE TABLE IF NOT EXISTS phonebook(id INTEGER PRIMARY KEY, dept_id INTEGER REFERENCES departments(id),
  room TEXT, fio TEXT, position TEXT, phone TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS sop(id INTEGER PRIMARY KEY, code TEXT, title TEXT, version TEXT,
  effective_date TEXT, mandatory_read INTEGER DEFAULT 1, body TEXT);
CREATE TABLE IF NOT EXISTS read_log(id INTEGER PRIMARY KEY, doc_kind TEXT, doc_id INTEGER,
  user_id INTEGER REFERENCES users(id), read_at TEXT);
CREATE TABLE IF NOT EXISTS notice(id INTEGER PRIMARY KEY, dept_id INTEGER REFERENCES departments(id),
  text TEXT, author TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS ticket(
  id INTEGER PRIMARY KEY, segment TEXT, category TEXT, summary TEXT, description TEXT,
  dept_id INTEGER REFERENCES departments(id), room TEXT, asset_ref TEXT,
  author_id INTEGER REFERENCES users(id), assignee_id INTEGER REFERENCES users(id),
  status TEXT DEFAULT 'created', sla_hours INTEGER DEFAULT 24, created_at TEXT, closed_at TEXT,
  ns_id INTEGER);
CREATE TABLE IF NOT EXISTS ns_event(
  id INTEGER PRIMARY KEY, event_date TEXT, dept_id INTEGER REFERENCES departments(id),
  character TEXT, description TEXT, persons TEXT, sop_id INTEGER REFERENCES sop(id),
  author_id INTEGER REFERENCES users(id), responsible_id INTEGER REFERENCES users(id),
  due_date TEXT, conclusion TEXT, measures TEXT,
  status TEXT DEFAULT 'registered', created_at TEXT, linked_ticket_id INTEGER);
CREATE TABLE IF NOT EXISTS request(
  id INTEGER PRIMARY KEY, kind TEXT, subject TEXT, dept_id INTEGER REFERENCES departments(id),
  author_id INTEGER REFERENCES users(id), route TEXT, stage INTEGER DEFAULT 0,
  status TEXT DEFAULT 'on_route', created_at TEXT, life_threatening INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS approval_step(
  id INTEGER PRIMARY KEY, request_id INTEGER REFERENCES request(id), step_no INTEGER,
  approver_role TEXT, approver_name TEXT, action TEXT, comment TEXT, acted_at TEXT,
  signature_cert TEXT);
CREATE TABLE IF NOT EXISTS task(
  id INTEGER PRIMARY KEY, text TEXT, assignee_id INTEGER REFERENCES users(id),
  due_date TEXT, status TEXT DEFAULT 'in_work', source TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS notification(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  text TEXT, link TEXT, created_at TEXT, read INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS deadline(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  kind TEXT, label TEXT, end_date TEXT);
CREATE TABLE IF NOT EXISTS contract(
  id INTEGER PRIMARY KEY, num TEXT, date TEXT, price REAL, supplier TEXT, end_date TEXT,
  subject TEXT, notes TEXT, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS audit_checklist(id INTEGER PRIMARY KEY, template TEXT, dept_id INTEGER,
  checked_by TEXT, check_date TEXT, result TEXT);
CREATE TABLE IF NOT EXISTS drug_form(id INTEGER PRIMARY KEY, name TEXT, form TEXT, available TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS survey(id INTEGER PRIMARY KEY, title TEXT, anon INTEGER DEFAULT 1,
  options TEXT, votes_a INTEGER DEFAULT 0, votes_b INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS proto(id INTEGER PRIMARY KEY, pdate TEXT, title TEXT, participants TEXT);
CREATE TABLE IF NOT EXISTS booking(id INTEGER PRIMARY KEY, hall TEXT, bdate TEXT, btime TEXT,
  duration INTEGER, topic TEXT, organizer TEXT);
CREATE TABLE IF NOT EXISTS go_chs(id INTEGER PRIMARY KEY, title TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS newbie(id INTEGER PRIMARY KEY, step TEXT, hint TEXT);
CREATE TABLE IF NOT EXISTS md_doc(id INTEGER PRIMARY KEY, title TEXT, kind TEXT, version TEXT, effective_date TEXT);
CREATE TABLE IF NOT EXISTS med_equipment(id INTEGER PRIMARY KEY, inv_num TEXT, name TEXT, dept_id INTEGER,
  verification_date TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS pc_asset(id INTEGER PRIMARY KEY, type TEXT, model TEXT, serial TEXT,
  dept_id INTEGER, responsible TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS cert_registry(id INTEGER PRIMARY KEY, fio TEXT, serial TEXT, valid_until TEXT);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, num TEXT, odate TEXT, title TEXT,
  otype TEXT, mandatory_read INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS minzdrav_order(id INTEGER PRIMARY KEY, num TEXT, odate TEXT, title TEXT,
  inner_order_id INTEGER REFERENCES orders(id));
CREATE TABLE IF NOT EXISTS security_log(id INTEGER PRIMARY KEY, ts TEXT, user TEXT, action TEXT, ip TEXT);
CREATE TABLE IF NOT EXISTS holidays(dt TEXT);
"""

def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    return salt + hashlib.sha256((salt + pw).encode()).hexdigest(), salt

def init_db(reset=False):
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = get_db()
    con.executescript(FULL_SCHEMA)
    cur = con.cursor()
    if cur.execute("SELECT COUNT(*) c FROM roles").fetchone()["c"] == 0:
        for k, n in ROLE_SEED:
            cur.execute("INSERT INTO roles(key,name) VALUES(?,?)", (k, n))
        for bname, dep in BLOCKS_SEED:
            cur.execute("INSERT INTO blocks(name,deputy) VALUES(?,?)", (bname, dep))
            bid = cur.lastrowid
            for d in DEPTS_SEED[bname]:
                cur.execute("INSERT INTO departments(block_id,name) VALUES(?,?)", (bid, d))

        def u(fio, uname, role, pos, dept_name, email, birth="1980-05-12"):
            did = cur.execute("SELECT id FROM departments WHERE name=?", (dept_name,)).fetchone()
            did = did["id"] if did else None
            h, s = hash_pw(uname + "123!")  # временный пароль по ТЗ генерируется системой
            cur.execute("""INSERT INTO users(fio,dept_id,position,email,role_key,username,pw_hash,salt,must_change_pw,birth_month_day)
                           VALUES(?,?,?,?,?,?,?, ?,1,?)""",
                        (fio, did, pos, email, role, uname, h, s, birth[5:]))

        u("Смирнов Андрей Викторович", "smirnov.av", "admin", "Начальник отдела АСУ", "Отдел АСУ", "smirnov@msh38.ru", "1978-03-14")
        u("Козлова Ирина Петровна", "kozlova.ip", "quality", "Менеджер по качеству", "Отдел качества и БМД", "kozlova@msh38.ru", "1985-11-02")
        u("Новиков Сергей Дмитриевич", "novikov.sd", "hd_it", "Инженер АСУ", "Отдел АСУ", "novikov@msh38.ru", "1990-01-20")
        u("Фёдорова Ольга Николаевна", "fedorova.on", "hd_ahch", "Заведующая АХЧ", "Административно-хозяйственная часть (АХЧ)", "fedorova@msh38.ru", "1982-07-30")
        u("Григорьев Павел Анатольевич", "grigoriev.pa", "hd_mt", "Медицинский инженер", "Медицинская часть (стационар и диагностика)", "grigoriev@msh38.ru", "1988-09-16")
        u("Белова Марина Сергеевна", "belova.ms", "chief", "Главный врач", "Организационно-методическое отделение (ОМО)", "belova@msh38.ru", "1970-10-28")
        u("Кузнецов Виктор Леонидович", "kuznetsov.vl", "deputy", "Зам. по хозчасти", "Административно-хозяйственная часть (АХЧ)", "kuznetsov@msh38.ru", "1975-02-11")
        u("Рождественская Татьяна Ивановна", "rozhdestvenskaya.ti", "head", "Заведующая 1 терапевтическим отделением", "1 терапевтическое отделение", "rozhdestvenskaya@msh38.ru", "1983-06-05")
        u("Соколов Денис Олегович", "sokolov.do", "employee", "Врач-терапевт", "1 терапевтическое отделение", "sokolov@msh38.ru", "1992-12-23")
        u("Лебедева Анна Юрьевна", "lebedeva.au", "employee", "Постовая медицинская сестра", "Поликлиника: регистратура", "lebedeva@msh38.ru", "1995-04-18")
        u("Морозова Елена Витальевна", "morozova.ev", "hr", "Начальник отдела кадров", "Отдел кадров", "morozova@msh38.ru", "1979-08-21")
        u("Волков Артём Игоревич", "volkov.ai", "peo", "Экономист ПЭО", "Планово-экономический отдел (ПЭО)", "volkov@msh38.ru", "1991-03-09")
        u("Зайцева Наталья Павловна", "zaytseva.np", "signer", "Главный бухгалтер", "Бухгалтерия", "zaytseva@msh38.ru", "1976-05-27")
        u("Петров Роман Сергеевич", "petrov.rs", "mse", "Регистратор МСЭ", "Организационно-методическое отделение (ОМО)", "petrov@msh38.ru", "1989-07-07")
        u("Сидорова Мария Александровна", "sidorova.ma", "pharmacy", "Заведующая аптекой", "Аптека", "sidorova@msh38.ru", "1984-02-14")

        def ins(table, rows):
            cur.executemany(f"INSERT INTO {table} VALUES(NULL,{','.join('?'*len(rows[0]))})", rows)

        import datetime
        today = datetime.date(2026, 10, 28)
        ins("news", [
            ("Портал запущен в опытную эксплуатацию", "Добро пожаловать на внутренний портал Медсанчасти ИАПО. Все разделы доступны после авторизации.", "2026-10-26"),
            ("График планёрки на ноябрь", "Понедельник 09:00, большой зал, повестка — подготовка к аккредитации.", "2026-10-25"),
            ("Осторожно: фишинговые письма", "Не открывайте вложения от «msh@med-iaapo.ru» — это подделка. Сообщайте в АСУ.", "2026-10-24"),
        ])
        ins("duty", [
            ("Дежурный врач", "Соколов Д.О.", "внутр. 210", str(today)),
            ("Ответственный администратор", "Лебедева А.Ю.", "внутр. 100", str(today)),
            ("Охрана", "ЧОП «Барьер»", "02 / 32-97-07", str(today)),
            ("Эпидемиолог", "Козлова И.П.", "внутр. 315", str(today)),
            ("Ответственный за ГО", "Кузнецов В.Л.", "внутр. 118", str(today)),
        ])
        ins("ext_links", [
            ("МИС ЕЦП", "https://ecp.local"), ("L2", "https://l2.local"), ("ТМК", "https://tmk.local"),
            ("ФРМО", "https://frmomo.local"), ("ФРЛР", "https://frlr.local"), ("ЕГИСЗ", "https://egisz.local"),
            ("Деловая почта (ViPNet)", "https://vipnet.local"),
        ])
        ph = []
        for name, tel, room, pos in [
            ("Регистратура", "32-97-01", "101", "Регистратор"), ("Справочная", "32-97-02", "101", ""),
            ("Приёмная главной врача", "32-97-07", "201", "Секретарь"), ("Бухгалтерия", "32-97-10", "210", ""),
            ("Отдел АСУ (HelpDesk IT)", "32-97-20", "215", "Инженер"), ("АХЧ", "32-97-30", "118", ""),
            ("Медицинские инженеры", "32-97-40", "119", "Инженер"), ("Аптека", "32-97-50", "105", ""),
            ("Отдел кадров", "32-97-60", "205", ""), ("Отдел качества и БМД", "32-97-70", "315", ""),
        ]:
            did = cur.execute("SELECT id FROM departments WHERE name LIKE ?", (f"%{name.split('(')[0].strip()}%",)).fetchone()
            ph.append((did["id"] if did else None, room, name, pos, tel, ""))
        ins("phonebook", ph)
        ins("sop", [
            ("СОП-01-2026", "Обработка нежелательных событий", "3", "2026-09-01", 1, "Актуальная редакция классификатора НС (Приложение 2 ТЗ)."),
            ("СОП-02-2026", "Сестринский уход за пациентами ОРИТ", "2", "2026-08-15", 1, ""),
            ("СОП-03-2026", "Утилизация медицинских отходов классов Б", "5", "2026-07-01", 1, ""),
            ("СОП-04-2026", "Работа с МИС ЕЦП: регистрация талонов", "1", "2026-06-10", 0, ""),
        ])
        ins("notice", [
            (None, "Внимание! 30.10 в 14:00 тренировка по эвакуации (ГО и ЧС).", "Кузнецов В.Л.", "2026-10-27"),
            (None, "Обновлён график подачи ходатайств на 2027 год: до 1 сентября.", "Волков А.И.", "2026-10-26"),
        ])
        t1 = [("it", "Не работает принтер", "Принтер в регистратуре печатает полосами", None, "101", None, 10, None, "accepted", 8, "2026-10-27 09:12", None, None)]
        cur.executemany("INSERT INTO ticket(id,segment,category,summary,description,dept_id,room,asset_ref,author_id,assignee_id,status,sla_hours,created_at,closed_at,ns_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [(None,"it","Не работает ПК/принтер/СБИС","Не работает принтер","Принтер в регистратуре печатает полосами",1,"101",None,10,3,"accepted",8,"2026-10-27 09:12",None,None),
             (None,"ahch","Сантехника","Течь под раковиной","Кабинет 105, медленно капает",None,"105",None,9,4,"created",24,"2026-10-28 08:40",None,None),
             (None,"mt","Поломка медицинского оборудования","Не работает пульсоксиметр","Пульсоксиметр PM-10 показывает неверные данные",None,"301",None,9,5,"in_work",16,"2026-10-26 15:00",None,None)])
        cur.execute("""INSERT INTO ns_event(id,event_date,dept_id,character,description,persons,sop_id,author_id,responsible_id,due_date,conclusion,measures,status,created_at)
                       VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("2026-10-27 10:30", 1, "Не работает СОП",
             "СОП-03 не соответствует фактической схеме сбора отходов в процедурном кабинете",
             "медсестра Соколова А.А.", 3, 9, 2, "2026-11-10", None, None, "registered", "2026-10-27 10:35"))
        ins("request", [
            ("ходатайство_товар", "Закупка картриджей для регистратуры", 1, 10, "initiator|procurement|accounting|peo|commission", 1, "on_route", "2026-10-25", 0),
            ("ходатайство_медоборудование", "Замена пульсоксиметров в посты наблюдения", 14, 9, "deputy|head_mid", 0, "on_route", "2026-10-27", 0),
            ("согласование_приказ", "Приказ о внесении изменений в структуру", 19, 7, "executor|head|deputy|chief", 2, "on_route", "2026-10-26", 0),
        ])
        ins("approval_step", [
            (1, 1, "initiator", "Лебедева А.Ю.", "agreed", "", "2026-10-25 10:00", None),
            (1, 2, "procurement", "", "", "", None, None),
            (2, 1, "deputy", "", "", "", None, None),
            (3, 1, "head", "Рождественская Т.И.", "agreed", "Без замечаний", "2026-10-26 14:00", None),
            (3, 2, "deputy", "Кузнецов В.Л.", "agreed", "", "2026-10-26 16:20", "6A2F...E1 (УКЭП, ГОСТ Р 34.10-2012)"),
        ])
        ins("task", [
            ("Подготовить материалы к заседанию ВКК", 2, "2026-11-03", "in_work", "Протокол №41 от 21.10.2026", "2026-10-21"),
            ("Согласовать график дежурств на ноябрь", 8, "2026-10-25", "overdue", "Вручную (зам. по хозчасти)", "2026-10-15"),
            ("Провести инвентаризацию IT-склада", 3, "2026-11-15", "in_work", "Протокол планёрки", "2026-10-24"),
        ])
        nid = 1
        for uid in (9, 10):
            cur.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                        (uid, "Напоминание: срок действия сертификата УКЭП истекает через 14 дней", "/certs"))
            cur.execute("INSERT INTO notification VALUES(NULL,?,?,?,datetime('now','localtime'),0)",
                        (uid, "У вас поручение с истёкшим сроком: «Согласовать график дежурств»", "/tasks"))
        ins("deadline", [
            (1, "cert", "Сертификат УКЭП", "2026-11-11"),
            (9, "accreditation", "Аккредитация: терапия", "2026-12-15"),
            (9, "nmo", "Сертификат НМО (200 часов)", "2026-11-05"),
            (10, "sanmin", "Санминимум", "2026-11-30"),
            (8, "med_inspect", "Периодический медосмотр", "2026-11-02"),
        ])
        ins("contract", [
            ("Д-145/2026", "2026-03-02", 185000, "ООО «ОфисТехСервис»", "2026-11-20", "Поставка картриджей", "", 0),
            ("Д-77/2026", "2026-02-10", 1240000, "АО «МедТехника-Сибирь»", "2026-10-30", "ТО физиотерапевтического оборудования", "Монополия", 0),
            ("Д-12/2026", "2026-01-15", 45000, "ИП Кравцов В.В.", "2026-09-30", "Ремонт мягкой мебели", "отработан", 1),
        ])
        ins("audit_checklist", [
            ("Санэпидрежим", 1, "Козлова И.П.", "2026-10-20", "2 замечания: нарушение хранения дезсредств"),
            ("Учрежденческий контроль", 9, "Рождественская Т.И.", "2026-10-18", "Замечаний нет"),
        ])
        ins("drug_form", [
            ("Инсулин гларгин", "р-р п/к 100 МЕ/мл", "есть", ""),
            ("Метформин", "таб. 1000 мг", "нет, срок поставки 03.11", "замена по заявке №12"),
            ("Амоксициллин/клавуланат", "таб. 875+125 мг", "есть", ""),
        ])
        ins("survey", [
            ("Удовлетворённость условиями труда (анонимно)", 1, "Да|Скорее нет", 42, 11),
            ("Готовность к работе в новой версии ЕЦП", 0, "Готов|Не готов", 18, 25),
        ])
        ins("proto", [
            ("2026-10-21", "Заседание ВКК №41", "Белова М.С., Козлова И.П., Рождественская Т.И."),
            ("2026-10-24", "Планёрка руководителей", "заместители главврача, заведующие"),
        ])
        ins("booking", [
            ("Большой зал", "2026-10-29", "09:00", 1, "Планёрка", "ОМО"),
            ("Переговорная 2 этаж", "2026-10-28", "15:00", 1, "Согласование ТЗ на закупку", "ПЭО"),
        ])
        ins("go_chs", [
            ("Действия при пожаре", "Порядок эвакуации, точки сбора, ответственные. Тренировка 30.10.2026."),
            ("Действия при отключении электроэнергии", "Переход на ИБП/генератор, приоритетные потребители."),
            ("План тренировок на IV квартал", "Эвакуация — 30.10, проверка ГО — 15.12."),
        ])
        ins("newbie", [
            ("1. Получение доступа", "Заявку на учётную запись подаёт руководитель подразделения в отдел АСУ (внутр. 32-97-20)."),
            ("2. Первый вход", "Войдите под временным паролем и обязательно смените его (8+ символов, разные регистры, цифры)."),
            ("3. Прочитать обязательно", "Приказы «обязательно к ознакомлению» и СОПы — отметка под роспись в личном кабинете."),
            ("4. Куда обращаться", "IT — HelpDesk IT; бытовые вопросы — АХЧ; оборудование — мединженеры; всё через раздел «Заявки»."),
        ])
        ins("md_doc", [
            ("Клинические рекомендации «Терапия»: Артериальная гипертензия у взрослых", "КР", "2026", "2026-01-12"),
            ("Стандарт оснащения кабинета ПСМП", "Стандарт", "ред. 5", "2026-05-01"),
            ("Инструкция по охране труда для медсестры", "ОТ", "ред. 2", "2026-03-01"),
            ("Инструкция о пожарной безопасности", "ПБ", "ред. 3", "2026-06-15"),
        ])
        ins("med_equipment", [
            ("ИНВ-04-118", "Пульсоксиметр PM-10 (Minray)", 14, "2026-11-05", "в эксплуатации"),
            ("ИНВ-04-203", "Аппарат ИВЛ Fabian (Acute Care)", 26, "2026-10-30", "в ремонте"),
            ("ИНВ-07-055", "УЗИ-аппарат MyLab Twice (Esaote)", 22, "2027-02-14", "в эксплуатации"),
        ])
        ins("pc_asset", [
            ("ПК", "Dell OptiPlex 7010", "SN-DL70-8812", 1, "Лебедева А.Ю.", "в эксплуатации"),
            ("Принтер", "HP LaserJet Pro M404", "SN-HPM4-3311", 1, "Регистратура", "в эксплуатации"),
            ("Сервер", "HP ProLiant DL380", "SN-HPSV-1102", 13, "Новиков С.Д.", "в эксплуатации"),
        ])
        ins("cert_registry", [
            ("Белова М.С.", "6A2F...E1", "2026-11-11"),
            ("Кузнецов В.Л.", "7B31...04", "2027-04-30"),
            ("Зайцева Н.П.", "9C12...77", "2026-10-20"),
        ])
        ins("orders", [
            ("№ 118-к", "2026-10-01", "О структуре портфельных назначений", "по личному составу", 1),
            ("№ 120", "2026-10-15", "Об утверждении графика вакцинации", "организационный", 0),
        ])
        ins("minzdrav_order", [
            ("№ 54-1580-мр", "2026-06-25", "Об изменении структуры ОГАУЗ «Медсанчасть ИАПО»", 1),
        ])
        ins("read_log", [
            ("order", 1, 9, "2026-10-02 09:14"), ("order", 1, 10, "2026-10-02 11:40"),
            ("sop", 1, 9, "2026-09-05 08:30"),
        ])
        con.commit()
    con.close()

if __name__ == "__main__":
    init_db(reset=True)
    print("DB initialized:", DB_PATH)
