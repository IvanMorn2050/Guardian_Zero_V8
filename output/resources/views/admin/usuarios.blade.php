@extends('layouts.admin')

@section('content')

<h2 class="mb-4">Gestión de Usuarios</h2>

@if(session('success'))
    <div class="alert alert-success">{{ session('success') }}</div>
@endif

{{-- Filtro por rol --}}
<div class="card shadow-sm p-3 mb-4">
    <form method="GET" action="{{ url('/admin/usuarios') }}" class="row g-3">
        <div class="col-md-4">
            <label>Filtrar por Rol</label>
            <select name="rol" class="form-control">
                <option value="Todos">Todos</option>
                @foreach(['Administrador','Especialista','Voluntario','Civil'] as $rol)
                    <option value="{{ $rol }}" {{ request('rol') == $rol ? 'selected' : '' }}>{{ $rol }}</option>
                @endforeach
            </select>
        </div>
        <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-primary">Filtrar</button>
        </div>
    </form>
</div>

<div class="card shadow-sm p-3">

    @if($usuarios->isEmpty())
        <p class="text-muted text-center py-3">No se encontraron usuarios.</p>
    @else
        <table class="table table-hover align-middle">
            <thead class="table-light">
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Rol</th>
                    <th>Fecha Registro</th>
                </tr>
            </thead>
            <tbody>
                @foreach($usuarios as $usuario)
                <tr>
                    <td>{{ $usuario->ID }}</td>
                    <td>{{ $usuario->Nombre }}</td>
                    <td>{{ $usuario->Email }}</td>
                    <td>
                        <span class="badge bg-secondary">{{ $usuario->Rol }}</span>
                    </td>
                    <td>{{ \Carbon\Carbon::parse($usuario->Fecha_Registro)->format('d/m/Y') }}</td>
                </tr>
                @endforeach
            </tbody>
        </table>

        <div class="mt-3">
            {{ $usuarios->withQueryString()->links() }}
        </div>
    @endif

</div>

@endsection
