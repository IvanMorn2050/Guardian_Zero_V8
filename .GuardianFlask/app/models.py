from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ============================================================
# MODELOS PRINCIPALES
# ============================================================

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    ID             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre         = db.Column(db.String(100), nullable=False)
    Telefono       = db.Column(db.String(15), nullable=True)
    Email          = db.Column(db.String(100), unique=True, nullable=True)
    Direccion      = db.Column(db.Text, nullable=True)
    Contraseña     = db.Column(db.String(128), nullable=False, default="temp_password")
    Rol            = db.Column(
                        db.Enum("Administrador", "Especialista", "Voluntario", "Civil"),
                        default="Civil"
                     )
    Fecha_Registro = db.Column(db.DateTime, default=datetime.utcnow)
    FotoPerfil     = db.Column(db.LargeBinary, nullable=True)

    # Flask-Login requiere que get_id() devuelva el PK como string
    def get_id(self):
        return str(self.ID)


# ============================================================
# BLOG / FORO
# ============================================================

class Blog(db.Model):
    __tablename__ = "blog"

    ID_Blog     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo      = db.Column(db.String(100))
    Descripcion = db.Column(db.String(100))
    contenidos  = db.relationship(
                    "ContenidoBlog", backref="blog",
                    lazy=True, cascade="all, delete-orphan"
                  )


class ContenidoBlog(db.Model):
    __tablename__ = "contenido_blog"

    ID_Contenido_Blog = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Contenido         = db.Column(db.String(1000))
    ID_Blog           = db.Column(
                            db.Integer,
                            db.ForeignKey("blog.ID_Blog", ondelete="CASCADE")
                        )


# ============================================================
# CATÁLOGOS (tablas de referencia)
# ============================================================

class ConocimientosTecnicos(db.Model):
    """Catálogo de conocimientos: Primeros Auxilios, Rescate Urbano, etc."""
    __tablename__ = "conocimientos_tecnicos"

    ID     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(255), nullable=False)


class Puestos(db.Model):
    """Catálogo de puestos: Paramédico, Rescatista, Coordinador, Logística."""
    __tablename__ = "puestos"

    ID          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tipo_Puesto = db.Column(db.String(100))


class TipoEvidencia(db.Model):
    """Catálogo de tipos de evidencia: Imagen, Video, Documento PDF."""
    __tablename__ = "tipo_evidencia"

    ID             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Tipo_Evidencia = db.Column(db.String(100))


# ============================================================
# ZONA AFECTADA
# ============================================================

class ZonaAfectada(db.Model):
    __tablename__ = "zona_afectada"

    ID                 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Zona        = db.Column(db.String(255))
    Coordenadas        = db.Column(db.Text)           # formato esperado: "lat,lng"
    Tipo_Zona          = db.Column(db.String(100))
    Poblacion_Afectada = db.Column(db.Integer)
    Nivel_Gravedad     = db.Column(
                            db.Enum("Estable", "Moderado", "Critico", "Desastre Total"),
                            default="Estable"
                         )
    Fecha_Evaluacion   = db.Column(db.Date)
    Impacto_Medio      = db.Column(db.Text)


# ============================================================
# RECURSOS Y ASIGNACIONES
# ============================================================

class Recursos(db.Model):
    __tablename__ = "recursos"

    ID                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Recurso      = db.Column(db.String(100), nullable=False)
    Categoria           = db.Column(
                            db.Enum("Viveres", "Herramientas", "Medico", "Transporte"),
                            nullable=False
                          )
    Cantidad_Disponible = db.Column(db.Integer, default=0)
    Ubicacion_Almacen   = db.Column(db.String(255))


class AsignacionRecursos(db.Model):
    __tablename__ = "asignacion_recursos"

    ID                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Reporte        = db.Column(db.Integer, db.ForeignKey("reporte.ID"), nullable=False)
    ID_Recurso        = db.Column(db.Integer, db.ForeignKey("recursos.ID"), nullable=False)
    Cantidad_Asignada = db.Column(db.Integer, nullable=False)
    Fecha_Entrega     = db.Column(db.DateTime, default=datetime.utcnow)
    recurso           = db.relationship("Recursos", backref="asignaciones")


