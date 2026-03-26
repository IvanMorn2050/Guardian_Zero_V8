<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Usuario extends Model
{
    protected $table = 'usuario';
    protected $primaryKey = 'ID';
    public $timestamps = false;

    protected $fillable = [
        'Nombre', 'Telefono', 'Email', 'Direccion',
        'Contraseña', 'Rol', 'Fecha_Registro',
    ];

    public function voluntario()
    {
        return $this->hasOne(Voluntario::class, 'ID_Usuario', 'ID');
    }

    public function alertas()
    {
        return $this->hasMany(Alerta::class, 'ID_Emisor', 'ID');
    }
}
