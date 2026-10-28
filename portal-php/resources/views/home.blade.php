@extends('layouts.app')

@section('title', 'Главная')

@section('content')
<h1 style="margin-bottom:20px">Корпоративный портал</h1>
<div class="grid">
    <div class="card">
        <h3 style="color:var(--primary);margin-bottom:8px">📖 Справочник сотрудников</h3>
        <p style="font-size:14px;color:var(--muted)">Подразделения, телефоны, кабинеты.</p>
        <p style="margin-top:10px"><a class="btn" href="{{ route('phonebook.index') }}">Открыть</a></p>
    </div>
    @foreach(['📑 Приказы','📘 СОПы','🛠 HelpDesk','📅 Календарь','💊 Лекарства','⚙️ Админка'] as $future)
    <div class="card" style="opacity:.55">
        <h3 style="margin-bottom:8px">{{ $future }}</h3>
        <p style="font-size:14px;color:var(--muted)">В разработке — следующий шаг.</p>
    </div>
    @endforeach
</div>
@endsection
