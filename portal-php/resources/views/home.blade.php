@extends('layouts.app')

@section('title', 'Главная')

@section('content')
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
    <h1>Добро пожаловать, {{ auth()->user()->name }} 👋</h1>
    <span class="badge">{{ now()->format('d.m.Y') }} · {{ ['вс','пн','вт','ср','чт','пт','сб'][now()->dayOfWeek] }}</span>
</div>

{{-- Виджеты разделов --}}
@php
    $widgets = [
        ['icon'=>'📖','title'=>'Справочник','route'=>'phonebook.index','ready'=>true,'count'=>$phonebookCount,'hint'=>'сотрудников'],
        ['icon'=>'📑','title'=>'Приказы','route'=>null,'ready'=>false,'count'=>$ordersUnread,'hint'=>'непрочитанных'],
        ['icon'=>'📘','title'=>'СОПы','route'=>null,'ready'=>false,'count'=>$sopsUnread,'hint'=>'к обязательному прочтению'],
        ['icon'=>'🛠','title'=>'HelpDesk','route'=>null,'ready'=>false,'count'=>$ticketsOpen,'hint'=>'открытых заявок'],
        ['icon'=>'📝','title'=>'Ходатайства','route'=>null,'ready'=>false,'count'=>$requestsNew,'hint'=>'новых'],
        ['icon'=>'📅','title'=>'Календарь','route'=>null,'ready'=>false,'count'=>$eventsUpcoming,'hint'=>'ближайших событий'],
    ];
@endphp
<div class="grid" style="margin-bottom:24px">
    @foreach($widgets as $w)
        <div class="card widget @unless($w['ready']) disabled @endunless">
            @if($w['ready'])
                <a href="{{ route($w['route']) }}" class="widget-link">
                    <span class="widget-icon">{{ $w['icon'] }}</span>
                    <div><strong>{{ $w['title'] }}</strong>
                        <div class="widget-count">{{ number_format($w['count']) }} <span>{{ $w['hint'] }}</span></div>
                    </div>
                </a>
            @else
                <span class="widget-icon" style="opacity:.4">{{ $w['icon'] }}</span>
                <div><strong>{{ $w['title'] }}</strong>
                    <div class="widget-count muted">в разработке</div>
                </div>
            @endif
        </div>
    @endforeach
</div>

<div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;align-items:start">
    <div>
        {{-- Новости --}}
        <div class="card">
            <h3 class="card-title">📰 Новости портала</h3>
            @forelse($news as $n)
                <div class="news-item">
                    <div class="news-date">{{ $n->published_at->format('d.m.Y') }}</div>
                    <div>
                        <strong>{{ $n->title }}</strong>
                        <p>{{ $n->body }}</p>
                        @if($n->author)<small class="muted">— {{ $n->author->name }}</small>@endif
                    </div>
                </div>
            @empty
                <p class="muted">Новостей пока нет.</p>
            @endforelse
        </div>

        {{-- Дежурства --}}
        <div class="card">
            <h3 class="card-title">🩺 Дежурства на сегодня</h3>
            @if($duties->isEmpty())
                <p class="muted">График дежурств на сегодня не заполнен (модуль «Календарь и дежурства» — впереди).</p>
            @else
                <table class="data">
                    <tr><th>Служба</th><th>ФИО</th><th>Связь</th></tr>
                    @foreach($duties as $d)
                        <tr><td>{{ $d->service }}</td><td>{{ $d->fio }}</td><td>{{ $d->phone }}</td></tr>
                    @endforeach
                </table>
            @endif
        </div>
    </div>

    <div>
        {{-- Быстрые ссылки --}}
        <div class="card">
            <h3 class="card-title">🔗 Внешние системы</h3>
            @forelse($links as $l)
                <a class="ext-link" href="{{ $l->url }}" target="_blank" rel="noopener">↗ {{ $l->name }}</a>
            @empty
                <p class="muted">Список ссылок пуст.</p>
            @endforelse
        </div>

        {{-- Дни рождения --}}
        <div class="card">
            <h3 class="card-title">🎂 Дни рождения месяца</h3>
            @forelse($birthdays as $b)
                <div class="bday">
                    <span class="bday-date">{{ $b->birth_date->format('d.m') }}</span>
                    <span>{{ $b->fio_short }}</span>
                    @if($b->department)<small class="muted">· {{ $b->department->short_name ?? $b->department->name }}</small>@endif
                </div>
            @empty
                <p class="muted">В этом месяце дней рождения нет.</p>
            @endforelse
        </div>
    </div>
</div>
@endsection
