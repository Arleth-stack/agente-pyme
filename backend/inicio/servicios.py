"""Código QR de los chats de ejemplo."""
import segno


def qr_svg(url):
    """SVG del QR que abre ese enlace; se arma aquí, el enlace no sale a ningún otro sitio."""
    return segno.make(url, error='m').svg_inline(scale=4, border=0, omitsize=True)
