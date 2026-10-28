@extends('layouts.app')

@section('title', 'Справочник')

@section('content')
<h1 style="margin-bottom:16px">Справочник сотрудников и подразделений</h1>

<form method="GET" action="{{ route('phonebook.index') }}" style="display:flex;gap:12px;margin-bottom:20px">
    <input type="text" name="q" placeholder="Поиск по ФИО, должности, телефону…" value="{{ request('q') }}" style="flex:2;margin:0">
    <select name="department_id" style="flex:1;margin:0">
        <option value="">Все подразделения</option>
        @foreach($departments as $d)
            <option value="{{ $d->id }}" @selected(request('department_id')==$d->id)>{{ $d->name }}</option>
        @endforeach
    </select>
    <button class="btn" type="submit">Найти</button>
</form>

<table class="data">
    <thead>
    <tr><th>ФИО</th><th>Должность</th><th>Подразделение</th><th>Тел.</th><th>Доп.</th><th>Кабинет</th><th>Email</th></tr>
    </thead>
    <tbody>
    @forelse($employees as $e)
        <tr>
            <td><strong>{{ $e->fio }}</strong> @if($e->role!=='employee') <span class="badge">{{ $e->role }}</span>@endif</td>
            <td>{{ $e->position }}</td>
            <td>{{ $e->department?->short_name ?? '—' }}</td>
            <td>{{ $e->phone ?? '—' }}</td>
            <td>{{ $e->ext_phone ?? '—' }}</td>
            <td>{{ $e->room ?? '—' }}</td>
            <td>{{ $e->email ?? '—' }}</td>
        </tr>
    @empty
        <tr><td colspan="7" style="text-align:center;color:var(--muted)">Ничего не найдено</td></tr>
    @endforelse
    </tbody>
</table>

<div style="margin-top:16px">{{ $employees->links() }}</div>
@endsection
