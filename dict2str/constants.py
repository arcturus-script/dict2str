"""Format related constants.

``C`` (the legacy element module alias) and ``T`` (format -> render
method) are kept for backward compatibility.
"""

from . import convert as C

#: output format name -> renderer method name
T = {
    "markdown": "toMd",
    "html": "toHtml",
    "txt": "toTxt",
}

#: supported output format names
SUPPORTED_TYPES = tuple(T)
