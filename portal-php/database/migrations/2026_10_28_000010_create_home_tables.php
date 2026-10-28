<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Шаг 3: Главная страница — таблицы новостей, дежурств, быстрых ссылок
 * и прочитанных документов (для счётчика «Непрочитанные СОПы»).
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('news', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('body');
            $table->foreignId('author_id')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamp('published_at')->useCurrent();
            $table->timestamps();
            $table->index('published_at');
        });

        Schema::create('duties', function (Blueprint $table) {
            $table->id();
            $table->date('day');
            $table->string('service');          // напр. «Дежурный врач»
            $table->string('fio');
            $table->string('phone')->nullable();
            $table->unique(['day', 'service', 'fio']);
            $table->index('day');
        });

        Schema::create('quick_links', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('url');
            $table->unsignedSmallInteger('sort')->default(0);
            $table->boolean('is_active')->default(true);
        });

        Schema::create('document_reads', function (Blueprint $table) {
            $table->id();
            $table->string('doc_kind', 20);     // sop | order | notice …
            $table->unsignedBigInteger('doc_id');
            $table->foreignId('user_id')->constrained('users')->cascadeOnDelete();
            $table->timestamp('read_at')->useCurrent();
            $table->unique(['doc_kind', 'doc_id', 'user_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('document_reads');
        Schema::dropIfExists('quick_links');
        Schema::dropIfExists('duties');
        Schema::dropIfExists('news');
    }
};
