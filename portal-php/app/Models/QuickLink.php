<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class QuickLink extends Model
{
    public $timestamps = false;
    protected $fillable = ['name', 'url', 'sort', 'is_active'];

    public function scopeActive($q)
    {
        return $q->where('is_active', true)->orderBy('sort');
    }
}
