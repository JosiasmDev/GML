from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from notifications.signals import notify
from .models import Proyecto, Tarea, Mensaje, Comentario, Rol, Grupo, MensajeProyecto
from .forms import ProyectoForm, TareaForm, MensajeForm, ComentarioForm, RegistroForm

# Vistas generales
def inicio(request):
    if request.user.is_authenticated:
        return redirect('lista_proyectos')
    return redirect('login')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'gestion/registro.html', {'form': form})

# Vistas de proyectos
@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'gestion/lista_proyectos.html', {'proyectos': proyectos})

@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            # Obtener los usuarios seleccionados del formulario
            usuarios_seleccionados = form.cleaned_data['usuarios']
            print("Usuarios seleccionados en el formulario:", usuarios_seleccionados)  # Depuración
            # Asignar los usuarios seleccionados al proyecto
            for usuario in usuarios_seleccionados:
                proyecto.usuarios.add(usuario)
            proyecto.usuarios.add(request.user)  # Asegurar que el creador esté asignado
            print("Usuarios asignados al proyecto después de guardar:", proyecto.usuarios.all())  # Depuración
            # Notificar a todos los usuarios asignados (excepto el creador)
            for usuario in proyecto.usuarios.all():
                if usuario != request.user:
                    print(f"Enviando notificación a {usuario.username}")  # Depuración
                    notify.send(
                        sender=request.user,
                        recipient=usuario,
                        verb='te asignó al proyecto',
                        target=proyecto,
                        description=f'Proyecto: {proyecto.titulo}'
                    )
            Rol.objects.create(usuario=request.user, proyecto=proyecto, rol='administrador')
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'gestion/crear_proyecto.html', {'form': form})

@login_required
def vista_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    rol = Rol.objects.filter(usuario=request.user, proyecto=proyecto).first()
    if request.user not in proyecto.usuarios.all() and (not rol or rol.rol != 'administrador'):
        return render(request, 'gestion/sin_permiso.html')
    
    tareas = proyecto.tareas.all()
    mensajes = proyecto.mensajes.all()
    estado = request.GET.get('estado', '')
    usuario_id = request.GET.get('usuario', '')
    if estado:
        tareas = tareas.filter(estado=estado)
    if usuario_id:
        tareas = tareas.filter(asignados__id=usuario_id)
    tareas = tareas.order_by('fecha_limite')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        usuario_id = request.POST.get('usuario')
        if accion == 'agregar' and usuario_id:
            usuario = User.objects.get(id=usuario_id)
            proyecto.usuarios.add(usuario)
            Rol.objects.get_or_create(usuario=usuario, proyecto=proyecto, defaults={'rol': 'miembro'})
            notify.send(
                request.user,
                recipient=usuario,
                verb='te asignó al proyecto',
                target=proyecto,
                description=f'Proyecto: {proyecto.titulo}'
            )
        elif accion == 'quitar' and usuario_id:
            usuario = User.objects.get(id=usuario_id)
            proyecto.usuarios.remove(usuario)
            Rol.objects.filter(usuario=usuario, proyecto=proyecto).delete()
            notify.send(
                request.user,
                recipient=usuario,
                verb='te quitó del proyecto',
                target=proyecto,
                description=f'Proyecto: {proyecto.titulo}'
            )
        elif accion == 'cambiar_rol' and usuario_id:
            rol = request.POST.get('rol')
            usuario = User.objects.get(id=usuario_id)
            Rol.objects.update_or_create(usuario=usuario, proyecto=proyecto, defaults={'rol': rol})
            notify.send(
                request.user,
                recipient=usuario,
                verb='cambió tu rol en el proyecto',
                target=proyecto,
                description=f'Proyecto: {proyecto.titulo}, nuevo rol: {rol}'
            )

    usuarios_con_roles = []
    for usuario in proyecto.usuarios.all():
        rol_obj = Rol.objects.filter(usuario=usuario, proyecto=proyecto).first()
        usuarios_con_roles.append({'usuario': usuario, 'rol': rol_obj.rol if rol_obj else 'Sin rol'})

    return render(request, 'gestion/proyecto.html', {
        'proyecto': proyecto,
        'tareas': tareas,
        'mensajes': mensajes,
        'usuarios_con_roles': usuarios_con_roles,
        'todos_los_usuarios': User.objects.all()
    })

