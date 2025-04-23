from django.urls import path
from . import views

urlpatterns = [
    # Vistas de proyectos
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('<int:proyecto_id>/', views.vista_proyecto, name='vista_proyecto'),
    path('<int:proyecto_id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),

    # Vistas de tareas
    path('<int:proyecto_id>/tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('tareas/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('tareas/<int:tarea_id>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),

    # Vistas de comentarios
    path('tareas/<int:tarea_id>/comentarios/agregar/', views.agregar_comentario, name='agregar_comentario'),
    path('comentarios/<int:comentario_id>/editar/', views.editar_comentario, name='editar_comentario'),
    path('comentarios/<int:comentario_id>/eliminar/', views.eliminar_comentario, name='eliminar_comentario'),

    # Vistas de mensajes privados
    path('mensaje/nuevo/', views.enviar_mensaje_privado, name='enviar_mensaje_privado'),
    path('mensaje/<int:mensaje_id>/editar/', views.editar_mensaje, name='editar_mensaje'),
    path('mensaje/<int:mensaje_id>/eliminar/', views.eliminar_mensaje, name='eliminar_mensaje'),  # Corregido
    path('chat/<int:usuario_id>/borrar/', views.borrar_chat, name='borrar_chat'),

    # Vistas de mensajes de proyecto
    path('<int:proyecto_id>/mensajes/enviar/', views.enviar_mensaje_proyecto, name='enviar_mensaje_proyecto'),
    path('mensajes/proyecto/<int:mensaje_id>/eliminar/', views.eliminar_mensaje_proyecto, name='eliminar_mensaje_proyecto'),

    # Vistas de grupos
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/<int:grupo_id>/', views.gestionar_grupo, name='gestionar_grupo'),

    # Vistas de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('registro/', views.registro, name='registro'),  # Añadida la ruta para registro

    # Vistas de notificaciones
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),
    path('notificaciones/marcar/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas/', views.marcar_todas_notificaciones_leidas, name='marcar_todas_notificaciones_leidas'),
]