# ============================================================
# CURRICULUM Y CONOCIMIENTOS DEL VOLUNTARIO
# ============================================================

class Curriculum(db.Model):
    __tablename__ = "curriculum"

    ID             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Usuario     = db.Column(db.Integer, db.ForeignKey("usuario.ID"))
    Descripcion_CV = db.Column(db.Text)
    detalles       = db.relationship(
                        "DetalleConocimientos", backref="curriculum", lazy=True
                     )


class DetalleConocimientos(db.Model):
    """Relación N:M entre Curriculum y ConocimientosTecnicos con años de experiencia."""
    __tablename__ = "detalle_conocimientos"

    ID                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_CV             = db.Column(db.Integer, db.ForeignKey("curriculum.ID"))
    ID_Conocimiento   = db.Column(db.Integer, db.ForeignKey("conocimientos_tecnicos.ID"))
    Anios_Experiencia = db.Column(db.Integer)
    conocimiento      = db.relationship("ConocimientosTecnicos", backref="detalles")


# ============================================================
# VOLUNTARIO
# ============================================================

class Voluntario(db.Model):
    __tablename__ = "voluntario"

    ID                     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Usuario             = db.Column(db.Integer, db.ForeignKey("usuario.ID"))
    Nivel_Experiencia      = db.Column(db.String(50))
    Estatus                = db.Column(
                                db.Enum("Activo", "Inactivo", "En Mision"),
                                default="Activo"
                             )
    Horario_disponibilidad = db.Column(db.String(500), nullable=False)
    usuario                = db.relationship("Usuario", backref="voluntario")


# ============================================================
# REPORTE
# ============================================================

class Reporte(db.Model):
    __tablename__ = "reporte"

    ID                     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha                  = db.Column(db.DateTime, default=datetime.utcnow)
    Lugar                  = db.Column(db.String(255))
    ID_Voluntario          = db.Column(db.Integer, db.ForeignKey("voluntario.ID"))
    ID_Zona_Afectada       = db.Column(db.Integer, db.ForeignKey("zona_afectada.ID"))
    Estatus                = db.Column(
                                db.Enum("Pendiente", "Validado", "En Proceso", "Finalizado"),
                                default="Pendiente"
                             )
    Prioridad              = db.Column(
                                db.Enum("Baja", "Media", "Alta", "Critica"),
                                default="Media"
                             )
    Descripcion_Emergencia = db.Column(db.Text)
    zona                   = db.relationship("ZonaAfectada", backref="reportes")
    evidencias             = db.relationship("Evidencia", backref="reporte", lazy=True)
    asignaciones           = db.relationship("AsignacionRecursos", backref="reporte", lazy=True)


# ============================================================
# EVIDENCIA
# ============================================================

class Evidencia(db.Model):
    __tablename__ = "evidencia"

    ID                = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Archivo_Ruta      = db.Column(db.Text)
    Fecha_Captura     = db.Column(db.DateTime, default=datetime.utcnow)
    Tipo_Evidencia_ID = db.Column(db.Integer, db.ForeignKey("tipo_evidencia.ID"))
    ID_Reporte        = db.Column(db.Integer, db.ForeignKey("reporte.ID"))
    tipo              = db.relationship("TipoEvidencia", backref="evidencias")


# ============================================================
# ALERTAS
# ============================================================

class Alertas(db.Model):
    __tablename__ = "alertas"

    ID            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo        = db.Column(db.String(150), nullable=False)
    Mensaje       = db.Column(db.Text, nullable=False)
    Nivel_Alerta  = db.Column(
                        db.Enum("Informativa", "Precaucion", "Evacuacion"),
                        default="Informativa"
                    )
    Fecha_Emision = db.Column(db.DateTime, default=datetime.utcnow)
    ID_Emisor     = db.Column(db.Integer, db.ForeignKey("usuario.ID"))
    emisor        = db.relationship("Usuario", backref="alertas")