@login_required
def editar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            # Notificar a todos los usuarios asignados sobre la edición
            for usuario in proyecto.usuarios.all():
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='modificó el proyecto',
                    target=proyecto,
                    description=f'Proyecto: {proyecto.titulo}'
                )
            return redirect('vista_proyecto', proyecto_id=proyecto.id)
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'gestion/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

@login_required
def eliminar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        # Guardar la lista de usuarios antes de eliminar
        usuarios_asignados = list(proyecto.usuarios.all())
        proyecto_titulo = proyecto.titulo
        proyecto.delete()
        # Notificar a todos los usuarios asignados sobre la eliminación
        for usuario in usuarios_asignados:
            notify.send(
                request.user,
                recipient=usuario,
                verb='eliminó el proyecto',
                target=None,  # El proyecto ya no existe
                description=f'Proyecto: {proyecto_titulo}'
            )
        return redirect('lista_proyectos')
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': proyecto, 'tipo': 'proyecto'})

# Vistas de tareas
@login_required
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.proyecto = proyecto
            tarea.save()
            form.save_m2m()  # Guardar los usuarios asignados
            # Enviar una sola notificación a los asignados
            for usuario in tarea.asignados.all():
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='te asignó la tarea',
                    target=tarea,
                    description=f'Tarea: {tarea.titulo} en {proyecto.titulo}'
                )
            return redirect('vista_proyecto', proyecto_id=proyecto.id)
    else:
        form = TareaForm()
    return render(request, 'gestion/crear_tarea.html', {'form': form, 'proyecto': proyecto})

@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            # Notificar a todos los asignados sobre cualquier modificación
            for usuario in tarea.asignados.all():
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='modificó la tarea',
                    target=tarea,
                    description=f'Tarea: {tarea.titulo} en {tarea.proyecto.titulo}'
                )
            return redirect('vista_proyecto', proyecto_id=tarea.proyecto.id)
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'gestion/editar_tarea.html', {'form': form, 'tarea': tarea})

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        proyecto_id = tarea.proyecto.id
        tarea.delete()
        return redirect('vista_proyecto', proyecto_id=proyecto_id)
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': tarea, 'tipo': 'tarea'})

# Vistas de comentarios
@login_required
def agregar_comentario(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.autor = request.user
            comentario.save()
            for usuario in tarea.asignados.all():
                if usuario != request.user:
                    notify.send(
                        request.user,
                        recipient=usuario,
                        verb='comentó en una tarea',
                        target=tarea,
                        description=f'Comentario: {comentario.contenido[:50]}'
                    )
            return redirect('vista_proyecto', proyecto_id=tarea.proyecto.id)
    else:
        form = ComentarioForm()
    return render(request, 'gestion/agregar_comentario.html', {'form': form, 'tarea': tarea})

@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)
    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            return redirect('vista_proyecto', proyecto_id=comentario.tarea.proyecto.id)
    else:
        form = ComentarioForm(instance=comentario)
    return render(request, 'gestion/editar_comentario.html', {'form': form, 'comentario': comentario})

@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)
    if request.method == 'POST':
        proyecto_id = comentario.tarea.proyecto.id
        comentario.delete()
        return redirect('vista_proyecto', proyecto_id=proyecto_id)
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': comentario, 'tipo': 'comentario'})

# Vistas de mensajes privados
@login_required
def enviar_mensaje_privado(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.save()
            # Enviar UNA sola notificación con el contenido
            notify.send(
                request.user,
                recipient=mensaje.destinatario,
                verb='te envió un mensaje',
                target=mensaje,
                description=mensaje.contenido  # Solo el contenido del mensaje
            )
            return redirect(request.META.get('HTTP_REFERER', 'lista_proyectos'))
    else:
        form = MensajeForm()
    return render(request, 'gestion/enviar_mensaje_privado.html', {'form': form})

@login_required
def editar_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id, remitente=request.user)
    if request.method == 'POST':
        form = MensajeForm(request.POST, instance=mensaje)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', 'lista_proyectos'))
    else:
        form = MensajeForm(instance=mensaje)
    return render(request, 'gestion/editar_mensaje.html', {'form': form, 'mensaje': mensaje})

