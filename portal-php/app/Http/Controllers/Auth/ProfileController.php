<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\Rules\Password;

class ProfileController extends Controller
{
    /** Личный кабинет: профиль + смена пароля. */
    public function edit(Request $request)
    {
        return view('auth.profile', [
            'user'     => $request->user()->loadMissing('employee.department'),
            'rolesMap' => config('portal.roles'),
        ]);
    }

    /** Смена пароля. */
    public function updatePassword(Request $request)
    {
        $data = $request->validate([
            'current_password' => ['required', 'string'],
            'password'         => ['required', 'confirmed', Password::min(8)],
        ]);

        $user = $request->user();

        if (!Auth::guard('web')->validate([
            'email'    => $user->email,
            'password' => $data['current_password'],
        ])) {
            return back()->withErrors(['current_password' => 'Текущий пароль неверен.']);
        }

        $user->forceFill(['password' => $data['password']])->save(); // cast hashed

        return back()->with('status', 'Пароль изменён.');
    }
}
