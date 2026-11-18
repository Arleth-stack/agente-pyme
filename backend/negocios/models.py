"""Negocios, sus miembros y sus preguntas frecuentes.

Mismas reglas que las tablas de Supabase de la Fase 1 (ver
supabase/migrations/20261019000001_esquema.sql): las validaciones viven aquí y
también como restricciones de MySQL, para que nadie las pueda saltar.
"""
import re
import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length

GIROS = [
    ('consultorio', 'Consultorio o clínica'),
    ('salon', 'Salón o barbería'),
    ('gimnasio', 'Gimnasio o estudio'),
    ('inmobiliaria', 'Inmobiliaria'),
    ('taller', 'Taller'),
    ('otro', 'Otro'),
]
PLAN_ESTADOS = [
    ('sin_activar', 'Sin activar'),
    ('prueba', 'Prueba gratis'),
    ('activa', 'Activa'),
    ('pago_pendiente', 'Pago pendiente'),
    ('cancelada', 'Cancelada'),
]
TEMAS = [
    ('horarios', 'Horarios'), ('precios', 'Precios'), ('servicios', 'Servicios'),
    ('citas', 'Citas'), ('pagos', 'Pagos'), ('ubicacion', 'Ubicación'), ('otros', 'Otros'),
]
ROLES = [('dueno', 'Dueño'), ('encargado', 'Encargado')]
DIAS = ('lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom')

models.CharField.register_lookup(Length)
models.TextField.register_lookup(Length)

telefono_10 = RegexValidator(r'^[0-9]{10}$', 'El número debe tener 10 dígitos.')


class Negocio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(max_length=70, unique=True,
                            validators=[RegexValidator(r'^[a-z0-9]+(-[a-z0-9]+)*$')])
    nombre = models.CharField(max_length=60, validators=[MinLengthValidator(2)])
    giro = models.CharField(max_length=20, choices=GIROS)
    telefono = models.CharField(max_length=10, validators=[telefono_10])
    direccion = models.CharField(max_length=120, null=True, blank=True)
    zona_horaria = models.CharField(max_length=60, default='America/Mexico_City')
    # {"lun": {"abre": "09:00", "cierra": "19:00"}, "dom": null, ...}; null = cerrado
    horario = models.JSONField()
    es_demo = models.BooleanField(default=False)
    merkatics_org_id = models.CharField(max_length=80, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    # Prueba gratis y plan mensual (Stripe). El dueño los ve pero no los cambia.
    plan_estado = models.CharField(max_length=20, choices=PLAN_ESTADOS, default='sin_activar')
    prueba_termina = models.DateTimeField(null=True, blank=True)
    plan_termina = models.DateTimeField(null=True, blank=True)
    stripe_cliente = models.CharField(max_length=80, null=True, blank=True)
    stripe_suscripcion = models.CharField(max_length=80, null=True, blank=True, unique=True)
    plan_actualizado = models.DateTimeField(null=True, blank=True)

    # F2-08: el dueño puede apagar la redacción con inteligencia artificial.
    redaccion_activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'negocios'
        ordering = ['nombre']
        constraints = [
            models.CheckConstraint(condition=Q(giro__in=[g for g, _ in GIROS]), name='negocio_giro_valido'),
            models.CheckConstraint(condition=Q(plan_estado__in=[p for p, _ in PLAN_ESTADOS]), name='negocio_plan_valido'),
            models.CheckConstraint(condition=Q(telefono__regex=r'^[0-9]{10}$'), name='negocio_telefono_10'),
            models.CheckConstraint(condition=Q(slug__regex=r'^[a-z0-9]+(-[a-z0-9]+)*$'), name='negocio_slug_valido'),
        ]

    def __str__(self):
        return self.nombre


class Miembro(models.Model):
    """Quién puede entrar al panel de un negocio y con qué rol."""
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='miembros')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membresias')
    rol = models.CharField(max_length=12, choices=ROLES, default='dueno')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'miembros'
        constraints = [
            models.UniqueConstraint(fields=['negocio', 'usuario'], name='miembro_unico'),
            models.CheckConstraint(condition=Q(rol__in=['dueno', 'encargado']), name='miembro_rol_valido'),
        ]


class Pregunta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='preguntas')
    tema = models.CharField(max_length=12, choices=TEMAS)
    pregunta = models.CharField(max_length=150, validators=[MinLengthValidator(3)])
    otras_formas = models.CharField(max_length=300, null=True, blank=True)
    respuesta = models.TextField(max_length=500)
    activa = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'preguntas'
        ordering = ['orden', 'pregunta']
        constraints = [
            # La comparación de MySQL (utf8mb4_0900_ai_ci) ignora mayúsculas y acentos:
            # «¿Cuánto cuesta?» y «¿cuanto cuesta?» cuentan como la misma pregunta.
            models.UniqueConstraint(fields=['negocio', 'pregunta'], name='pregunta_sin_repetir'),
            models.CheckConstraint(condition=Q(tema__in=[t for t, _ in TEMAS]), name='pregunta_tema_valido'),
            models.CheckConstraint(condition=Q(respuesta__length__gte=1), name='pregunta_con_respuesta'),
        ]

    def save(self, *args, **kwargs):
        self.pregunta = (self.pregunta or '').strip()
        self.respuesta = (self.respuesta or '').strip()
        self.otras_formas = (self.otras_formas or '').strip() or None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.pregunta


def horario_valido(h):
    """Igual que public.horario_valido de la Fase 1."""
    if not isinstance(h, dict) or not h or any(k not in DIAS for k in h):
        return False
    abiertos = 0
    for v in h.values():
        if v is None:
            continue
        if not isinstance(v, dict):
            return False
        abre, cierra = v.get('abre', ''), v.get('cierra', '')
        if not (re.fullmatch(r'\d{2}:\d{2}', str(abre)) and re.fullmatch(r'\d{2}:\d{2}', str(cierra))):
            return False
        if not abre < cierra:
            return False
        abiertos += 1
    return abiertos > 0
