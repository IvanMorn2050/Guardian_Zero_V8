<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ZonaAfectada extends Model
{
    protected $table = 'zona_afectada';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'Nombre_Zona', 'Coordenadas', 'Tipo_Zona',
        'Poblacion_Afectada', 'Nivel_Gravedad',
        'Fecha_Evaluacion', 'Impacto_Medio',
    ];

    public function reportes()
    {
        return $this->hasMany(Reporte::class, 'ID_Zona_Afectada', 'ID');
    }
}
