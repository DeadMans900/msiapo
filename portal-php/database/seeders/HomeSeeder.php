<?php

namespace Database\Seeders;

use App\Models\Duty;
use App\Models\Employee;
use App\Models\News;
use App\Models\QuickLink;
use App\Models\User;
use Illuminate\Database\Seeder;

/**
 * Данные для главной страницы (Шаг 3): новости, дежурства на сегодня,
 * внешние системы и даты рождения сотрудников.
 */
class HomeSeeder extends Seeder
{
    public function run(): void
    {
        // Даты рождения (подчищаем демо-данные)
        $bdays = [
            'Иванов'   => '1978-10-29',
            'Смирнова' => '1985-11-03',
            'Петрова'  => '1990-10-28',
            'Соколов'  => '1982-12-15',
            'Морозова' => '1995-11-20',
        ];
        foreach ($bdays as $last => $date) {
            Employee::where('last_name', $last)->update(['birth_date' => $date]);
        }

        // Новости
        $admin = User::where('role', 'admin')->first();
        News::firstOrCreate(
            ['title' => 'Портал запущен в опытную эксплуатацию'],
            ['body' => 'Добро пожаловать на внутренний портал. Разделы «Справочник» уже доступны, остальные модули подключаются поэтапно.',
             'author_id' => $admin?->id, 'published_at' => now()->subDays(2)]
        );
        News::firstOrCreate(
            ['title' => 'График планёрки на ноябрь'],
            ['body' => 'Понедельник 09:00, большой зал. Повестка — подготовка к аккредитации.',
             'author_id' => $admin?->id, 'published_at' => now()->subDay()]
        );
        News::firstOrCreate(
            ['title' => 'Осторожно: фишинговые письма'],
            ['body' => 'Не открывайте вложения от имени «техподдержки» с внешних адресов. О подозрительных письмах сообщайте в АСУ (внутр. 32-97-20).',
             'author_id' => $admin?->id, 'published_at' => now()]
        );

        // Дежурства на сегодня
        $today = now()->toDateString();
        foreach ([
            ['Дежурный врач', 'Соколов Д.О.', 'внутр. 210'],
            ['Ответственный администратор', 'Лебедева А.Ю.', 'внутр. 100'],
            ['Охрана', 'ЧОП «Барьер»', '02 / 32-97-07'],
            ['Эпидемиолог', 'Козлова И.П.', 'внутр. 315'],
            ['Ответственный за ГО', 'Кузнецов В.Л.', 'внутр. 118'],
        ] as [$service, $fio, $phone]) {
            Duty::firstOrCreate(['day' => $today, 'service' => $service, 'fio' => $fio], ['phone' => $phone]);
        }

        // Внешние системы
        foreach ([
            ['МИС ЕЦП', 'https://ecp.local', 1],
            ['L2', 'https://l2.local', 2],
            ['ТМК', 'https://tmk.local', 3],
            ['ФРМО', 'https://frmomo.local', 4],
            ['ФРЛР', 'https://frlr.local', 5],
            ['ЕГИСЗ', 'https://egisz.local', 6],
            ['Деловая почта (ViPNet)', 'https://vipnet.local', 7],
        ] as [$name, $url, $sort]) {
            QuickLink::firstOrCreate(['name' => $name], ['url' => $url, 'sort' => $sort]);
        }
    }
}
