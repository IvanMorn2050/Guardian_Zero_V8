<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Alerta extends Model
{
    protected $table = 'alertas';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'Titulo', 'Mensaje', 'Nivel_Alerta',
        'Fecha_Emision', 'ID_Emisor',
    ];

    protected $casts = [
        'Fecha_Emision' => 'datetime',
    ];

    public function emisor()
    {
        return $this->belongsTo(Usuario::class, 'ID_Emisor', 'ID');
    }
}
