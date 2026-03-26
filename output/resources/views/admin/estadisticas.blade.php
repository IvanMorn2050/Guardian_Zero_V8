@extends('layouts.admin')

@section('content')

<h2 class="mb-4">Estadísticas del Sistema</h2>

{{-- Tarjetas resumen --}}
<div class="row mb-4">

    <div class="col-md-3">
        <div class="card text-center shadow-sm">
            <div class="card-body">
                <h6>Incidentes Hoy</h6>
                <h3 class="text-primary">{{ $incidentesHoy }}</h3>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card text-center shadow-sm">
            <div class="card-body">
                <h6>Incidentes Críticos</h6>
                <h3 class="text-danger">{{ $incidentesCriticos }}</h3>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card text-center shadow-sm">
            <div class="card-body">
                <h6>Tiempo Promedio</h6>
                <h3 class="text-success">{{ $tiempoPromedio }} hrs</h3>
            </div>
        </div>
    </div>

    <div class="col-md-3">
        <div class="card text-center shadow-sm">
            <div class="card-body">
                <h6>Voluntarios Activos</h6>
                <h3 class="text-warning">{{ $voluntariosActivos }}</h3>
            </div>
        </div>
    </div>

</div>

<div class="row">

    {{-- Incidentes por día (últimos 7 días) --}}
    <div class="col-md-6 mb-4">
        <div class="card shadow-sm p-3">
            <h5 class="mb-3">Incidentes Últimos 7 Días</h5>
            @if($incidentesPorDia->isEmpty())
                <p class="text-muted">Sin datos registrados.</p>
            @else
                <table class="table table-sm text-center">
                    <thead class="table-light">
                        <tr>
                            <th>Fecha</th>
                            <th>Cantidad</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($incidentesPorDia as $dia)
                        <tr>
                            <td>{{ \Carbon\Carbon::parse($dia->dia)->isoFormat('ddd D/MM') }}</td>
                            <td>{{ $dia->total }}</td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            @endif
        </div>
    </div>

    {{-- Top voluntarios --}}
    <div class="col-md-6 mb-4">
        <div class="card shadow-sm p-3">
            <h5 class="mb-3">Top Voluntarios (Últimos 30 días)</h5>
            @if($topVoluntarios->isEmpty())
                <p class="text-muted">Sin datos registrados.</p>
            @else
                <table class="table table-sm text-center">
                    <thead class="table-light">
                        <tr>
                            <th>Voluntario</th>
                            <th>Incidentes Atendidos</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($topVoluntarios as $vol)
                        <tr>
                            <td>{{ $vol->usuario->Nombre ?? 'N/A' }}</td>
                            <td>{{ $vol->reportes_atendidos }}</td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            @endif
        </div>
    </div>

</div>

{{-- Resumen general --}}
<div class="row">
    <div class="col-md-12">
        <div class="card shadow-sm p-4">
            <h5 class="mb-3">Resumen General</h5>
            <ul class="list-group">

                <li class="list-group-item">
                    📋 Total de reportes registrados: <strong>{{ $totalReportes }}</strong>
                </li>

                <li class="list-group-item">
                    ✔ Incidentes finalizados: <strong>{{ $finalizados }}</strong>
                    @if($totalReportes > 0)
                        <span class="text-success">({{ $pctResueltos }}%)</span>
                    @endif
                </li>

                <li class="list-group-item">
                    ⚙ En proceso: <strong>{{ $enProceso }}</strong>
                </li>

                <li class="list-group-item">
                    ⏱ Tiempo promedio de atención:
                    <strong>
                        @if($tiempoPromedio > 0)
                            {{ $tiempoPromedio }} horas
                        @else
                            Sin datos suficientes
                        @endif
                    </strong>
                </li>

            </ul>
        </div>
    </div>
</div>

@endsection
