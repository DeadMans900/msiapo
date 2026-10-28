<?php

namespace App\Http\Controllers;

use App\Models\Duty;
use App\Models\Employee;
use App\Models\News;
use App\Models\QuickLink;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class HomeController extends Controller
{
    /** Пустой/нулевой счётчик, пока модуль не реализован */
    private const NOT_READY = null;

    public function index(Request $request)
    {
        $user = $request->user(); // на главной возможен только вход (middleware auth — см. routes)

        return view('home', [
            'news'      => News::with('author')->recent(5)->get(),
            'duties'    => Duty::today()->get(),
            'links'     => QuickLink::active()->get(),
            'birthdays' => Employee::birthdaysThisMonth()->take(6),

            // Счётчики виджетов по готовым модулям
            'phonebookCount' => Employee::count(),

            // Модули в разработке — счётчики появятся вместе с ними
            'ordersUnread'   => self::NOT_READY,
            'sopsUnread'     => self::NOT_READY,
            'ticketsOpen'    => self::NOT_READY,
            'requestsNew'    => self::NOT_READY,
            'eventsUpcoming' => self::NOT_READY,
        ]);
    }
}
