@extends('layouts.admin')

@section('title', 'Dashboard - Guardian Zero')

@section('content')

<style>
.dashboard-title {
    font-weight: 700;
    font-size: 24px;
    margin-bottom: 24px;
    color: #0f4c5c;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 28px;
}

.dashboard-card {
    background: white;
    padding: 22px 24px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
    transition: 0.2s;
}

.dashboard-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.11);
}

.dashboard-card h5 {
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}

.dashboard-card h3 {
    font-size: 34px;
    font-weight: 700;
    margin: 0;
}

.card-incidentes  { border-left: 5px solid #3b82f6; }
.card-criticos    { border-left: 5px solid #ef4444; }
.card-tiempo      { border-left: 5px solid #f59e0b; }
.card-voluntarios { border-left: 5px solid #10b981; }

.card-incidentes  h3 { color: #3b82f6; }
.card-criticos    h3 { color: #ef4444; }
.card-tiempo      h3 { color: #f59e0b; }
.card-voluntarios h3 { color: #10b981; }

.map-section {
    background: white;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
    overflow: hidden;
    margin-bottom: 28px;
}

.map-header {
    padding: 18px 24px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.map-header h4 {
    font-size: 16px;
    font-weight: 600;
    color: #0f4c5c;
    margin: 0;
}

.map-header span {
    font-size: 12px;
    color: #6b7280;
}

#mapa { height: 460px; width: 100%; }

.map-legend {
    padding: 14px 24px;
    background: #f9fafb;
    border-top: 1px solid #f0f0f0;
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #4b5563;
}

.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}
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

<div class="map-section">

    <div class="map-header">
        <h4>🗺️ Panorámica Nacional de Incidentes</h4>
        <span>Zonas afectadas registradas en el sistema</span>
    </div>

    <div id="mapa"></div>

    <div class="map-legend">
        <div class="legend-item">
            <div class="legend-dot" style="background:#ef4444"></div> Crítico / Desastre Total
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#f97316"></div> Moderado
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#10b981"></div> Estable
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#6b7280"></div> Sin nivel asignado
        </div>
    </div>

</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const map = L.map('mapa').setView([23.6345, -102.5528], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

function colorPorNivel(nivel) {
    const colores = {
        'Critico':        '#ef4444',
        'Desastre Total': '#ef4444',
        'Moderado':       '#f97316',
        'Estable':        '#10b981',
    };
    return colores[nivel] || '#6b7280';
}

const zonas = @json($zonas ?? []);

zonas.forEach(zona => {
    if (!zona.Coordenadas) return;
    const partes = zona.Coordenadas.split(',');
    if (partes.length < 2) return;
    const lat = parseFloat(partes[0].trim());
    const lng = parseFloat(partes[1].trim());
    if (isNaN(lat) || isNaN(lng)) return;

    const color = colorPorNivel(zona.Nivel_Gravedad);

    L.circleMarker([lat, lng], {
        radius: 12,
        fillColor: color,
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85
    }).addTo(map).bindPopup(`
        <strong>${zona.Nombre_Zona ?? 'Zona sin nombre'}</strong><br>
        <span style="color:${color}">● ${zona.Nivel_Gravedad ?? 'Sin nivel'}</span><br>
        Tipo: ${zona.Tipo_Zona ?? '—'}<br>
        Población afectada: ${zona.Poblacion_Afectada ? zona.Poblacion_Afectada.toLocaleString() : '—'}<br>
        Evaluación: ${zona.Fecha_Evaluacion ?? '—'}
    `);
});
</script>

@endsection
