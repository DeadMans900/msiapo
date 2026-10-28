<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AuthTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(\Database\Seeders\DepartmentEmployeeSeeder::class);
        $this->seed(\Database\Seeders\UserSeeder::class);
    }

    public function test_guest_is_redirected_to_login(): void
    {
        $this->get('/phonebook')->assertRedirect('/login');
    }

    public function test_login_form_renders(): void
    {
        $this->get('/login')->assertOk()->assertSee('Вход в МедПортал');
    }

    public function test_user_can_login_and_logout(): void
    {
        $user = User::where('email', 'employee@portal.local')->firstOrFail();

        $this->post('/login', ['email' => $user->email, 'password' => 'password'])
            ->assertRedirect(route('home'));

        $this->assertAuthenticatedAs($user);
        $this->get('/phonebook')->assertOk();

        $this->post('/logout')->assertRedirect(route('login'));
        $this->assertGuest();
    }

    public function test_wrong_password_rejected(): void
    {
        $user = User::where('email', 'admin@portal.local')->firstOrFail();

        $this->from('/login')->post('/login', ['email' => $user->email, 'password' => 'wrong'])
            ->assertRedirect('/login')
            ->assertSessionHasErrors('email');

        $this->assertGuest();
    }

    public function test_role_middleware_blocks_unauthorized(): void
    {
        $employee = User::where('email', 'employee@portal.local')->firstOrFail();
        $this->actingAs($employee);
        $this->get('/hr')->assertForbidden();

        $hr = User::where('email', 'hr@portal.local')->firstOrFail();
        $this->actingAs($hr);
        $this->get('/hr')->assertOk();

        // admin проходит везде
        $admin = User::where('email', 'admin@portal.local')->firstOrFail();
        $this->actingAs($admin);
        $this->get('/hr')->assertOk();
    }

    public function test_profile_and_password_change(): void
    {
        $user = User::where('email', 'it@portal.local')->firstOrFail();
        $this->actingAs($user);

        $this->get('/profile')->assertOk()->assertSee('Личный кабинет');

        $this->put('/profile/password', [
            'current_password'      => 'password',
            'password'              => 'NewStrongPass123',
            'password_confirmation' => 'NewStrongPass123',
        ])->assertSessionHas('status');

        $this->post('/logout');
        $this->post('/login', ['email' => $user->email, 'password' => 'NewStrongPass123'])
            ->assertRedirect(route('home'));
    }
}
