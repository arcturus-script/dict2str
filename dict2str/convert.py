"""Backward-compatibility shim.

The element renderers now live in :mod:`dict2str.elements`. This module
re-exports every historical name (the element classes and the
``replace_tag`` / ``replace_style`` helpers) so existing imports such as
``from dict2str import convert`` or ``from dict2str.convert import h1``
keep working.
"""

from .utils import replace_tag, replace_style
from .elements import (
    REGISTRY,
    call_element,
    register,
    render_nested,
    supported_elements,
    blockQuote,
    bold,
    code,
    convert,
    h,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    img,
    italic,
    link,
    orderedList,
    strikethrough,
    table,
    taskList,
    txt,
    unOrderedList,
)

__all__ = [
    "REGISTRY",
    "register",
    "call_element",
    "render_nested",
    "supported_elements",
    "replace_tag",
    "replace_style",
    "convert",
    "txt",
    "bold",
    "italic",
    "strikethrough",
    "blockQuote",
    "code",
    "h",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "link",
    "orderedList",
    "unOrderedList",
    "taskList",
    "table",
]
