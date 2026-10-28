<?php

namespace App\Http\Controllers;

use App\Models\Department;
use App\Models\Employee;
use Illuminate\Http\Request;

class PhonebookController extends Controller
{
    public function index(Request $request)
    {
        $q = trim((string) $request->query('q'));
        $depId = $request->query('department_id');

        $employees = Employee::with('department')
            ->when($q !== '', function ($query) use ($q) {
                $query->where(function ($sub) use ($q) {
                    $sub->where('last_name', 'like', "%{$q}%")
                        ->orWhere('first_name', 'like', "%{$q}%")
                        ->orWhere('middle_name', 'like', "%{$q}%")
                        ->orWhere('position', 'like', "%{$q}%")
                        ->orWhere('phone', 'like', "%{$q}%")
                        ->orWhere('email', 'like', "%{$q}%");
                });
            })
            ->when($depId, fn($query) => $query->where('department_id', $depId))
            ->orderBy('last_name')
            ->paginate(25)
            ->withQueryString();

        return view('phonebook.index', [
            'employees' => $employees,
            'departments' => Department::orderBy('name')->get(),
        ]);
    }
}
