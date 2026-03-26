<?php

namespace App\Http\Controllers;

use App\Models\Reporte;
use App\Models\Voluntario;
use App\Models\Usuario;
use App\Models\ZonaAfectada;
use App\Models\Alerta;
use App\Models\Recurso;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminController extends Controller
{
    public function dashboard()
    {
        $hoy = now()->toDateString();

        $incidentesHoy = Reporte::whereDate('Fecha', $hoy)->count();

        $incidentesCriticos = Reporte::where('Prioridad', 'Critica')
            ->whereIn('Estatus', ['Pendiente', 'En Proceso'])
            ->count();

        $voluntariosActivos = Voluntario::where('Estatus', 'Activo')->count();

        // Tiempo promedio: diferencia entre Fecha y ahora para reportes finalizados (en horas)
        $tiempoPromedio = Reporte::where('Estatus', 'Finalizado')
            ->whereDate('Fecha', '>=', now()->subDays(30)->toDateString())
            ->selectRaw('AVG(TIMESTAMPDIFF(HOUR, Fecha, NOW())) as promedio')
            ->value('promedio');

        $tiempoPromedio = $tiempoPromedio ? round($tiempoPromedio, 1) . 'h' : 'N/A';

        $zonas = ZonaAfectada::whereNotNull('Coordenadas')->get();

        return view('admin.dashboard', compact(
            'incidentesHoy',
            'incidentesCriticos',
            'voluntariosActivos',
            'tiempoPromedio',
            'zonas'
        ));
    }

    public function incidentes(Request $request)
    {
        $query = Reporte::with(['zona', 'voluntario.usuario']);

        if ($request->filled('fecha')) {
            $query->whereDate('Fecha', $request->fecha);
        }

        if ($request->filled('prioridad') && $request->prioridad !== 'Todas') {
            $query->where('Prioridad', $request->prioridad);
        }

        if ($request->filled('estatus') && $request->estatus !== 'Todos') {
            $query->where('Estatus', $request->estatus);
        }

        $reportes = $query->orderBy('Fecha', 'desc')->paginate(20);

        return view('admin.incidentes', compact('reportes'));
    }

    public function actualizarEstatus(Request $request, $id)
    {
        $reporte = Reporte::findOrFail($id);
        $reporte->Estatus = $request->estatus;
        $reporte->save();

        return back()->with('success', 'Estatus actualizado correctamente.');
    }

    public function usuarios(Request $request)
    {
        $query = Usuario::query();

        if ($request->filled('rol') && $request->rol !== 'Todos') {
            $query->where('Rol', $request->rol);
        }

        $usuarios = $query->orderBy('Fecha_Registro', 'desc')->paginate(20);

        return view('admin.usuarios', compact('usuarios'));
    }

    public function estadisticas()
    {
        $hoy = now()->toDateString();

        // Tarjetas resumen
        $incidentesHoy       = Reporte::whereDate('Fecha', $hoy)->count();
        $incidentesCriticos  = Reporte::where('Prioridad', 'Critica')
                                    ->whereIn('Estatus', ['Pendiente', 'En Proceso'])->count();
        $voluntariosActivos  = Voluntario::where('Estatus', 'Activo')->count();
        $tiempoPromedio      = Reporte::where('Estatus', 'Finalizado')
                                    ->selectRaw('AVG(TIMESTAMPDIFF(HOUR, Fecha, NOW())) as promedio')
                                    ->value('promedio');
        $tiempoPromedio      = $tiempoPromedio ? round($tiempoPromedio, 1) : 0;

        // Incidentes por día de la semana (últimos 7 días)
        $incidentesPorDia = Reporte::selectRaw('DATE(Fecha) as dia, COUNT(*) as total')
            ->whereDate('Fecha', '>=', now()->subDays(6)->toDateString())
            ->groupBy('dia')
            ->orderBy('dia')
            ->get();

        // Top voluntarios por reportes atendidos (últimos 30 días)
        $topVoluntarios = Voluntario::with('usuario')
            ->withCount(['reportes as reportes_atendidos' => function ($q) {
                $q->whereDate('Fecha', '>=', now()->subDays(30)->toDateString());
            }])
            ->orderByDesc('reportes_atendidos')
            ->limit(5)
            ->get();

        // Porcentaje de resolución
        $totalReportes     = Reporte::count();
        $finalizados       = Reporte::where('Estatus', 'Finalizado')->count();
        $enProceso         = Reporte::where('Estatus', 'En Proceso')->count();
        $pctResueltos      = $totalReportes > 0 ? round(($finalizados / $totalReportes) * 100) : 0;

        return view('admin.estadisticas', compact(
            'incidentesHoy', 'incidentesCriticos', 'voluntariosActivos', 'tiempoPromedio',
            'incidentesPorDia', 'topVoluntarios',
            'totalReportes', 'finalizados', 'enProceso', 'pctResueltos'
        ));
    }

    public function reportes()
    {
        $reportes = Reporte::with(['zona', 'voluntario.usuario'])
            ->orderBy('Fecha', 'desc')
            ->get();

        return view('admin.reportes', compact('reportes'));
    }
}
