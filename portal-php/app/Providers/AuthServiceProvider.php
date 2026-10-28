<?php

namespace App\Providers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\ServiceProvider;

class AuthServiceProvider extends ServiceProvider
{
    /**
     * Модули портала и роли, которым они доступны.
     * admin всегда имеет полный доступ (см. EnsureUserHasRole).
     */
    public const MODULES = [
        'phonebook'   => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'orders'      => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'sops'        => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'helpdesk'    => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'requests'    => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'halls'       => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'calendar'    => ['employee', 'head', 'chief', 'hr', 'pharmacy', 'it'],
        'hr'          => ['hr', 'chief'],
        'pharmacy'    => ['pharmacy', 'chief'],
        'mse'         => ['chief', 'hr'],
        'dashboard'   => ['chief', 'head', 'hr'],
        'admin'       => ['admin'],
    ];

    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        Model::shouldBeStrict(!app()->isProduction());

        foreach (self::MODULES as $module => $roles) {
            Gate::define("module.{$module}", function ($user) use ($roles) {
                return $user->isRole('admin', ...$roles);
            });
        }
    }
}
