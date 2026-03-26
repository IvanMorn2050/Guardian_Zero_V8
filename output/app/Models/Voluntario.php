<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Voluntario extends Model
{
    protected $table = 'voluntario';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'ID_Usuario', 'Nivel_Experiencia',
        'Estatus', 'Horario_disponibilidad',
    ];

    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'ID_Usuario', 'ID');
    }

    public function reportes()
    {
        return $this->hasMany(Reporte::class, 'ID_Voluntario', 'ID');
    }
}
