"""Cuentas: el dueño entra con su número de WhatsApp (10 dígitos) y su contraseña."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

telefono_10 = RegexValidator(r'^[0-9]{10}$', 'Escribe tu WhatsApp con 10 dígitos.')


def solo_digitos(valor):
    """«55 1234-5678» → «5512345678»."""
    return ''.join(c for c in str(valor or '') if c.isdigit())


class UsuarioManager(BaseUserManager):
    """Crea cuentas a partir del número de WhatsApp."""

    def create_user(self, telefono, password=None, **extra):
        telefono = solo_digitos(telefono)
        if len(telefono) != 10:
            raise ValueError('El WhatsApp debe tener 10 dígitos.')
        usuario = self.model(telefono=telefono, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, telefono, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True)
        return self.create_user(telefono, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Persona que entra al panel de un negocio."""

    telefono = models.CharField('WhatsApp', max_length=10, unique=True, validators=[telefono_10])
    nombre = models.CharField('nombre', max_length=80, blank=True)
    correo = models.EmailField('correo', blank=True, help_text='Opcional: para los recibos de Stripe.')
    is_active = models.BooleanField('activa', default=True)
    is_staff = models.BooleanField('equipo de Merkatics', default=False)
    date_joined = models.DateTimeField('creada', default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'telefono'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'cuenta'
        verbose_name_plural = 'cuentas'

    def __str__(self):
        t = self.telefono
        return f'{t[:2]} {t[2:6]} {t[6:]}' + (f' · {self.nombre}' if self.nombre else '')
