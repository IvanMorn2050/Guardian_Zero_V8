from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import (
    db, Usuario, Voluntario, Curriculum, DetalleConocimientos,
    ConocimientosTecnicos, Reporte, Evidencia, ZonaAfectada,
    Blog, ContenidoBlog, Alertas, Recursos, AsignacionRecursos
)
from datetime import datetime
import os

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


# ═══════════════════════════════════════════════════════════════
#  HELPER: obtener usuario autenticado
# ═══════════════════════════════════════════════════════════════
def get_current_user():
    """Devuelve el objeto Usuario desde flask-login o session como fallback."""
    if current_user and current_user.is_authenticated:
        return current_user
    user_id = session.get("user_id")
    if user_id:
        return Usuario.query.get(user_id)
    return None


# ═══════════════════════════════════════════════════════════════
#  HOME / DASHBOARD PRINCIPAL  →  GET /dashboard/
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/")
@login_required
def index():

    # ── Incidentes ───────────────────────────────────────────
    total_reportes       = Reporte.query.count()
    reportes_criticos    = Reporte.query.filter_by(Prioridad="Critica").count()
    reportes_alta        = Reporte.query.filter_by(Prioridad="Alta").count()
    reportes_activos     = Reporte.query.filter(
        Reporte.Estatus.in_(["Pendiente", "En Proceso"])
    ).count()
    reportes_finalizados = Reporte.query.filter_by(Estatus="Finalizado").count()

    # ── Tipos de desastre (agrupados por Tipo_Zona) ──────────
    tipos_raw = (
        db.session.query(ZonaAfectada.Tipo_Zona, func.count(ZonaAfectada.ID))
        .group_by(ZonaAfectada.Tipo_Zona)
        .all()
    )
    tipos_desastre = {t: c for t, c in tipos_raw if t}
    total_tipos    = sum(tipos_desastre.values()) or 1

    # ── Voluntarios ──────────────────────────────────────────
    total_voluntarios = Voluntario.query.filter_by(Estatus="Activo").count()
    vol_en_mision     = Voluntario.query.filter_by(Estatus="En Mision").count()

    # ── Zonas afectadas ──────────────────────────────────────
    zonas_criticas  = ZonaAfectada.query.filter(
        ZonaAfectada.Nivel_Gravedad.in_(["Critico", "Desastre Total"])
    ).count()
    zonas_moderadas = ZonaAfectada.query.filter_by(Nivel_Gravedad="Moderado").count()
    zonas_estables  = ZonaAfectada.query.filter_by(Nivel_Gravedad="Estable").count()
    total_zonas     = ZonaAfectada.query.count() or 1

    pop_result = db.session.query(
        func.sum(ZonaAfectada.Poblacion_Afectada)
    ).scalar()
    poblacion_afectada = pop_result or 0

    # ── Recursos ─────────────────────────────────────────────
    recursos_asignados = db.session.query(
        func.sum(AsignacionRecursos.Cantidad_Asignada)
    ).scalar() or 0

    # ── Alertas recientes ────────────────────────────────────
    alertas_recientes  = (
        Alertas.query
        .order_by(Alertas.Fecha_Emision.desc())
        .limit(5)
        .all()
    )
    alertas_evacuacion = Alertas.query.filter_by(Nivel_Alerta="Evacuacion").count()
    alertas_precaucion = Alertas.query.filter_by(Nivel_Alerta="Precaucion").count()

    # ── Zonas para el mapa (serializar a JSON para Leaflet/JS) ─
    zonas_mapa = (
        ZonaAfectada.query
        .filter(ZonaAfectada.Coordenadas.isnot(None))
        .all()
    )
    zonas_json = []
    for z in zonas_mapa:
        try:
            partes = z.Coordenadas.strip().split(",")
            lat = float(partes[0])
            lng = float(partes[1])
            zonas_json.append({
                "lat":      lat,
                "lng":      lng,
                "nombre":   z.Nombre_Zona or "Sin nombre",
                "tipo":     z.Tipo_Zona or "General",
                "gravedad": z.Nivel_Gravedad or "Estable",
                "poblacion": z.Poblacion_Afectada or 0,
            })
        except Exception:
            pass

    # ── Top 5 zonas con más reportes ─────────────────────────
    estados_prep = (
        db.session.query(
            ZonaAfectada.Nombre_Zona,
            ZonaAfectada.Nivel_Gravedad,
            func.count(Reporte.ID).label("total_rep")
        )
        .outerjoin(Reporte, Reporte.ID_Zona_Afectada == ZonaAfectada.ID)
        .group_by(ZonaAfectada.ID)
        .order_by(func.count(Reporte.ID).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        active_page          = "home",        # ← activa el ícono Inicio
        # Incidentes
        total_reportes       = total_reportes,
        reportes_criticos    = reportes_criticos,
        reportes_alta        = reportes_alta,
        reportes_activos     = reportes_activos,
        reportes_finalizados = reportes_finalizados,
        # Desastres
        tipos_desastre       = tipos_desastre,
        total_tipos          = total_tipos,
        # Voluntarios
        total_voluntarios    = total_voluntarios,
        vol_en_mision        = vol_en_mision,
        # Zonas
        zonas_criticas       = zonas_criticas,
        zonas_moderadas      = zonas_moderadas,
        zonas_estables       = zonas_estables,
        total_zonas          = total_zonas,
        poblacion_afectada   = poblacion_afectada,
        # Recursos
        recursos_asignados   = recursos_asignados,
        # Alertas
        alertas_recientes    = alertas_recientes,
        alertas_evacuacion   = alertas_evacuacion,
        alertas_precaucion   = alertas_precaucion,
        # Mapa
        zonas_json           = zonas_json,
        # Preparación
        estados_prep         = estados_prep,
    )


# ═══════════════════════════════════════════════════════════════
#  PERFIL  →  GET /dashboard/perfil
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/perfil")
@login_required
def perfil():
    usuario    = get_current_user()
    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()

    curriculum    = Curriculum.query.filter_by(ID_Usuario=usuario.ID).first()
    conocimientos = []
    if curriculum:
        rows = (
            db.session.query(DetalleConocimientos, ConocimientosTecnicos)
            .join(
                ConocimientosTecnicos,
                DetalleConocimientos.ID_Conocimiento == ConocimientosTecnicos.ID
            )
            .filter(DetalleConocimientos.ID_CV == curriculum.ID)
            .all()
        )
        conocimientos = [
            {"Nombre": ct.Nombre, "Anios_Experiencia": dk.Anios_Experiencia}
            for dk, ct in rows
        ]

    mis_foros = Blog.query.order_by(Blog.ID_Blog.desc()).limit(3).all()

    return render_template(
        "perfil.html",
        active_page        = "perfil",        # ← activa el ícono Perfil
        usuario            = usuario,
        voluntario         = voluntario,
        conocimientos      = conocimientos,
        total_certificados = len(conocimientos),
        total_horas        = 0,
        certificados       = [],
        mis_foros          = mis_foros,
    )


# ── POST: actualizar datos personales ────────────────────────
@dashboard_bp.route("/perfil/actualizar", methods=["POST"])
@login_required
def perfil_actualizar():
    usuario          = get_current_user()
    usuario.Nombre   = request.form.get("nombre",   usuario.Nombre)
    usuario.Email    = request.form.get("email",    usuario.Email)
    usuario.Telefono = request.form.get("telefono", usuario.Telefono)
    db.session.commit()
    flash("Perfil actualizado correctamente.", "success")
    return redirect(url_for("dashboard.perfil"))


# ── POST: cambiar foto de perfil ─────────────────────────────
@dashboard_bp.route("/perfil/foto", methods=["POST"])
@login_required
def perfil_foto():
    try:
        usuario = get_current_user()
        foto = request.files.get("foto")

        if not foto or foto.filename == "":
            flash("No seleccionaste ninguna imagen.", "error")
            return redirect(url_for("dashboard.perfil"))

        if not foto.mimetype.startswith("image/"):
            flash("El archivo debe ser una imagen.", "error")
            return redirect(url_for("dashboard.perfil"))

        # 🔥 leer una sola vez
        contenido = foto.read()

        if len(contenido) > 5 * 1024 * 1024:
            flash("La imagen es demasiado grande (máx 5MB).", "error")
            return redirect(url_for("dashboard.perfil"))

        usuario.FotoPerfil = contenido
        db.session.commit()

        flash("Foto de perfil actualizada correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        print("ERROR FOTO PERFIL:", e)
        flash("Error al subir la foto.", "error")

    return redirect(url_for("dashboard.perfil"))


# ═══════════════════════════════════════════════════════════════
#  CAPACITACIONES  →  GET /dashboard/capacitaciones
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/capacitaciones")
@login_required
def capacitaciones():
    return render_template(
        "capacitaciones.html",
        active_page = "capacitaciones",       # ← activa el ícono Capacitaciones
        cursos      = [],
        proximas    = [],
        usuario     = get_current_user(),
    )


# ═══════════════════════════════════════════════════════════════
#  FORO  →  GET /dashboard/foro
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/foro")
@login_required
def foro():
    blogs_raw   = Blog.query.order_by(Blog.ID_Blog.desc()).limit(10).all()
    discusiones = [
        {
            "ID":     b.ID_Blog,
            "Titulo": b.Titulo,
            "Autor":  "Voluntario",
            "Tipo":   "Voluntario",
            "Tiempo": "hace un momento",
        }
        for b in blogs_raw
    ]
    return render_template(
        "foro.html",
        active_page = "foro",                 # ← activa el ícono Foro
        discusiones = discusiones,
        usuario     = get_current_user(),
    )


# ── POST: crear nueva discusión ──────────────────────────────
@dashboard_bp.route("/foro/nueva", methods=["POST"])
@login_required
def foro_nueva():
    titulo    = request.form.get("titulo")
    contenido = request.form.get("contenido")

    nuevo_blog = Blog(Titulo=titulo, Descripcion=(contenido or "")[:100])
    db.session.add(nuevo_blog)
    db.session.flush()

    db.session.add(ContenidoBlog(Contenido=contenido, ID_Blog=nuevo_blog.ID_Blog))
    db.session.commit()

    flash("Discusión publicada exitosamente.", "success")
    return redirect(url_for("dashboard.foro"))


# ── GET: detalle de una discusión ────────────────────────────
@dashboard_bp.route("/foro/<int:blog_id>")
@login_required
def foro_detalle(blog_id):
    blog       = Blog.query.get_or_404(blog_id)
    contenidos = ContenidoBlog.query.filter_by(ID_Blog=blog_id).all()
    return render_template(
        "foro_detalle.html",
        active_page = "foro",                 # ← mantiene activo el ícono Foro
        blog        = blog,
        contenidos  = contenidos,
        usuario     = get_current_user(),
    )


# ═══════════════════════════════════════════════════════════════
#  REPORTE  →  GET /dashboard/reporte
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/reporte")
@login_required
def reporte():
    return render_template(
        "reporte.html",
        active_page = "reporte",              # ← activa el ícono Reporte
        usuario     = get_current_user(),
    )


# ── POST: enviar nuevo reporte ───────────────────────────────
@dashboard_bp.route("/reporte/nuevo", methods=["POST"])
@login_required
def reporte_nuevo():
    usuario = get_current_user()

    lugar       = request.form.get("lugar")
    descripcion = request.form.get("descripcion")
    prioridad   = request.form.get("prioridad", "Media")
    latitud     = request.form.get("latitud")
    longitud    = request.form.get("longitud")

    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()
    if not voluntario:
        flash("Debes estar registrado como voluntario para enviar reportes.", "error")
        return redirect(url_for("dashboard.reporte"))

    zona = None
    if latitud and longitud:
        zona = ZonaAfectada(
            Nombre_Zona      = lugar,
            Coordenadas      = f"{latitud},{longitud}",
            Nivel_Gravedad   = "Estable",
            Fecha_Evaluacion = datetime.utcnow().date(),
        )
        db.session.add(zona)
        db.session.flush()

    nuevo_reporte = Reporte(
        Lugar                  = lugar,
        Descripcion_Emergencia = descripcion,
        Prioridad              = prioridad,
        Estatus                = "Pendiente",
        ID_Voluntario          = voluntario.ID,
        ID_Zona_Afectada       = zona.ID if zona else None,
    )
    db.session.add(nuevo_reporte)
    db.session.flush()

    for campo, tipo_id in [("foto", 1), ("video", 2), ("audio", 3)]:
        archivo = request.files.get(campo)
        if archivo and archivo.filename:
            uploads_dir = os.path.join("app", "static", "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            filename = f"{nuevo_reporte.ID}_{campo}_{archivo.filename}"
            archivo.save(os.path.join(uploads_dir, filename))
            db.session.add(Evidencia(
                Archivo_Ruta      = f"uploads/{filename}",
                Tipo_Evidencia_ID = tipo_id,
                ID_Reporte        = nuevo_reporte.ID,
            ))

    db.session.commit()
    flash("Reporte enviado exitosamente. ¡Gracias por tu ayuda!", "success")
    return redirect(url_for("dashboard.reporte"))