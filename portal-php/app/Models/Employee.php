<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Employee extends Model
{
    protected $fillable = [
        'user_id', 'department_id', 'last_name', 'first_name', 'middle_name',
        'position', 'phone', 'ext_phone', 'email', 'room', 'hired_at', 'birth_date', 'role', 'notes',
    ];

    protected $casts = ['hired_at' => 'date', 'birth_date' => 'date'];

    public function department(): BelongsTo
    {
        return $this->belongsTo(Department::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function getFioAttribute(): string
    {
        return trim("{$this->last_name} {$this->first_name} {$this->middle_name}");
    }

    /** Инициалы: «Иванов П.С.» */
    public function getFioShortAttribute(): string
    {
        $ini = fn ($n) => $n ? mb_substr($n, 0, 1) . '.' : '';
        return trim("{$this->last_name} " . $ini($this->first_name) . $ini($this->middle_name));
    }

    /**
     * Дни рождения в текущем месяце (виджет «Дни рождения»).
     * Сортировка: сначала ближайшие (день >= сегодня), затем остаток месяца.
     * @return \Illuminate\Support\Collection<int, Employee>
     */
    public static function birthdaysThisMonth()
    {
        $month  = (int) now()->format('m');
        $dayNow = (int) now()->format('d');

        return static::query()
            ->with('department')
            ->whereNotNull('birth_date')
            ->selectRaw("*, DAY(birth_date) AS bday")
            ->orderByRaw("CASE WHEN DAY(birth_date) >= ? THEN DAY(birth_date) ELSE 32 + DAY(birth_date) END", [$dayNow])
            ->get()
            ->filter(fn ($e) => (int) $e->birth_date->format('m') === $month);
    }
}
