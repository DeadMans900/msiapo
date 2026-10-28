<?php

namespace Database\Seeders;

use App\Models\Department;
use App\Models\Employee;
use Illuminate\Database\Seeder;

class DepartmentEmployeeSeeder extends Seeder
{
    public function run(): void
    {
        $departments = [
            ['name' => 'Приёмное отделение', 'short_name' => 'ПО', 'phone' => '201'],
            ['name' => 'Терапевтическое отделение №1', 'short_name' => 'ТО-1', 'phone' => '210'],
            ['name' => 'Хирургическое отделение №1', 'short_name' => 'ХО-1', 'phone' => '220'],
            ['name' => 'Аптека', 'short_name' => 'АПТ', 'phone' => '250'],
            ['name' => 'Кадровая служба (отдел кадров)', 'short_name' => 'КД', 'phone' => '290'],
            ['name' => 'Главный корпус / Администрация', 'short_name' => 'Гл.к.', 'phone' => '300'],
            ['name' => 'Отделение функциональной диагностики', 'short_name' => 'ОФД', 'phone' => '310'],
            ['name' => 'IT-служба', 'short_name' => 'IT', 'phone' => '330'],
        ];
        foreach ($departments as $d) {
            Department::query()->firstOrCreate(['name' => $d['name']], $d);
        }

        $employees = [
            ['Иванов', 'Пётр', 'Сергеевич', 'Заведующий отделением', 'ТО-1', '211', 'chief'],
            ['Смирнова', 'Анна', 'Викторовна', 'Старшая медсестра', 'ХО-1', '221', 'head'],
            ['Кузнецова', 'Мария', 'Игоревна', 'Провизор', 'АПТ', '251', 'pharmacy'],
            ['Петрова', 'Елена', 'Дмитриевна', 'Специалист по кадрам', 'КД', '291', 'hr'],
            ['Соколов', 'Алексей', 'Николаевич', 'Системный администратор', 'IT', '331', 'it'],
            ['Морозова', 'Ольга', 'Андреевна', 'Врач-терапевт', 'ТО-1', '212', 'employee'],
        ];
        foreach ($employees as $e) {
            [$ln, $fn, $mn, $pos, $depShort, $phone, $role] = $e;
            $dep = Department::where('short_name', $depShort)->first();
            Employee::query()->firstOrCreate(
                ['last_name' => $ln, 'first_name' => $fn, 'position' => $pos],
                [
                    'middle_name' => $mn,
                    'department_id' => $dep?->id,
                    'phone' => $phone,
                    'role' => $role,
                ]
            );
        }
    }
}
