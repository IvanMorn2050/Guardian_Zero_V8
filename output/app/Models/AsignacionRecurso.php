<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AsignacionRecurso extends Model
{
    protected $table = 'asignacion_recursos';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'ID_Reporte', 'ID_Recurso',
        'Cantidad_Asignada', 'Fecha_Entrega',
    ];

    public function reporte()
    {
        return $this->belongsTo(Reporte::class, 'ID_Reporte', 'ID');
    }

    public function recurso()
    {
        return $this->belongsTo(Recurso::class, 'ID_Recurso', 'ID');
    }
}
