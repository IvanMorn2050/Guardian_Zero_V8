@extends('layouts.admin')

@section('content')

<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="mb-0">Gestión de Usuarios</h2>
    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modalCrear">
        + Agregar Usuario
    </button>
</div>

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
                    <th>Acciones</th>
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
                    <td>
                        <button
                            class="btn btn-sm btn-outline-primary me-1"
                            data-bs-toggle="modal"
                            data-bs-target="#modalGestionar"
                            data-id="{{ $usuario->ID }}"
                            data-nombre="{{ $usuario->Nombre }}"
                            data-email="{{ $usuario->Email }}"
                            data-rol="{{ $usuario->Rol }}"
                        >
                            Gestionar
                        </button>
                        <button
                            class="btn btn-sm btn-outline-danger"
                            data-bs-toggle="modal"
                            data-bs-target="#modalEliminar"
                            data-id="{{ $usuario->ID }}"
                            data-nombre="{{ $usuario->Nombre }}"
                        >
                            Eliminar
                        </button>
                    </td>
                </tr>
                @endforeach
            </tbody>
        </table>

        <div class="mt-3">
            {{ $usuarios->withQueryString()->links() }}
        </div>
    @endif

</div>

{{-- Modal Gestionar Usuario --}}
<div class="modal fade" id="modalGestionar" tabindex="-1" aria-labelledby="modalGestionarLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalGestionarLabel">Gestionar Usuario</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="formGestionar" method="POST" action="">
                @csrf
                @method('PATCH')
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Nombre</label>
                        <p id="modal-nombre" class="form-control-plaintext"></p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Email</label>
                        <p id="modal-email" class="form-control-plaintext"></p>
                    </div>
                    <div class="mb-3">
                        <label for="modal-rol" class="form-label fw-bold">Rol</label>
                        <select name="rol" id="modal-rol" class="form-select">
                            @foreach(['Administrador','Especialista','Voluntario','Civil'] as $rol)
                                <option value="{{ $rol }}">{{ $rol }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                </div>
            </form>
        </div>
    </div>
</div>

{{-- Modal Crear Usuario --}}
<div class="modal fade" id="modalCrear" tabindex="-1" aria-labelledby="modalCrearLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalCrearLabel">Agregar Usuario</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form method="POST" action="{{ url('/admin/usuarios') }}">
                @csrf
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="crear-nombre" class="form-label fw-bold">Nombre *</label>
                        <input type="text" name="Nombre" id="crear-nombre" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="crear-email" class="form-label fw-bold">Email *</label>
                        <input type="email" name="Email" id="crear-email" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="crear-telefono" class="form-label fw-bold">Teléfono</label>
                        <input type="text" name="Telefono" id="crear-telefono" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="crear-direccion" class="form-label fw-bold">Dirección</label>
                        <input type="text" name="Direccion" id="crear-direccion" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label for="crear-password" class="form-label fw-bold">Contraseña *</label>
                        <input type="password" name="Contraseña" id="crear-password" class="form-control" minlength="4" required>
                    </div>
                    <div class="mb-3">
                        <label for="crear-rol" class="form-label fw-bold">Rol *</label>
                        <select name="Rol" id="crear-rol" class="form-select" required>
                            @foreach(['Administrador','Especialista','Voluntario','Civil'] as $rol)
                                <option value="{{ $rol }}">{{ $rol }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-success">Crear Usuario</button>
                </div>
            </form>
        </div>
    </div>
</div>

{{-- Modal Confirmar Eliminación --}}
<div class="modal fade" id="modalEliminar" tabindex="-1" aria-labelledby="modalEliminarLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title" id="modalEliminarLabel">Confirmar Eliminación</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <form id="formEliminar" method="POST" action="">
                @csrf
                @method('DELETE')
                <div class="modal-body">
                    <p>¿Estás seguro de que deseas eliminar al usuario <strong id="eliminar-nombre"></strong>?</p>
                    <p class="text-muted mb-0">Esta acción no se puede deshacer.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-danger">Eliminar</button>
                </div>
            </form>
        </div>
    </div>
</div>

@push('scripts')
<script>
    // Modal Gestionar
    document.getElementById('modalGestionar').addEventListener('show.bs.modal', function (event) {
        const btn = event.relatedTarget;
        document.getElementById('modal-nombre').textContent = btn.dataset.nombre;
        document.getElementById('modal-email').textContent = btn.dataset.email;
        document.getElementById('modal-rol').value = btn.dataset.rol;
        document.getElementById('formGestionar').action = '/admin/usuarios/' + btn.dataset.id;
    });

    // Modal Eliminar
    document.getElementById('modalEliminar').addEventListener('show.bs.modal', function (event) {
        const btn = event.relatedTarget;
        document.getElementById('eliminar-nombre').textContent = btn.dataset.nombre;
        document.getElementById('formEliminar').action = '/admin/usuarios/' + btn.dataset.id;
    });
</script>
@endpush

@endsection
