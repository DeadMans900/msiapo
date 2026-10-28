<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Корпоративный портал') — МедПортал</title>
    @stack('head')
    <style>
        :root{--primary:#1266a8;--accent:#e8f2fa;--text:#233044;--muted:#7b8794;--border:#dfe6ee;}
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Segoe UI',Roboto,Arial,sans-serif;color:var(--text);background:#f4f7fa}
        header.topbar{background:var(--primary);color:#fff;display:flex;align-items:center;gap:24px;padding:0 24px;height:56px}
        header.topbar a.brand{color:#fff;font-weight:700;font-size:18px;text-decoration:none}
        header.topbar nav{display:flex;gap:4px;flex:1}
        header.topbar nav a{color:#dceaf6;text-decoration:none;padding:8px 14px;border-radius:6px;font-size:14px}
        header.topbar nav a:hover,header.topbar nav a.active{background:rgba(255,255,255,.15);color:#fff}
        header.topbar .user{font-size:14px}
        main{max-width:1200px;margin:24px auto;padding:0 24px}
        footer{color:var(--muted);text-align:center;padding:24px;font-size:13px}
        .card{background:#fff;border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:16px}
        table.data{width:100%;border-collapse:collapse;background:#fff}
        table.data th{background:var(--accent);text-align:left;padding:10px;font-size:13px;color:var(--primary)}
        table.data td{padding:10px;border-bottom:1px solid var(--border);font-size:14px}
        .badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;background:var(--accent);color:var(--primary)}
        .btn{display:inline-block;background:var(--primary);color:#fff;border:none;padding:10px 18px;border-radius:6px;cursor:pointer;text-decoration:none;font-size:14px}
        .btn:hover{filter:brightness(1.1)}
        input,select,textarea{width:100%;padding:10px;border:1px solid var(--border);border-radius:6px;font:inherit;margin-bottom:12px}
        label{display:block;font-size:13px;color:var(--muted);margin-bottom:4px}
        .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
        .alert-danger{background:#fdecea;color:#b3261e;padding:10px;border-radius:6px;margin-bottom:16px;font-size:14px}
    </style>
</head>
<body>
<header class="topbar">
    <a class="brand" href="{{ route('home') }}">🏥 МедПортал</a>
    <nav>
        <a href="{{ route('home') }}" class="{{ request()->routeIs('home')?'active':'' }}">Главная</a>
        @auth
            <a href="{{ route('phonebook.index') }}" class="{{ request()->routeIs('phonebook.*')?'active':'' }}">Справочник</a>
            @can('module.hr')
                <a href="{{ route('hr.index') }}" class="{{ request()->routeIs('hr.*')?'active':'' }}">Кадры</a>
            @endcan
        @endauth
    </nav>
    <div class="user">
        @auth
            <a href="{{ route('profile') }}" style="color:#fff;text-decoration:none" class="{{ request()->routeIs('profile')?'active':'' }}">
                {{ auth()->user()->name }}
            </a>
            <span class="badge" style="background:rgba(255,255,255,.2);color:#fff">{{ config('portal.roles')[auth()->user()->role] ?? auth()->user()->role }}</span> ·
            <form action="{{ route('logout') }}" method="POST" style="display:inline">
                @csrf
                <button type="submit" style="background:none;border:none;color:#fff;cursor:pointer;text-decoration:underline;font-size:14px">Выйти</button>
            </form>
        @else
            <a href="{{ route('login') }}" style="color:#fff">Войти</a>
        @endauth
    </div>
</header>
<main>
    @if(session('status'))<div class="alert" style="background:#e6f4ea;color:#1e7e34;padding:10px;border-radius:6px;margin-bottom:16px">{{ session('status') }}</div>@endif
    @if($errors->any())<div class="alert-danger">{{ $errors->first() }}</div>@endif
    @yield('content')
</main>
<footer>МедПортал © {{ date('Y') }} · Laravel {{ app()->version() }} · MySQL</footer>
@stack('scripts')
</body>
</html>
