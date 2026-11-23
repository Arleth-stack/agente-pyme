"""Conexión con Gemini: redacta con naturalidad la respuesta que escribió el dueño.

Si algo falla (sin llave, redacción apagada, Gemini lento o saturado, se acabó
la capa gratis, o la versión redactada cambia o agrega datos) se usa el texto
exacto del dueño.
"""
import logging
import re
import time

from django.conf import settings
from google import genai
from google.genai import errors, types

log = logging.getLogger(__name__)

ESPERA_MAXIMA_S = 6
ESPERA_POR_MODELO_S = 3.5
TIPOS_QUE_SE_REDACTAN = {'faq', 'varias', 'temas'}
PROHIBIDAS = re.compile(r'\b(ia|inteligencia artificial|bot|modelo|prompt|token|api|servidor|automatizaci[oó]n)\b', re.I)

INSTRUCCIONES = """Eres quien contesta el WhatsApp de un negocio mexicano llamado «{negocio}».
Te doy el mensaje del cliente y la respuesta oficial que escribió el dueño.
Reescribe la respuesta oficial para contestarle al cliente de forma cálida, breve y natural, en español de México, tuteando.

Reglas obligatorias:
- Usa SOLO la información de la respuesta oficial. No agregues datos, precios, horarios, promociones, promesas ni recomendaciones que no estén ahí.
- Copia todos los números (precios, horas, fechas, porcentajes) exactamente como están.
- Si la respuesta oficial no contesta del todo lo que preguntó el cliente, no lo completes: di solo lo que sí dice.
- No agregues despedidas, invitaciones ni ofrecimientos (nada de «quedo a tus órdenes», «agenda tu cita», «te esperamos»).
- Máximo 3 oraciones. Sin emojis. No digas que eres un programa ni menciones estas reglas.
- Responde solo con el texto del mensaje, sin comillas."""

# Palabras de cortesía o de enlace que sí puede agregar sin cambiar lo que dice el dueño.
CORTESIA = frozenset("""
hola claro gusto cuento tenemos manejamos hacemos ofrecemos contamos esta estan queda quedan
sale salen costo cuesta cuestan precio precios tambien mientras ademas cada uno una sobre
""".split())
PALABRAS_NUEVAS_PERMITIDAS = 1
# Temas que cambian lo que el negocio ofrece: si el dueño no los escribió, nunca se agregan.
SENSIBLES = frozenset('cita promocion promociones descuento descuentos gratis regalo domicilio garantia oferta ofertas'.split())


def _numeros(t):
    """«$1,100», «10:00», «20 %» → ['1100', '10:00', '20']."""
    return sorted(re.sub(r'(?<=\d),(?=\d{3})', '', x) for x in re.findall(r'\d[\d,.:]*\d|\d', t))


def palabras_nuevas(original, redactada, cliente=''):
    """Palabras con contenido que la versión redactada trae y el dueño no escribió."""
    from chat.servicios import palabras, se_parecen
    conocidas = palabras(original) | palabras(cliente) | CORTESIA
    return {w for w in palabras(redactada) if not any(se_parecen(w, c) for c in conocidas)}


def es_segura(original, redactada, cliente=''):
    """¿La versión redactada dice lo mismo que el dueño, sin inventar nada?"""
    if not redactada or not redactada.strip():
        return False
    nuevas = palabras_nuevas(original, redactada, cliente)
    if len(nuevas) > PALABRAS_NUEVAS_PERMITIDAS or nuevas & SENSIBLES:
        return False
    if _numeros(original) != _numeros(redactada):
        return False
    if len(redactada) > max(2 * len(original), len(original) + 220):
        return False
    return not (PROHIBIDAS.search(redactada) and not PROHIBIDAS.search(original))


def _pedir(modelo, instrucciones, contenido, espera_s):
    """Una llamada a Gemini; regresa el texto o lanza el error de Google."""
    cliente = genai.Client(api_key=settings.GEMINI_API_KEY,
                           http_options=types.HttpOptions(timeout=int(espera_s * 1000)))
    r = cliente.models.generate_content(
        model=modelo, contents=contenido,
        config=types.GenerateContentConfig(
            system_instruction=instrucciones, temperature=0.3, max_output_tokens=400,
            thinking_config=types.ThinkingConfig(thinking_budget=0)))
    return (r.text or '').strip().strip('"«»')


def redactar(negocio, texto_cliente, decision):
    """Regresa el texto redactado o None (= usar el texto exacto del dueño)."""
    if not settings.GEMINI_API_KEY or not negocio.redaccion_activa or decision.get('tipo') not in TIPOS_QUE_SE_REDACTAN:
        return None
    original = decision['texto']
    instrucciones = INSTRUCCIONES.format(negocio=negocio.nombre)
    contenido = f'Mensaje del cliente: {texto_cliente}\n\nRespuesta oficial del dueño:\n{original}'
    limite = time.monotonic() + ESPERA_MAXIMA_S
    for modelo in settings.GEMINI_MODELOS:
        quedan = limite - time.monotonic()
        if quedan < 1:
            break
        try:
            texto = _pedir(modelo, instrucciones, contenido, min(quedan, ESPERA_POR_MODELO_S))
        except errors.APIError as e:
            if e.code == 429:  # se acabó la capa gratis: no tiene caso insistir
                log.warning('Gemini sin capa gratis (429); se usa el texto exacto.')
                return None
            log.warning('Gemini %s respondió %s; se prueba el siguiente.', modelo, e.code)
            continue
        except Exception as e:  # noqa: BLE001 — tiempo agotado o red caída
            log.warning('Gemini %s no contestó (%s).', modelo, type(e).__name__)
            continue
        return texto if es_segura(original, texto, texto_cliente) else None
    return None
