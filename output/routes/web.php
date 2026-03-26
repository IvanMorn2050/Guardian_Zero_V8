<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\FakeAuthController;

Route::get('/', function () {
    return redirect('/login');
});

Route::get('/login', [FakeAuthController::class, 'loginForm'])->name('login');
Route::post('/login', [FakeAuthController::class, 'login']);
Route::get('/logout', [FakeAuthController::class, 'logout'])->name('logout');

Route::middleware(['fakeauth'])->group(function () {

    Route::get('/admin/dashboard',    [AdminController::class, 'dashboard']);
    Route::get('/admin/incidentes',   [AdminController::class, 'incidentes']);
    Route::get('/admin/usuarios',     [AdminController::class, 'usuarios']);
    Route::get('/admin/estadisticas', [AdminController::class, 'estadisticas']);
    Route::get('/admin/reportes',     [AdminController::class, 'reportes']);

    // Actualizar estatus de un reporte desde la vista de incidentes
    Route::patch('/admin/incidentes/{id}/estatus', [AdminController::class, 'actualizarEstatus']);

});
