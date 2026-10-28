<?php

namespace Database\Seeders;

use App\Models\Department;
use App\Models\Employee;
use App\Models\User;
use Illuminate\Database\Seeder;

/**
 * Учётные записи портала. Пароль по умолчанию: password
 */
class UserSeeder extends Seeder
{
    public function run(): void
    {
        $accounts = [
            // [name, email, role, department short_name]
            ['Администратор портала', 'admin@portal.local',  'admin',    'IT'],
            ['Иванов Пётр Сергеевич', 'chief@portal.local',  'chief',    'ТО-1'],
            ['Смирнова Анна Викторовна', 'head@portal.local', 'head',   'ХО-1'],
            ['Петрова Елена Дмитриевна', 'hr@portal.local',   'hr',     'КД'],
            ['Кузнецова Мария Игоревна', 'pharmacy@portal.local', 'pharmacy', 'АПТ'],
            ['Соколов Алексей Николаевич', 'it@portal.local', 'it',     'IT'],
            ['Морозова Ольга Андреевна', 'employee@portal.local', 'employee', 'ТО-1'],
        ];

        foreach ($accounts as [$name, $email, $role, $depShort]) {
            $employee = Employee::query()
                ->where('role', $role)
                ->when($depShort, fn ($q) => $q->whereHas('department', fn ($d) => $d->where('short_name', $depShort)))
                ->first();

            $user = User::query()->firstOrNew(['email' => $email]);
            $user->name        = $name;
            $user->role        = $role;
            $user->employee_id = $employee?->id;
            if (!$user->exists) {
                $user->password = 'password'; // cast 'hashed'
            }
            $user->save();
        }
    }
}
