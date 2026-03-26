@extends('layouts.admin')

@section('content')

<style>
.dashboard-title{ font-weight:600; margin-bottom:25px; }
.dashboard-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:20px; }
.dashboard-card{ background:white; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.08); transition:0.2s; }
.dashboard-card:hover{ transform:translateY(-3px); box-shadow:0 6px 15px rgba(0,0,0,0.12); }
.dashboard-card h5{ font-size:14px; color:#6b7280; margin-bottom:10px; }
.dashboard-card h3{ font-size:30px; font-weight:700; }
.card-incidentes{ border-left:5px solid #3b82f6; }
.card-criticos{ border-left:5px solid #ef4444; }
.card-tiempo{ border-left:5px solid #f59e0b; }
.card-voluntarios{ border-left:5px solid #10b981; }
</style>

<h2 class="dashboard-title">Dashboard</h2>

@if(session('success'))
    <div class="alert alert-success">{{ session('success') }}</div>
@endif

<div class="dashboard-grid">

    <div class="dashboard-card card-incidentes">
        <h5>Incidentes Hoy</h5>
        <h3>{{ $incidentesHoy }}</h3>
    </div>

    <div class="dashboard-card card-criticos">
        <h5>Incidentes Críticos</h5>
        <h3>{{ $incidentesCriticos }}</h3>
    </div>

    <div class="dashboard-card card-tiempo">
        <h5>Tiempo Promedio</h5>
        <h3>{{ $tiempoPromedio }}</h3>
    </div>

    <div class="dashboard-card card-voluntarios">
        <h5>Voluntarios Activos</h5>
        <h3>{{ $voluntariosActivos }}</h3>
    </div>

</div>

@endsection
