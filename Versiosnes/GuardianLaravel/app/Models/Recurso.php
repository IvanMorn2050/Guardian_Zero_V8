<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Recurso extends Model
{
    protected $table = 'recursos';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'Nombre_Recurso', 'Categoria',
        'Cantidad_Disponible', 'Ubicacion_Almacen',
    ];

    public function asignaciones()
    {
        return $this->hasMany(AsignacionRecurso::class, 'ID_Recurso', 'ID');
    }
}
