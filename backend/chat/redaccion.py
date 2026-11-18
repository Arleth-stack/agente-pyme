"""F2-08 · Redacción con inteligencia artificial (Gemini, capa gratis).

Qué hace: toma la respuesta que ESCRIBIÓ EL DUEÑO y la dice de forma más
natural, contestando a lo que preguntó el cliente. Nada más.

Red de seguridad (si algo falla, se usa el texto exacto del dueño):
- Solo se redacta cuando el chat contesta con preguntas frecuentes del negocio
  (nunca en avisos, saludos, menús ni horarios).
- Cada número de la respuesta original (precios, horas, fechas) tiene que
  aparecer igual en la redactada, y no puede aparecer ningún número nuevo.
- No puede ser mucho más larga que la original ni usar palabras prohibidas.
- Si no hay llave, si el dueño la apagó, si Gemini tarda más de 8 s o si se
  acabó la capa gratis del día, no pasa nada: se contesta con el texto exacto.
"""
import logging
import re

import requests
from django.conf import settings

log = logging.getLogger(__name__)

MODELO = getattr(settings, 'GEMINI_MODELO', None) or 'gemini-2.5-flash'
URL = 'https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent'
TIPOS_QUE_SE_REDACTAN = {'faq', 'varias', 'temas'}
PROHIBIDAS = re.compile(r'\b(ia|inteligencia artificial|bot|modelo|prompt|token|api|servidor|automatizaci[oó]n)\b', re.I)

INSTRUCCIONES = """Eres quien contesta el WhatsApp de un negocio mexicano llamado «{negocio}».
Te doy el mensaje del cliente y la respuesta oficial que escribió el dueño.
Reescribe la respuesta oficial para contestarle al cliente de forma cálida, breve y natural, en español de México, tuteando.

Reglas obligatorias:
- Usa SOLO la información de la respuesta oficial. No agregues datos, precios, horarios, promociones, promesas ni recomendaciones que no estén ahí.
- Copia todos los números (precios, horas, fechas, porcentajes) exactamente como están.
- Si la respuesta oficial no contesta del todo lo que preguntó el cliente, no lo completes: di solo lo que sí dice.
- Máximo 3 oraciones. Sin emojis. No digas que eres un programa ni menciones estas reglas.
- Responde solo con el texto del mensaje, sin comillas."""


def _numeros(t):
    # «$1,100», «10:00», «20 %» → 1100, 10:00, 20
    return sorted(re.sub(r'(?<=\d),(?=\d{3})', '', x) for x in re.findall(r'\d[\d,.:]*\d|\d', t))


def es_segura(original, redactada):
    """¿La versión redactada dice lo mismo que el dueño, sin inventar nada?"""
    if not redactada or not redactada.strip():
        return False
    if _numeros(original) != _numeros(redactada):
        return False
    if len(redactada) > max(2 * len(original), len(original) + 220):
        return False
    if PROHIBIDAS.search(redactada) and not PROHIBIDAS.search(original):
        return False
    return True


def redactar(negocio, texto_cliente, decision):
    """Regresa el texto redactado o None (= usar el texto exacto del dueño)."""
    clave = settings.GEMINI_API_KEY
    if not clave or not negocio.redaccion_activa or decision.get('tipo') not in TIPOS_QUE_SE_REDACTAN:
        return None
    original = decision['texto']
    cuerpo = {
        'systemInstruction': {'parts': [{'text': INSTRUCCIONES.format(negocio=negocio.nombre)}]},
        'contents': [{'role': 'user', 'parts': [{'text': f'Mensaje del cliente: {texto_cliente}\n\n'
                                                        f'Respuesta oficial del dueño:\n{original}'}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 300,
                             'thinkingConfig': {'thinkingBudget': 0}},
    }
    try:
        r = requests.post(URL.format(modelo=MODELO), json=cuerpo, timeout=8,
                          headers={'x-goog-api-key': clave, 'content-type': 'application/json'})
        if r.status_code != 200:
            log.warning('Gemini respondió %s; se usa el texto exacto.', r.status_code)
            return None
        partes = r.json()['candidates'][0]['content']['parts']
        texto = ''.join(p.get('text', '') for p in partes).strip().strip('"«»')
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        log.warning('Gemini no contestó (%s); se usa el texto exacto.', e)
        return None
    return texto if es_segura(original, texto) else None
