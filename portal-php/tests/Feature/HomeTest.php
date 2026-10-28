<?php

namespace Tests\Feature;

use App\Models\Duty;
use App\Models\Employee;
use App\Models\News;
use App\Models\QuickLink;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class HomeTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(\Database\Seeders\DepartmentEmployeeSeeder::class);
        $this->seed(\Database\Seeders\UserSeeder::class);
        $this->seed(\Database\Seeders\HomeSeeder::class);
    }

    public function test_guest_is_redirected_from_home(): void
    {
        $this->get('/')->assertRedirect('/login');
    }

    public function test_home_shows_news_duties_links_and_birthdays(): void
    {
        $user = User::where('role', 'employee')->first();

        $this->actingAs($user)->get('/')
            ->assertOk()
            ->assertSee('Добро пожаловать, ' . $user->name)
            // Новости из сида
            ->assertSee('Портал запущен в опытную эксплуатацию')
            ->assertSee('фишинговые письма')
            // Дежурства на сегодня
            ->assertSee('Дежурный врач')
            ->assertSee('внутр. 210')
            // Внешние системы
            ->assertSee('МИС ЕЦП')
            ->assertSee('Деловая почта (ViPNet)')
            // Виджет справочника со счётчиком
            ->assertSee('Справочник')
            ->assertSee('сотрудников');
    }

    public function test_birthday_widget_lists_current_month_only(): void
    {
        // Сегодня 28.10.2026 → в списке должны быть октябрьские ДР, но не ноябрьские
        Employee::where('last_name', 'Иванов')->update(['birth_date' => '1978-10-29']);
        Employee::where('last_name', 'Смирнова')->update(['birth_date' => '1985-11-03']);

        $resp = $this->actingAs(User::where('role', 'employee')->first())->get('/');
        $resp->assertSee('Дни рождения месяца');

        $bdays = Employee::birthdaysThisMonth();
        $this->assertTrue($bdays->contains(fn ($e) => $e->last_name === 'Иванов'));
        $this->assertFalse($bdays->contains(fn ($e) => $e->last_name === 'Смирнова'));
    }

    public function test_duties_widget_uses_today_only(): void
    {
        Duty::create(['day' => now()->subDay()->toDateString(), 'service' => 'Вчера', 'fio' => 'Проверка', 'phone' => '000']);
        $this->actingAs(User::where('role', 'employee')->first())->get('/')
            ->assertDontSee('Проверка');
    }

    public function test_inactive_quick_link_hidden(): void
    {
        QuickLink::where('name', 'ТМК')->update(['is_active' => false]);
        $this->actingAs(User::where('role', 'employee')->first())->get('/')
            ->assertDontSee('ТМК');
    }

    public function test_news_limited_to_five_latest(): void
    {
        for ($i = 1; $i <= 7; $i++) {
            News::create(['title' => "Н новость номер $i", 'body' => 'test', 'published_at' => now()->addMinutes($i)]);
        }
        $titles = News::recent(5)->pluck('title');
        $this->assertCount(5, $titles);
        $this->assertFalse($titles->contains('Н новость номер 1'));
    }
}
