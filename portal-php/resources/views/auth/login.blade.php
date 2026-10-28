@extends('layouts.app')

@section('title', 'Вход')

@section('content')
<div style="max-width:420px;margin:60px auto">
    <div class="card">
        <h1 style="font-size:22px;margin-bottom:16px;color:var(--primary)">🏥 Вход в МедПортал</h1>

        <form method="POST" action="{{ route('login.store') }}">
            @csrf
            <div>
                <label for="email">E-mail (корпоративный)</label>
                <input type="email" id="email" name="email" value="{{ old('email') }}" required autofocus>
                @error('email')<div class="alert-danger">{{ $message }}</div>@enderror
            </div>
            <div>
                <label for="password">Пароль</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
                <input type="checkbox" id="remember" name="remember" value="1" style="width:auto;margin:0">
                <label for="remember" style="margin:0">Запомнить меня</label>
            </div>
            <button type="submit" class="btn" style="width:100%">Войти</button>
        </form>

        <p style="color:var(--muted);font-size:12px;margin-top:16px">
            Тестовые учётные записи: admin@portal.local / chief@portal.local / hr@portal.local — пароль <b>password</b>
        </p>
    </div>
</div>
@endsection
