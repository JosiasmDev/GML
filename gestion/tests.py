# gestion/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Proyecto, Tarea

class ProyectoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Prueba',
            descripcion='Descripción',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            creador=self.user
        )
        self.proyecto.usuarios.add(self.user)

    def test_proyecto_creado(self):
        proyecto = Proyecto.objects.get(titulo='Proyecto Prueba')
        self.assertEqual(proyecto.descripcion, 'Descripción')

    def test_tarea_asignada(self):
        tarea = Tarea.objects.create(
            proyecto=self.proyecto,
            titulo='Tarea Prueba',
            descripcion='Hacer algo',
            fecha_limite='2025-06-01',
            estado='pendiente'
        )
        tarea.asignados.add(self.user)
        self.assertIn(self.user, tarea.asignados.all())