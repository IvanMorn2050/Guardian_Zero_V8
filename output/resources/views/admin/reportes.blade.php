@extends('layouts.admin')

@section('content')

<h2 class="mb-4">Exportar Reportes</h2>

<div class="card p-4 shadow-sm mb-4">
    <form method="GET" action="{{ url('/admin/reportes') }}" class="row g-3">
        <div class="col-md-4">
            <label>Desde</label>
            <input type="date" name="desde" class="form-control" value="{{ request('desde') }}">
        </div>
        <div class="col-md-4">
            <label>Hasta</label>
            <input type="date" name="hasta" class="form-control" value="{{ request('hasta') }}">
        </div>
        <div class="col-md-4 d-flex align-items-end gap-2">
            <button class="btn btn-primary">Filtrar</button>
        </div>
    </form>
</div>

<div class="card shadow-sm p-3">
    <h5 class="mb-3">Listado de Reportes ({{ $reportes->count() }})</h5>

    @if($reportes->isEmpty())
        <p class="text-muted text-center py-3">No hay reportes en el rango seleccionado.</p>
    @else
        <div class="table-responsive">
            <table class="table table-sm table-hover align-middle" id="tabla-reportes">
                <thead class="table-light">
                    <tr>
                        <th>ID</th>
                        <th>Fecha</th>
                        <th>Lugar</th>
                        <th>Zona</th>
                        <th>Prioridad</th>
                        <th>Estatus</th>
                        <th>Voluntario</th>
                        <th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($reportes as $r)
                    <tr>
                        <td>{{ $r->ID }}</td>
                        <td>{{ \Carbon\Carbon::parse($r->Fecha)->format('d/m/Y H:i') }}</td>
                        <td>{{ $r->Lugar ?? '—' }}</td>
                        <td>{{ $r->zona->Nombre_Zona ?? '—' }}</td>
                        <td>{{ $r->Prioridad }}</td>
                        <td>{{ $r->Estatus }}</td>
                        <td>{{ $r->voluntario->usuario->Nombre ?? '—' }}</td>
                        <td>{{ Str::limit($r->Descripcion_Emergencia, 60) }}</td>
                    </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    @endif
</div>

@endsection
