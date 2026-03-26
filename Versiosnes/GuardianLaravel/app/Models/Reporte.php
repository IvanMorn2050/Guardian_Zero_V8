<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Reporte extends Model
{
    protected $table = 'reporte';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'Fecha', 'Lugar', 'ID_Voluntario', 'ID_Zona_Afectada',
        'Estatus', 'Prioridad', 'Descripcion_Emergencia',
    ];

    protected $casts = [
        'Fecha' => 'datetime',
    ];

    public function voluntario()
    {
        return $this->belongsTo(Voluntario::class, 'ID_Voluntario', 'ID');
    }

    public function zona()
    {
        return $this->belongsTo(ZonaAfectada::class, 'ID_Zona_Afectada', 'ID');
    }

    public function evidencias()
    {
        return $this->hasMany(Evidencia::class, 'ID_Reporte', 'ID');
    }

    public function asignaciones()
    {
        return $this->hasMany(AsignacionRecurso::class, 'ID_Reporte', 'ID');
    }
}