@login_required
def eliminar_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id, remitente=request.user)
    if request.method == 'POST':
        mensaje.delete()
        return redirect(request.META.get('HTTP_REFERER', 'lista_proyectos'))
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': mensaje, 'tipo': 'mensaje'})

@login_required
def borrar_chat(request, usuario_id):
    if request.method == 'POST':
        Mensaje.objects.filter(
            (models.Q(remitente=request.user) & models.Q(destinatario_id=usuario_id)) |
            (models.Q(destinatario=request.user) & models.Q(remitente_id=usuario_id))
        ).delete()
        return redirect('lista_proyectos')
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': User.objects.get(id=usuario_id), 'tipo': 'chat'})

# Vistas de mensajes de proyecto@login_required
def enviar_mensaje_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            mensaje = MensajeProyecto.objects.create(proyecto=proyecto, remitente=request.user, contenido=contenido)
            print("Usuarios asignados al proyecto:", proyecto.usuarios.all())  # Depuración
            from notifications.models import Notification  # Importar modelo directamente
            for usuario in proyecto.usuarios.all():
                if usuario != request.user:
                    print(f"Enviando notificación a {usuario.username} por mensaje: {contenido}")  # Depuración
                    Notification.objects.create(
                        recipient=usuario,
                        actor=request.user,
                        verb='envió un mensaje al proyecto',
                        target=mensaje,
                        description=f'Mensaje: {contenido} en {proyecto.titulo}'
                    )
        return redirect('vista_proyecto', proyecto_id=proyecto.id)
    return render(request, 'gestion/enviar_mensaje_proyecto.html', {'proyecto': proyecto})

@login_required
def eliminar_mensaje_proyecto(request, mensaje_id):
    mensaje = get_object_or_404(MensajeProyecto, id=mensaje_id, remitente=request.user)
    if request.method == 'POST':
        mensaje.delete()
        return redirect('vista_proyecto', proyecto_id=mensaje.proyecto.id)
    return render(request, 'gestion/confirmar_eliminar.html', {'objeto': mensaje, 'tipo': 'mensaje_proyecto'})

# Vistas de grupos
@login_required
def lista_grupos(request):
    grupos = Grupo.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        proyecto_id = request.POST.get('proyecto')
        if nombre and proyecto_id:
            grupo = Grupo.objects.create(nombre=nombre, proyecto_id=proyecto_id)
            return redirect('lista_grupos')
    return render(request, 'gestion/lista_grupos.html', {'grupos': grupos, 'proyectos': Proyecto.objects.all()})

@login_required
def gestionar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'agregar':
            usuario_id = request.POST.get('usuario')
            rol = request.POST.get('rol')
            if usuario_id and rol:
                usuario = User.objects.get(id=usuario_id)
                grupo.miembros.add(usuario)
                Rol.objects.update_or_create(
                    usuario=usuario, 
                    proyecto=grupo.proyecto, 
                    defaults={'rol': rol}
                )
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='te asignó al grupo',
                    target=grupo,
                    description=f'Grupo: {grupo.nombre} en {grupo.proyecto.titulo}'
                )
        elif accion == 'quitar':
            usuario_id = request.POST.get('usuario')
            if usuario_id:
                usuario = User.objects.get(id=usuario_id)
                grupo.miembros.remove(usuario)
                Rol.objects.filter(usuario=usuario, proyecto=grupo.proyecto).delete()
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='te quitó del grupo',
                    target=grupo,
                    description=f'Grupo: {grupo.nombre} en {grupo.proyecto.titulo}'
                )
        elif accion == 'cambiar_rol':
            usuario_id = request.POST.get('usuario')
            rol = request.POST.get('rol')
            if usuario_id and rol:
                usuario = User.objects.get(id=usuario_id)
                Rol.objects.update_or_create(
                    usuario=usuario, 
                    proyecto=grupo.proyecto, 
                    defaults={'rol': rol}
                )
                notify.send(
                    request.user,
                    recipient=usuario,
                    verb='cambió tu rol en el grupo',
                    target=grupo,
                    description=f'Grupo: {grupo.nombre} en {grupo.proyecto.titulo}, nuevo rol: {rol}'
                )
        elif accion == 'eliminar':
            grupo.delete()
            return redirect('lista_grupos')
        elif accion == 'editar':
            nombre = request.POST.get('nombre')
            if nombre and nombre != grupo.nombre:
                grupo_nombre_antiguo = grupo.nombre
                grupo.nombre = nombre
                grupo.save()
                # Notificar a todos los miembros del grupo sobre el cambio de nombre
                for miembro in grupo.miembros.all():
                    notify.send(
                        request.user,
                        recipient=miembro,
                        verb='modificó el nombre del grupo',
                        target=grupo,
                        description=f'Grupo: {grupo_nombre_antiguo} ahora es {grupo.nombre} en {grupo.proyecto.titulo}'
                    )

    miembros_con_roles = []
    for miembro in grupo.miembros.all():
        try:
            rol_obj = Rol.objects.get(usuario=miembro, proyecto=grupo.proyecto)
            miembros_con_roles.append({'miembro': miembro, 'rol': rol_obj.rol})
        except Rol.DoesNotExist:
            miembros_con_roles.append({'miembro': miembro, 'rol': 'Sin rol'})

    return render(request, 'gestion/gestionar_grupo.html', {
        'grupo': grupo,
        'usuarios': User.objects.all(),
        'miembros_con_roles': miembros_con_roles
    })


