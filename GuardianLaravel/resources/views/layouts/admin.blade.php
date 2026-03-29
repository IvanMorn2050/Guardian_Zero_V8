<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>@yield('title', 'Panel Admin - Guardian Zero')</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('css/admin.css') }}">
</head>
<body>

<div class="sidebar">
    <div class="logo">
        <img src="{{ asset('img/logo.png') }}" 
            alt="Guardian Zero"
            onerror="this.style.display='none'">
        <span class="logo-text">Guardian Zero</span>
    </div>

    <nav class="menu">
        <a href="/admin/dashboard"
        class="{{ request()->is('admin/dashboard') ? 'active' : '' }}">
        Dashboard
        </a>

        <a href="/admin/incidentes"
        class="{{ request()->is('admin/incidentes*') ? 'active' : '' }}">
        Incidentes
        </a>

        <a href="/admin/usuarios"
        class="{{ request()->is('admin/usuarios*') ? 'active' : '' }}">
        Usuarios
        </a>

        <a href="/admin/estadisticas"
        class="{{ request()->is('admin/estadisticas*') ? 'active' : '' }}">
        Estadísticas
        </a>

        <a href="/admin/reportes"
        class="{{ request()->is('admin/reportes*') ? 'active' : '' }}">
        Reportes
        </a>
    </nav>

    <div class="logout">
        <a href="/logout">Cerrar Sesión</a>
    </div>
</div>

<div class="content">

    @yield('content')

</div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    @stack('scripts')
</body>
</html>