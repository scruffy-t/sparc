from PyQt5.QtGui import QColor

from sparc.core import Types


class ColorSerializer(object):
    """Serialize QColor instances as hex strings."""

    @staticmethod
    def deserialize(text, **kwargs):
        if not len(text) == 9:
            raise ValueError(f'malformed hex color {text:!r}')
        text = text.lstrip('#')
        r, g, b, a = tuple([int(text[i:i+2], 16) for i in (0, 2, 4, 6)])
        return QColor(r=r, g=g, b=b, alpha=a)

    @staticmethod
    def serialize(obj):
        assert isinstance(obj, QColor)
        r, g, b, a = obj.getRgb()
        return f'#{r:02x}{g:02x}{b:02x}{a:02x}'


Types.register_type('Color', QColor, ColorSerializer)
