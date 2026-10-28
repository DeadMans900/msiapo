@extends('layouts.app')

@section('title', 'Личный кабинет')

@section('content')
<h1 style="margin-bottom:16px">Личный кабинет</h1>

<div class="grid" style="align-items:start">
    <div class="card">
        <h2 style="font-size:16px;color:var(--primary);margin-bottom:12px">Профиль</h2>
        <table class="data" style="background:transparent">
            <tr><th>ФИО</th><td>{{ $user->name }}</td></tr>
            <tr><th>E-mail</th><td>{{ $user->email }}</td></tr>
            <tr><th>Роль</th><td><span class="badge">{{ $rolesMap[$user->role] ?? $user->role }}</span></td></tr>
            @if($user->employee)
                <tr><th>Подразделение</th><td>{{ $user->employee->department?->name ?? '—' }}</td></tr>
                <tr><th>Должность</th><td>{{ $user->employee->position ?? '—' }}</td></tr>
                <tr><th>Телефон</th><td>{{ $user->employee->phone ? 'вн. ' . $user->employee->phone : '—' }}</td></tr>
            @endif
        </table>
    </div>

    <div class="card">
        <h2 style="font-size:16px;color:var(--primary);margin-bottom:12px">Смена пароля</h2>
        <form method="POST" action="{{ route('profile.password') }}">
            @csrf
            @method('PUT')
            <label for="current_password">Текущий пароль</label>
            <input type="password" id="current_password" name="current_password" required>
            @error('current_password')<div class="alert-danger">{{ $message }}</div>@enderror

            <label for="password">Новый пароль (мин. 8 символов)</label>
            <input type="password" id="password" name="password" required minlength="8">
            @error('password')<div class="alert-danger">{{ $message }}</div>@enderror

            <label for="password_confirmation">Повторите новый пароль</label>
            <input type="password" id="password_confirmation" name="password_confirmation" required minlength="8">

            <button type="submit" class="btn">Изменить пароль</button>
        </form>
    </div>
</div>
@endsection
