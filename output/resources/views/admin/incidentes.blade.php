@extends('layouts.admin')

@section('content')

<style>
.page-title{ font-weight:600; margin-bottom:20px; }
.filter-card{ background:white; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.08); margin-bottom:20px; }
.table-container{ background:white; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.08); }
.table th{ background:#f3f4f6; font-weight:600; }
.badge-prioridad-Critica{ background:#ef4444; color:white; padding:4px 10px; border-radius:6px; font-size:12px; }
.badge-prioridad-Alta{ background:#f97316; color:white; padding:4px 10px; border-radius:6px; font-size:12px; }
.badge-prioridad-Media{ background:#f59e0b; color:white; padding:4px 10px; border-radius:6px; font-size:12px; }
.badge-prioridad-Baja{ background:#10b981; color:white; padding:4px 10px; border-radius:6px; font-size:12px; }
.badge-estado{ background:#3b82f6; color:white; padding:4px 10px; border-radius:6px; font-size:12px; }
.estado-select{ border-radius:6px; padding:4px; font-size:13px; }
</style>

<h2 class="page-title">Gestión de Incidentes</h2>

@if(session('success'))
    <div class="alert alert-success">{{ session('success') }}</div>
@endif

<div class="filter-card">
    <form method="GET" action="{{ url('/admin/incidentes') }}" class="row g-3">

        <div class="col-md-3">
            <label>Fecha</label>
            <input type="date" name="fecha" class="form-control" value="{{ request('fecha') }}">
        </div>

        <div class="col-md-3">
            <label>Prioridad</label>
            <select name="prioridad" class="form-control">
                <option value="Todas">Todas</option>
                @foreach(['Critica','Alta','Media','Baja'] as $p)
                    <option value="{{ $p }}" {{ request('prioridad') == $p ? 'selected' : '' }}>{{ $p }}</option>
                @endforeach
            </select>
        </div>

        <div class="col-md-3">
            <label>Estado</label>
            <select name="estatus" class="form-control">
                <option value="Todos">Todos</option>
                @foreach(['Pendiente','Validado','En Proceso','Finalizado'] as $e)
                    <option value="{{ $e }}" {{ request('estatus') == $e ? 'selected' : '' }}>{{ $e }}</option>
                @endforeach
            </select>
        </div>

        <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-primary w-100">Filtrar</button>
        </div>

    </form>
</div>

<div class="table-container">

    @if($reportes->isEmpty())
        <p class="text-muted text-center py-3">No se encontraron incidentes.</p>
    @else
        <table class="table table-hover align-middle">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Fecha</th>
                    <th>Zona</th>
                    <th>Voluntario</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Cambiar Estado</th>
                </tr>
            </thead>
            <tbody>
                @foreach($reportes as $reporte)
                <tr>
                    <td>{{ $reporte->ID }}</td>
                    <td>{{ \Carbon\Carbon::parse($reporte->Fecha)->format('d/m/Y H:i') }}</td>
                    <td>{{ $reporte->zona->Nombre_Zona ?? 'Sin zona' }}</td>
                    <td>{{ $reporte->voluntario->usuario->Nombre ?? 'Sin asignar' }}</td>

                    <td>
                        <span class="badge-prioridad-{{ $reporte->Prioridad }}">
                            {{ $reporte->Prioridad }}
                        </span>
                    </td>

                    <td>
                        <span class="badge-estado">{{ $reporte->Estatus }}</span>
                    </td>

                    <td>
                        <form method="POST" action="{{ url('/admin/incidentes/' . $reporte->ID . '/estatus') }}">
                            @csrf
                            @method('PATCH')
                            <div class="d-flex gap-2">
                                <select name="estatus" class="form-control estado-select">
                                    @foreach(['Pendiente','Validado','En Proceso','Finalizado'] as $e)
                                        <option value="{{ $e }}" {{ $reporte->Estatus == $e ? 'selected' : '' }}>{{ $e }}</option>
                                    @endforeach
                                </select>
                                <button type="submit" class="btn btn-sm btn-primary">✓</button>
                            </div>
                        </form>
                    </td>
                </tr>
                @endforeach
            </tbody>
        </table>

        <div class="mt-3">
            {{ $reportes->withQueryString()->links() }}
        </div>
    @endif

</div>

@endsection
