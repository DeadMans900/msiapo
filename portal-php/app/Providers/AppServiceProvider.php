<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        //
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Не ронять портал с 500, если не заведён раздел справочника
        \Illuminate\Database\Eloquent\Model::preventSilentlyDiscardingAttributes(false);

        \Illuminate\Support\Facades\Schema::defaultStringLength(191);

        // Гарантируем существование каталогов storage (на OpenServer их может не быть после распаковки)
        foreach ([
            storage_path('framework/cache/data'),
            storage_path('framework/sessions'),
            storage_path('framework/views'),
            storage_path('logs'),
            base_path('bootstrap/cache'),
        ] as $dir) {
            if (!is_dir($dir)) {
                @mkdir($dir, 0775, true);
            }
        }
    }
}
