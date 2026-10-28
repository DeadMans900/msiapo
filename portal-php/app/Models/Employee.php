<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Employee extends Model
{
    protected $fillable = [
        'user_id', 'department_id', 'last_name', 'first_name', 'middle_name',
        'position', 'phone', 'ext_phone', 'email', 'room', 'hired_at', 'role', 'notes',
    ];

    protected $casts = ['hired_at' => 'date'];

    public function department(): BelongsTo
    {
        return $this->belongsTo(Department::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function getFioAttribute(): string
    {
        return trim("{$this->last_name} {$this->first_name} {$this->middle_name}");
    }
}
