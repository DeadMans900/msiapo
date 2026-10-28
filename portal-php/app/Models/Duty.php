<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Duty extends Model
{
    public $timestamps = false;
    protected $fillable = ['day', 'service', 'fio', 'phone'];

    protected function casts(): array
    {
        return ['day' => 'date'];
    }

    public function scopeToday($q)
    {
        return $q->whereDate('day', now()->toDateString())->orderBy('service');
    }
}
