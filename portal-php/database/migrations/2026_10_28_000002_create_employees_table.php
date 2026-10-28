<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('employees', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained()->cascadeOnDelete();
            $table->foreignId('department_id')->nullable()->constrained()->nullOnDelete();
            $table->string('last_name');
            $table->string('first_name');
            $table->string('middle_name')->nullable();
            $table->string('position')->nullable();
            $table->string('phone')->nullable();          // внутренний номер
            $table->string('ext_phone')->nullable();      // добавочный
            $table->string('email')->nullable();
            $table->string('room')->nullable();
            $table->date('hired_at')->nullable();
            $table->enum('role', ['employee','head','chief','hr','pharmacy','it','admin'])->default('employee');
            $table->text('notes')->nullable();
            $table->timestamps();
            $table->index(['last_name', 'department_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('employees');
    }
};
