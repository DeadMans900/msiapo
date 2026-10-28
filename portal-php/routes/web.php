<?php

use App\Http\Controllers\Auth\LoginController;
use App\Http\Controllers\Auth\ProfileController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\PhonebookController;
use Illuminate\Support\Facades\Route;

// Гостевые маршруты
Route::get('/', [HomeController::class, 'index'])->name('home');

// ===== Шаг 2: Аутентификация и роли =====
Route::middleware('guest')->group(function () {
    Route::get('/login', [LoginController::class, 'showLoginForm'])->name('login');
    Route::post('/login', [LoginController::class, 'login'])->name('login.store');
});

Route::post('/logout', [LoginController::class, 'logout'])
    ->middleware('auth')->name('logout');

Route::middleware('auth')->group(function () {
    // Личный кабинет
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile');
    Route::put('/profile/password', [ProfileController::class, 'updatePassword'])->name('profile.password');

    // Модуль «Справочник» (Шаг 1) — доступен всем авторизованным
    Route::get('/phonebook', [PhonebookController::class, 'index'])->name('phonebook.index');

    // Раздел «Кадры» — только hr/chief/admin (пример require_role)
    Route::get('/hr', fn () => view('hr.placeholder'))
        ->middleware('require_role:hr,chief')
        ->name('hr.index');
});

// TODO Шаг 3+: Приказы, СОПы, HelpDesk, Ходатайства, Залы, Календарь…
