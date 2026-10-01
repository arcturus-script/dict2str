"""Shared helper functions for dict2str renderers.

This module contains small utilities that are independent of any concrete
element:

* :func:`end_of`       -- read the trailing string of an element;
* :func:`escape_text`  -- escape text between HTML tags;
* :func:`escape_attr`  -- escape a value inside a single-quoted attribute;
* :func:`style_attr`   -- build a `` style='...'`` attribute fragment;
* :func:`replace_tag` / :func:`replace_style` -- legacy placeholder helpers.

Every function is a side-effect-free pure function, so they are safe to
call from concurrent render threads.

Typical usage inside a renderer::

    end = end_of(kwargs)                       # "\\n" by default
    return f"<strong{style_attr(style)}>{escape_text(content)}</strong>{end}"
"""

import html as _html

#: Trailing string used when an element does not specify ``end``.
DEFAULT_END = "\n"


def end_of(kwargs):
    """Return the trailing string requested by the element data.

    Each element accepts an optional ``end`` argument that controls what is
    appended after its output. When it is missing, :data:`DEFAULT_END` (a
    newline) is used.

    Parameters
    ----------
    kwargs : dict
        The element's data dict, typically the ``**kwargs`` received by an
        element renderer.

    Returns
    -------
    str
        ``kwargs["end"]``, or ``"\\n"`` when it is not provided.

    Examples
    --------
    >>> end_of({})
    '\\n'
    >>> end_of({"end": ""})
    ''
    >>> end_of({"end": "<br>"})
    '<br>'
    """
    return kwargs.get("end", DEFAULT_END)


def escape_text(value, escape=True):
    """Escape text content that will be placed between HTML tags.

    Converts ``<``, ``>`` and ``&`` into HTML entities so that element
    content cannot be interpreted as markup by the browser (this prevents
    e.g. ``<script>`` injection). Quotes are intentionally **not** escaped
    because this helper is only used for text nodes, not attributes --
    use :func:`escape_attr` for attribute values.

    Parameters
    ----------
    value :
        Any value; it is converted with ``str()`` first. ``None`` becomes
        an empty string.
    escape : bool
        When ``False`` the value is returned verbatim. Use this when the
        content is already trusted HTML, e.g.
        ``{"bold": {"content": "<b>ok</b>", "escape": False}}``.

    Returns
    -------
    str
        The escaped text, or the original text when ``escape=False``.

    Examples
    --------
    >>> escape_text("<b>hi</b>")
    '&lt;b&gt;hi&lt;/b&gt;'
    >>> escape_text("<b>hi</b>", escape=False)
    '<b>hi</b>'
    >>> escape_text(None)
    ''
    """
    text = "" if value is None else str(value)
    return _html.escape(text, quote=False) if escape else text


def escape_attr(value):
    """Escape a value that will be placed inside a single-quoted attribute.

    Used for ``href='...'``, ``src='...'`` and ``style='...'`` values. In
    addition to ``< > &``, both single and double quotes are escaped, so a
    malicious value cannot close the attribute and inject new attributes.

    Parameters
    ----------
    value :
        The raw attribute value. ``None`` becomes an empty string.

    Returns
    -------
    str
        Text safe to embed between single quotes in an HTML tag.

    Examples
    --------
    >>> escape_attr("color: red")
    'color: red'
    >>> escape_attr("x' onerror='alert(1)")
    'x&#x27; onerror=&#x27;alert(1)'
    """
    text = "" if value is None else str(value)
    # html.escape(quote=True) escapes double quotes but not single quotes,
    # so single quotes are replaced manually for single-quoted attributes.
    return _html.escape(text, quote=True).replace("'", "&#x27;")


def style_attr(style):
    """Build a `` style='...'`` attribute fragment, or an empty string.

    Parameters
    ----------
    style : str or None
        A CSS declaration string such as ``"color: red"``, or ``None`` when
        the element carries no style.

    Returns
    -------
    str
        A complete attribute fragment **with a leading space**, ready to be
        interpolated into a tag. When ``style`` is ``None`` the empty string
        is returned so the tag keeps no stray space.

    Examples
    --------
    >>> style_attr(None)
    ''
    >>> style_attr("color: red")
    " style='color: red'"
    >>> f"<div{style_attr('color: red')}>hi</div>"
    "<div style='color: red'>hi</div>"
    >>> f"<div{style_attr(None)}>hi</div>"
    '<div>hi</div>'
    """
    if style is None:
        return ""
    return f" style='{escape_attr(style)}'"


def replace_tag(src, dest, tag):
    """Replace a placeholder in a template with concrete text (legacy helper).

    Generic placeholder substitution used by the old renderer templates:
    the marker is replaced by the given text, or removed entirely when
    ``dest`` is ``None``.

    Parameters
    ----------
    src : str
        The template containing the placeholder.
    dest : str or None
        The text to insert. ``None`` means delete the placeholder.
    tag : str
        The placeholder to replace, e.g. ``"$th"``.

    Returns
    -------
    str
        The template after substitution.

    Examples
    --------
    >>> replace_tag("<tr>$th</tr>", "<th>A</th>", "$th")
    '<tr><th>A</th></tr>'
    >>> replace_tag("<tr>$th</tr>", None, "$th")
    '<tr></tr>'
    """
    if dest is not None:
        return src.replace(tag, dest)
    return src.replace(tag, "")


def replace_style(src, dest, tag="$style"):
    """Replace the legacy ``$style`` placeholder with a style attribute.

    Old element templates wrote a ``$style`` marker inside the tag, e.g.
    ``"<div$style>"``. This function turns it into a real HTML attribute
    based on the element's ``style`` field:

    * when ``dest`` is given, the marker becomes `` style='<dest>'`` (note
      the leading space);
    * when ``dest`` is ``None``, the marker is removed, leaving a clean tag.

    New code should prefer :func:`style_attr` with f-strings instead of
    placeholders.

    Parameters
    ----------
    src : str
        An HTML template containing the ``$style`` marker.
    dest : str or None
        A CSS declaration string, or ``None`` for no style attribute.
    tag : str
        The placeholder text, defaulting to ``"$style"``.

    Returns
    -------
    str
        The HTML string after substitution.

    Examples
    --------
    >>> replace_style("<div$style>hello</div>", "color: red")
    "<div style='color: red'>hello</div>"
    >>> replace_style("<div$style>hello</div>", None)
    '<div>hello</div>'
    """
    if dest is not None:
        return replace_tag(src, f" style='{dest}'", tag)
    return replace_tag(src, dest, tag)