# Vistas de usuarios
@login_required
def lista_usuarios(request):
    usuarios = User.objects.all()
    if request.method == 'POST':
        accion = request.POST.get('accion')
        usuario_id = request.POST.get('usuario')
        grupo_id = request.POST.get('grupo')
        rol = request.POST.get('rol')
        if accion == 'agregar' and usuario_id and grupo_id and rol:
            usuario = User.objects.get(id=usuario_id)
            grupo = Grupo.objects.get(id=grupo_id)
            grupo.miembros.add(usuario)
            Rol.objects.create(usuario=usuario, proyecto=grupo.proyecto, rol=rol)
            notify.send(
                request.user,
                recipient=usuario,
                verb='te asignó al grupo',
                target=grupo,
                description=f'Grupo: {grupo.nombre} en {grupo.proyecto.titulo}'
            )
        elif accion == 'quitar' and usuario_id and grupo_id:
            usuario = User.objects.get(id=usuario_id)
            grupo = Grupo.objects.get(id=grupo_id)
            grupo.miembros.remove(usuario)
            Rol.objects.filter(usuario=usuario, proyecto=grupo.proyecto).delete()
            notify.send(
                request.user,
                recipient=usuario,
                verb='te quitó del grupo',
                target=grupo,
                description=f'Grupo: {grupo.nombre} en {grupo.proyecto.titulo}'
            )

    usuarios_con_grupos = []
    for usuario in usuarios:
        grupos = usuario.grupos.all()
        usuarios_con_grupos.append({'usuario': usuario, 'grupos': grupos})

    return render(request, 'gestion/lista_usuarios.html', {
        'usuarios_con_grupos': usuarios_con_grupos,
        'grupos': Grupo.objects.all()
    })

@login_required
def lista_notificaciones(request):
    notificaciones = request.user.notifications.all().order_by('-timestamp')  # Ordenar por más reciente
    print("Notificaciones para", request.user.username, ":", notificaciones)  # Depuración
    return render(request, 'gestion/notificaciones.html', {'notificaciones': notificaciones})

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(request.user.notifications, id=notificacion_id)
    notificacion.mark_as_read()
    # Si la notificación está relacionada con un mensaje, marcarlo como leído
    if notificacion.target and isinstance(notificacion.target, Mensaje):
        mensaje = notificacion.target
        mensaje.leido = True
        mensaje.save()
    return redirect('lista_notificaciones')

@login_required
def marcar_todas_notificaciones_leidas(request):
    if request.method == 'POST':
        notificaciones = request.user.notifications.unread()
        for notificacion in notificaciones:
            notificacion.mark_as_read()
            if notificacion.target and isinstance(notificacion.target, Mensaje):
                mensaje = notificacion.target
                mensaje.leido = True
                mensaje.save()
        return redirect('lista_notificaciones')
    return redirect('lista_notificaciones')