<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

/**
 * Проверка роли пользователя: route->middleware('require_role:admin,chief')
 * Роль admin имеет доступ ко всем разделам.
 */
class EnsureUserHasRole
{
    public function handle(Request $request, Closure $next, string ...$roles): Response
    {
        $user = $request->user();

        if (!$user) {
            return redirect()->route('login');
        }

        // admin имеет доступ ко всему
        if ($user->isRole('admin', ...$roles)) {
            return $next($request);
        }

        abort(403, 'Недостаточно прав для доступа к разделу.');
    }
}
