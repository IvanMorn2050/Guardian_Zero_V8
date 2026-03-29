from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import (
    db, Usuario, Voluntario, Curriculum, DetalleConocimientos,
    ConocimientosTecnicos, Reporte, Evidencia, ZonaAfectada,
    Blog, ContenidoBlog, Alertas, Recursos, AsignacionRecursos,
    RespuestaForo
)
from datetime import datetime
import os

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


# ═══════════════════════════════════════════════════════════════
#  HELPER
# ═══════════════════════════════════════════════════════════════
def get_current_user():
    if current_user and current_user.is_authenticated:
        return current_user
    user_id = session.get("user_id")
    if user_id:
        return Usuario.query.get(user_id)
    return None


# ═══════════════════════════════════════════════════════════════
#  HOME  →  GET /dashboard/
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/")
@login_required
def index():
    total_reportes       = Reporte.query.count()
    reportes_criticos    = Reporte.query.filter_by(Prioridad="Critica").count()
    reportes_alta        = Reporte.query.filter_by(Prioridad="Alta").count()
    reportes_activos     = Reporte.query.filter(
        Reporte.Estatus.in_(["Pendiente", "En Proceso"])
    ).count()
    reportes_finalizados = Reporte.query.filter_by(Estatus="Finalizado").count()

    tipos_raw = (
        db.session.query(ZonaAfectada.Tipo_Zona, func.count(ZonaAfectada.ID))
        .group_by(ZonaAfectada.Tipo_Zona).all()
    )
    tipos_desastre = {t: c for t, c in tipos_raw if t}
    total_tipos    = sum(tipos_desastre.values()) or 1

    total_voluntarios = Voluntario.query.filter_by(Estatus="Activo").count()
    vol_en_mision     = Voluntario.query.filter_by(Estatus="En Mision").count()

    zonas_criticas  = ZonaAfectada.query.filter(
        ZonaAfectada.Nivel_Gravedad.in_(["Critico", "Desastre Total"])
    ).count()
    zonas_moderadas = ZonaAfectada.query.filter_by(Nivel_Gravedad="Moderado").count()
    zonas_estables  = ZonaAfectada.query.filter_by(Nivel_Gravedad="Estable").count()
    total_zonas     = ZonaAfectada.query.count() or 1

    pop_result         = db.session.query(func.sum(ZonaAfectada.Poblacion_Afectada)).scalar()
    poblacion_afectada = pop_result or 0
    recursos_asignados = db.session.query(func.sum(AsignacionRecursos.Cantidad_Asignada)).scalar() or 0

    alertas_recientes  = Alertas.query.order_by(Alertas.Fecha_Emision.desc()).limit(5).all()
    alertas_evacuacion = Alertas.query.filter_by(Nivel_Alerta="Evacuacion").count()
    alertas_precaucion = Alertas.query.filter_by(Nivel_Alerta="Precaucion").count()

    zonas_mapa = ZonaAfectada.query.filter(ZonaAfectada.Coordenadas.isnot(None)).all()
    zonas_json = []
    for z in zonas_mapa:
        try:
            partes = z.Coordenadas.strip().split(",")
            zonas_json.append({
                "lat": float(partes[0]), "lng": float(partes[1]),
                "nombre": z.Nombre_Zona or "Sin nombre",
                "tipo": z.Tipo_Zona or "General",
                "gravedad": z.Nivel_Gravedad or "Estable",
                "poblacion": z.Poblacion_Afectada or 0,
            })
        except Exception:
            pass

    estados_prep = (
        db.session.query(
            ZonaAfectada.Nombre_Zona,
            ZonaAfectada.Nivel_Gravedad,
            func.count(Reporte.ID).label("total_rep")
        )
        .outerjoin(Reporte, Reporte.ID_Zona_Afectada == ZonaAfectada.ID)
        .group_by(ZonaAfectada.ID)
        .order_by(func.count(Reporte.ID).desc())
        .limit(5).all()
    )

    return render_template(
        "dashboard/index.html",
        active_page          = "home",
        total_reportes       = total_reportes,
        reportes_criticos    = reportes_criticos,
        reportes_alta        = reportes_alta,
        reportes_activos     = reportes_activos,
        reportes_finalizados = reportes_finalizados,
        tipos_desastre       = tipos_desastre,
        total_tipos          = total_tipos,
        total_voluntarios    = total_voluntarios,
        vol_en_mision        = vol_en_mision,
        zonas_criticas       = zonas_criticas,
        zonas_moderadas      = zonas_moderadas,
        zonas_estables       = zonas_estables,
        total_zonas          = total_zonas,
        poblacion_afectada   = poblacion_afectada,
        recursos_asignados   = recursos_asignados,
        alertas_recientes    = alertas_recientes,
        alertas_evacuacion   = alertas_evacuacion,
        alertas_precaucion   = alertas_precaucion,
        zonas_json           = zonas_json,
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
    curriculum = Curriculum.query.filter_by(ID_Usuario=usuario.ID).first()

    conocimientos = []
    if curriculum:
        rows = (
            db.session.query(DetalleConocimientos, ConocimientosTecnicos)
            .join(ConocimientosTecnicos,
                  DetalleConocimientos.ID_Conocimiento == ConocimientosTecnicos.ID)
            .filter(DetalleConocimientos.ID_CV == curriculum.ID)
            .all()
        )
        conocimientos = [
            {"Nombre": ct.Nombre, "Anios_Experiencia": dk.Anios_Experiencia}
            for dk, ct in rows
        ]

    # ── Bloqueo cuestionario: ya respondió si tiene Descripcion_CV ──
    ya_respondio = curriculum is not None and bool(
        curriculum.Descripcion_CV and curriculum.Descripcion_CV.strip()
    )

    # ── Certificados: evidencias tipo 3 (PDF) del voluntario ──
    certificados = []
    if voluntario:
        evs = (
            db.session.query(Evidencia)
            .join(Reporte, Evidencia.ID_Reporte == Reporte.ID)
            .filter(
                Reporte.ID_Voluntario    == voluntario.ID,
                Evidencia.Tipo_Evidencia_ID == 3
            )
            .all()
        )
        certificados = [
            {
                "ID":      e.ID,
                "Nombre":  e.Nombre if e.Nombre else (e.Archivo_Ruta.split("/")[-1] if e.Archivo_Ruta else "Certificado"),
                "Fecha":   e.Fecha_Captura.strftime("%d/%m/%Y") if e.Fecha_Captura else "",
                "Archivo": "/static/" + e.Archivo_Ruta if e.Archivo_Ruta else "#",
            }
            for e in evs
        ]

    mis_foros = Blog.query.order_by(Blog.ID_Blog.desc()).limit(3).all()

    return render_template(
        "perfil.html",
        active_page        = "perfil",
        usuario            = usuario,
        voluntario         = voluntario,
        curriculum         = curriculum,
        conocimientos      = conocimientos,
        ya_respondio       = ya_respondio,
        total_certificados = len(certificados),
        certificados       = certificados,
        total_horas        = 0,
        mis_foros          = mis_foros,
    )


# ── POST: actualizar CV / info voluntario ───────────────────
@dashboard_bp.route("/perfil/cv/actualizar", methods=["POST"])
@login_required
def perfil_cv_actualizar():
    usuario    = get_current_user()
    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()
    if voluntario:
        voluntario.Nivel_Experiencia      = request.form.get("nivel_experiencia", voluntario.Nivel_Experiencia)
        voluntario.Horario_disponibilidad = request.form.get("disponibilidad",    voluntario.Horario_disponibilidad)
    curriculum = Curriculum.query.filter_by(ID_Usuario=usuario.ID).first()
    especialidades = request.form.getlist("especialidades")
    if curriculum and especialidades:
        curriculum.Descripcion_CV = ", ".join(especialidades)
    db.session.commit()
    flash("Información actualizada correctamente.", "success")
    return redirect(url_for("dashboard.perfil"))


# ── POST: actualizar datos personales ───────────────────────
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


# ── POST: cambiar foto ── (CORREGIDO) ───────────────────────
@dashboard_bp.route("/perfil/foto", methods=["POST"])
@login_required
def perfil_foto():
    try:
        usuario = get_current_user()
        foto    = request.files.get("foto")

        if not foto or not foto.filename:
            flash("No seleccionaste ninguna imagen.", "error")
            return redirect(url_for("dashboard.perfil"))

        allowed_mimes = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if foto.mimetype not in allowed_mimes:
            flash("Formato no permitido. Usa JPG, PNG, WEBP o GIF.", "error")
            return redirect(url_for("dashboard.perfil"))

        contenido = foto.read()
        if len(contenido) > 5 * 1024 * 1024:
            flash("La imagen no debe superar 5 MB.", "error")
            return redirect(url_for("dashboard.perfil"))

        usuario.FotoPerfil = contenido
        db.session.commit()
        flash("Foto de perfil actualizada correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        print("ERROR FOTO PERFIL:", e)
        flash(f"Error al subir la foto: {str(e)}", "error")

    return redirect(url_for("dashboard.perfil"))


# ── POST: cuestionario ── (CORREGIDO con bloqueo) ───────────
@dashboard_bp.route("/perfil/cuestionario", methods=["POST"])
@login_required
def perfil_cuestionario():
    usuario    = get_current_user()
    curriculum = Curriculum.query.filter_by(ID_Usuario=usuario.ID).first()

    # Bloquear si ya respondió
    if curriculum and curriculum.Descripcion_CV and curriculum.Descripcion_CV.strip():
        flash("Ya completaste el cuestionario anteriormente.", "info")
        return redirect(url_for("dashboard.perfil"))

    experiencia      = request.form.get("experiencia", "")
    habilidades      = request.form.getlist("habilidades")
    certificacion    = request.form.get("certificacion", "")
    horas_semana     = request.form.get("horas_semana", "")
    tipo_desastre    = request.form.getlist("tipo_desastre")
    condicion_medica = request.form.get("condicion_medica", "")
    vehiculo         = request.form.get("vehiculo", "")
    motivacion       = request.form.get("motivacion", "")

    descripcion_cv = (
        f"Experiencia: {experiencia} | "
        f"Habilidades: {', '.join(habilidades)} | "
        f"Certificación: {certificacion} | "
        f"Disponibilidad: {horas_semana} hrs/semana | "
        f"Tipos de desastre: {', '.join(tipo_desastre)} | "
        f"Condición médica: {condicion_medica} | "
        f"Vehículo: {vehiculo} | "
        f"Motivación: {motivacion}"
    )

    if curriculum:
        curriculum.Descripcion_CV = descripcion_cv
    else:
        curriculum = Curriculum(ID_Usuario=usuario.ID, Descripcion_CV=descripcion_cv)
        db.session.add(curriculum)
    db.session.flush()

    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()
    if not voluntario:
        voluntario = Voluntario(
            ID_Usuario             = usuario.ID,
            Nivel_Experiencia      = experiencia,
            Estatus                = "Activo",
            Horario_disponibilidad = horas_semana or "Por definir",
        )
        db.session.add(voluntario)
    else:
        voluntario.Nivel_Experiencia      = experiencia
        voluntario.Horario_disponibilidad = horas_semana or voluntario.Horario_disponibilidad

    db.session.commit()
    flash("¡Cuestionario enviado! El equipo de coordinación revisará tu perfil.", "success")
    return redirect(url_for("dashboard.perfil"))


# ── POST: subir certificado ─────────────────────────────────
@dashboard_bp.route("/perfil/certificado", methods=["POST"])
@login_required
def subir_certificado():
    usuario    = get_current_user()
    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()

    if not voluntario:
        flash("Debes completar el cuestionario de voluntario primero.", "error")
        return redirect(url_for("dashboard.perfil"))

    nombre_cert  = request.form.get("nombre_cert", "Certificado")
    archivo_cert = request.files.get("archivo_cert")

    if not archivo_cert or not archivo_cert.filename:
        flash("Selecciona un archivo para subir.", "error")
        return redirect(url_for("dashboard.perfil"))

    ext = archivo_cert.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pdf", "jpg", "jpeg", "png", "webp"}:
        flash("Formato no permitido. Usa PDF, JPG o PNG.", "error")
        return redirect(url_for("dashboard.perfil"))

    uploads_dir = os.path.join("app", "static", "uploads", "certificados")
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"cert_{usuario.ID}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
    archivo_cert.save(os.path.join(uploads_dir, filename))

    # Reporte genérico para anclar la evidencia
    reporte_cert = Reporte.query.filter_by(
        ID_Voluntario=voluntario.ID,
        Lugar="Certificados del voluntario"
    ).first()

    if not reporte_cert:
        reporte_cert = Reporte(
            Lugar                  = "Certificados del voluntario",
            Descripcion_Emergencia = "Repositorio de certificados",
            Estatus                = "Finalizado",
            Prioridad              = "Baja",
            ID_Voluntario          = voluntario.ID,
        )
        db.session.add(reporte_cert)
        db.session.flush()

    db.session.add(Evidencia(
        Archivo_Ruta      = f"uploads/certificados/{filename}",
        Nombre            = nombre_cert,
        Tipo_Evidencia_ID = 3,
        ID_Reporte        = reporte_cert.ID,
    ))
    db.session.commit()

    flash(f"Certificado '{nombre_cert}' subido correctamente.", "success")
    return redirect(url_for("dashboard.perfil"))


# ── POST: eliminar certificado ───────────────────────────────
@dashboard_bp.route("/perfil/certificado/<int:evidencia_id>/eliminar", methods=["POST"])
@login_required
def eliminar_certificado(evidencia_id):
    usuario    = get_current_user()
    evidencia  = Evidencia.query.get_or_404(evidencia_id)
    voluntario = Voluntario.query.filter_by(ID_Usuario=usuario.ID).first()

    # Verificar que el certificado pertenece al usuario actual
    reporte = Reporte.query.get(evidencia.ID_Reporte)
    if not voluntario or not reporte or reporte.ID_Voluntario != voluntario.ID:
        flash("No tienes permiso para eliminar este certificado.", "error")
        return redirect(url_for("dashboard.perfil"))

    # Eliminar archivo físico si existe
    if evidencia.Archivo_Ruta:
        ruta_fisica = os.path.join("app", "static", evidencia.Archivo_Ruta)
        if os.path.exists(ruta_fisica):
            os.remove(ruta_fisica)

    db.session.delete(evidencia)
    db.session.commit()
    flash("Certificado eliminado correctamente.", "success")
    return redirect(url_for("dashboard.perfil"))


# ═══════════════════════════════════════════════════════════════
#  CAPACITACIONES  →  GET /dashboard/capacitaciones
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/capacitaciones")
@login_required
def capacitaciones():
    return render_template(
        "capacitaciones.html",
        active_page = "capacitaciones",
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
        active_page = "foro",
        discusiones = discusiones,
        usuario     = get_current_user(),
    )


# ── POST: crear nueva discusión ── (CORREGIDO) ──────────────
@dashboard_bp.route("/foro/nueva", methods=["POST"])
@login_required
def foro_nueva():
    try:
        titulo    = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()

        if not titulo:
            flash("El título es obligatorio.", "error")
            return redirect(url_for("dashboard.foro"))

        if not contenido:
            flash("El contenido no puede estar vacío.", "error")
            return redirect(url_for("dashboard.foro"))

        nuevo_blog = Blog(
            Titulo      = titulo[:100],
            Descripcion = contenido[:100],
        )
        db.session.add(nuevo_blog)
        db.session.flush()

        db.session.add(ContenidoBlog(
            Contenido = contenido[:1000],
            ID_Blog   = nuevo_blog.ID_Blog,
        ))
        db.session.commit()
        flash("¡Discusión publicada exitosamente!", "success")

    except Exception as e:
        db.session.rollback()
        print("ERROR FORO NUEVA:", e)
        flash(f"Error al publicar la discusión: {str(e)}", "error")

    return redirect(url_for("dashboard.foro"))


# ── GET: detalle de discusión ────────────────────────────────
@dashboard_bp.route("/foro/<int:blog_id>")
@login_required
def foro_detalle(blog_id):
    blog       = Blog.query.get_or_404(blog_id)
    contenidos = ContenidoBlog.query.filter_by(ID_Blog=blog_id).all()
    respuestas = (
        RespuestaForo.query
        .filter_by(ID_Blog=blog_id)
        .order_by(RespuestaForo.Fecha.asc())
        .all()
    )
    return render_template(
        "foro_detalle.html",
        active_page = "foro",
        blog        = blog,
        contenidos  = contenidos,
        respuestas  = respuestas,
        usuario     = get_current_user(),
    )


# ── POST: agregar respuesta a discusión ──────────────────────
@dashboard_bp.route("/foro/<int:blog_id>/responder", methods=["POST"])
@login_required
def foro_responder(blog_id):
    Blog.query.get_or_404(blog_id)
    contenido = request.form.get("contenido", "").strip()
    if not contenido:
        flash("La respuesta no puede estar vacía.", "error")
        return redirect(url_for("dashboard.foro_detalle", blog_id=blog_id))
    db.session.add(RespuestaForo(
        ID_Blog    = blog_id,
        ID_Usuario = get_current_user().ID,
        Contenido  = contenido[:1000],
    ))
    db.session.commit()
    flash("Respuesta publicada.", "success")
    return redirect(url_for("dashboard.foro_detalle", blog_id=blog_id))


# ═══════════════════════════════════════════════════════════════
#  REPORTE  →  GET /dashboard/reporte
# ═══════════════════════════════════════════════════════════════
@dashboard_bp.route("/reporte")
@login_required
def reporte():
    return render_template(
        "reporte.html",
        active_page = "reporte",
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
    flash("¡Reporte enviado exitosamente! Gracias por tu ayuda.", "success")
    return redirect(url_for("dashboard.reporte"))