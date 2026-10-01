"""Element renderers: dict data in, txt / Markdown / HTML text out.

Architecture
------------
Each renderable element is a small class that implements up to three
static/class methods: ``toTxt``, ``toMd`` and ``toHtml``. A class declares
which dict key(s) it accepts through the :func:`register` decorator, and
dispatch goes through the :data:`REGISTRY` mapping instead of ``globals()``
lookups, so an unknown element name raises a clear error.

An input document is one ``{element_name: arguments}`` mapping, or a list
of them. Rendering one node is a single call::

    call_element("bold", "toMd", {"content": "hi"})   # -> "**hi**\\n"

The renderers are pure functions of their arguments:

* there is **no module-level mutable state** -- the nesting depth of lists
  travels through the reserved :data:`LEVEL_KEY` keyword instead of an
  ``global level``, which makes rendering reentrant and thread-safe;
* unknown element names / malformed data raise ``ValueError`` / ``TypeError``
  with explanatory messages;
* HTML output escapes text content and attribute values by default.

The public user-facing class ``dict2str`` (see ``dict2str.py``) validates
the document and drives :func:`call_element`; this module only contains the
rendering primitives, which can also be used directly.
"""

from . import utils
from .utils import end_of, escape_attr, escape_text, style_attr

#: Mapping of accepted element name (``"h1"``, ``"bold"``, ...) to the
#: renderer class that handles it. Populated by :func:`register`.
REGISTRY = {}

#: Reserved keyword used internally to carry list nesting depth. Renderers
#: read it from ``kwargs``; user data must never contain this key.
LEVEL_KEY = "_level"


def register(*names):
    """Class decorator that registers an element under one or more names.

    Parameters
    ----------
    *names : str
        Dict key(s) that should map to the decorated class. The canonical
        name is typically given first, followed by shorter aliases.

    Returns
    -------
    callable
        A class decorator that records the mappings in :data:`REGISTRY` and
        returns the class unchanged.

    Example
    -------
    ::

        @register("orderedList", "ol")
        class orderedList(_List):
            ...

        # afterwards both {"orderedList": {...}} and {"ol": {...}} work
    """

    def decorator(cls):
        for name in names:
            REGISTRY[name] = cls
        return cls

    return decorator


def supported_elements():
    """Return all accepted element names as a sorted list of strings.

    Examples
    --------
    >>> "h1" in supported_elements()
    True
    >>> "ol" in supported_elements() and "orderedList" in supported_elements()
    True
    """
    return sorted(REGISTRY)


def lookup(name):
    """Return the renderer class registered for ``name``.

    Parameters
    ----------
    name : str
        An element key as it appears in the input document.

    Returns
    -------
    type
        The renderer class registered under ``name``.

    Raises
    ------
    ValueError
        If no element is registered under ``name``; the message lists every
        supported element so typos are easy to spot.

    Examples
    --------
    >>> lookup("h1").__name__
    'h1'
    """
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(
            f"unknown element {name!r}; supported elements: "
            f"{', '.join(supported_elements())}"
        )
    return cls


def call_element(name, method, data, level=0):
    """Render one ``{name: data}`` element node.

    Validates the node, resolves the renderer and invokes the requested
    format method.

    Parameters
    ----------
    name : str
        Element key, e.g. ``"bold"`` (must exist in :data:`REGISTRY`).
    method : str
        Renderer method to call: ``"toTxt"``, ``"toMd"`` or ``"toHtml"``.
    data : dict
        Keyword arguments for the element, e.g. ``{"content": "hi"}``.
    level : int
        Nesting depth of the enclosing list (``0`` at the top level). It is
        passed to the renderer as the reserved :data:`LEVEL_KEY` keyword so
        list indentation/recursion needs no global state.

    Returns
    -------
    str
        The rendered text.

    Raises
    ------
    TypeError
        If ``data`` is not a dict.
    ValueError
        If ``data`` contains the reserved :data:`LEVEL_KEY`, the element is
        unknown, or the element does not implement ``method``.

    Examples
    --------
    >>> call_element("bold", "toMd", {"content": "hi"})
    '**hi**\\n'
    >>> call_element("h1", "toHtml", {"content": "T"})
    '<h1>T</h1>\\n'
    """
    if not isinstance(data, dict):
        raise TypeError(
            f"arguments for element {name!r} must be a dict, "
            f"got {type(data).__name__}"
        )
    if LEVEL_KEY in data:
        raise ValueError(
            f"{LEVEL_KEY!r} is a reserved key and cannot appear in element data"
        )

    cls = lookup(name)
    fn = getattr(cls, method, None)
    if not callable(fn):
        raise ValueError(f"element {name!r} does not support format method {method!r}")

    # level is injected here; renderers only ever see it through kwargs.
    return fn(**data, **{LEVEL_KEY: level})


def render_nested(items, method, level, escape=True):
    """Render the ``items`` payload attached to a list entry.

    A list entry may carry nested elements through ``items``. This helper
    renders each nested element one level deeper (``level + 1``), which is
    how arbitrary list nesting works.

    Parameters
    ----------
    items : dict or None
        Mapping ``{element_name: arguments}``, or ``None`` for a leaf entry.
    method : str
        Format method to render with (``"toTxt"`` / ``"toMd"`` / ``"toHtml"``).
    level : int
        Depth of the *containing* list; nested elements render at
        ``level + 1``.
    escape : bool
        HTML escaping flag forwarded to the nested elements.

    Returns
    -------
    str
        Concatenated output of all nested elements (``""`` for ``None``).

    Raises
    ------
    TypeError
        If ``items`` is neither ``None`` nor a dict.

    Examples
    --------
    >>> render_nested(None, "toMd", 0)
    ''
    >>> render_nested({"bold": {"content": "x"}}, "toMd", 0)
    '**x**\\n'
    """
    if items is None:
        return ""
    if not isinstance(items, dict):
        raise TypeError("a list item's 'items' must be a dict of element definitions")

    parts = []
    for name, data in items.items():
        # Forward the global escape flag, then let the element's own data
        # override it (e.g. per-element {"escape": False}).
        payload = {"escape": escape}
        if isinstance(data, dict):
            payload.update(data)
        parts.append(call_element(name, method, payload, level))
    return "".join(parts)


def _require_entry(value, where="list item"):
    """Validate one list/task entry and return it unchanged.

    Entries must be dicts containing a ``content`` key; everything else
    (``items``, ``style``, ``complete``, ...) is optional and handled by the
    specific renderers.

    Parameters
    ----------
    value :
        The candidate entry from a ``contents`` list.
    where : str
        Human-readable noun used in the error message.

    Returns
    -------
    dict
        The same ``value``, when valid.

    Raises
    ------
    ValueError
        If ``value`` is not a dict or has no ``content`` key.

    Examples
    --------
    >>> _require_entry({"content": "a"})
    {'content': 'a'}
    """
    if not isinstance(value, dict) or "content" not in value:
        raise ValueError(f"every {where} must be a dict containing a 'content' key")
    return value


# ---------------------------------------------------------------------------
# Basic elements
# ---------------------------------------------------------------------------


class convert:
    """Plain paragraph text; also the base class for every other element.

    Rendering rules:

    * txt / markdown: the content is emitted unchanged;
    * html: content is wrapped in ``<div>`` and escaped by default.

    Examples
    --------
    >>> convert.toTxt(content="hello")
    'hello\\n'
    >>> convert.toMd(content="hello")
    'hello\\n'
    >>> convert.toHtml(content="hello")
    '<div>hello</div>\\n'
    """

    @staticmethod
    def toTxt(content, **kwargs):
        """Render plain text: content followed by ``end`` (default newline)."""
        return f"{content}{end_of(kwargs)}"

    @staticmethod
    def toMd(content, **kwargs):
        """Render Markdown: plain text has no Markdown-specific markup."""
        return f"{content}{end_of(kwargs)}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Render HTML: ``<div>`` wrapper plus optional style/escaping."""
        return (
            f"<div{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</div>{end_of(kwargs)}"
        )


@register("txt")
class txt(convert):
    """Plain text element (key ``"txt"``); inherits :class:`convert` verbatim.

    Examples
    --------
    >>> txt.toMd(content="just text")
    'just text\\n'
    >>> txt.toHtml(content="just text")
    '<div>just text</div>\\n'
    """

    pass


@register("bold")
class bold(convert):
    """Strong/bold text (key ``"bold"``).

    * markdown: ``**content**``;
    * html: ``<strong>content</strong>``;
    * txt: plain content.

    Examples
    --------
    >>> bold.toTxt(content="hi")
    'hi\\n'
    >>> bold.toMd(content="hi")
    '**hi**\\n'
    >>> bold.toHtml(content="hi")
    '<strong>hi</strong>\\n'
    >>> bold.toHtml(content="<x>", escape=False)
    '<strong><x></strong>\\n'
    """

    @staticmethod
    def toTxt(content, **kwargs):
        """Plain text -- bold has no txt representation, delegate to base."""
        return convert.toTxt(content, **kwargs)

    @staticmethod
    def toMd(content, **kwargs):
        """Wrap content with ``**`` and append ``end``."""
        return f"**{content}**{end_of(kwargs)}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Wrap content in ``<strong>`` with optional style/escaping."""
        return (
            f"<strong{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</strong>{end_of(kwargs)}"
        )


@register("italic")
class italic(convert):
    """Italic/emphasis text (key ``"italic"``).

    Unlike block elements, emphasis is inline, so the default ``end`` is an
    empty string (no trailing newline) for markdown and html.

    Examples
    --------
    >>> italic.toMd(content="hi")
    '*hi*'
    >>> italic.toHtml(content="hi")
    '<i>hi</i>'
    """

    @staticmethod
    def toMd(content, **kwargs):
        """Wrap content with single ``*``; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return f"*{content}*{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Wrap content in ``<i>``; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return (
            f"<i{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</i>{end}"
        )


@register("strikethrough")
class strikethrough(convert):
    """Struck-through text (key ``"strikethrough"``); inline, empty default end.

    Examples
    --------
    >>> strikethrough.toMd(content="hi")
    '~~hi~~'
    >>> strikethrough.toHtml(content="hi")
    '<del>hi</del>'
    """

    @staticmethod
    def toMd(content, **kwargs):
        """Wrap content with ``~~~~``; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return f"~~{content}~~{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Wrap content in ``<del>``; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return (
            f"<del{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</del>{end}"
        )


@register("blockQuote", "blockquote")
class blockQuote(convert):
    """Block quotation (keys ``"blockQuote"`` and the alias ``"blockquote"``).

    Examples
    --------
    >>> blockQuote.toMd(content="words")
    '> words\\n'
    >>> blockQuote.toHtml(content="words")
    '<blockquote>words</blockquote>\\n'
    """

    @staticmethod
    def toMd(content, **kwargs):
        """Prefix the line with ``> `` and append ``end``."""
        return f"> {content}{end_of(kwargs)}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Wrap content in ``<blockquote>`` with optional style/escaping."""
        return (
            f"<blockquote{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</blockquote>{end_of(kwargs)}"
        )


@register("code")
class code(convert):
    """Inline code (key ``"code"``); inline, empty default end for md/html.

    Examples
    --------
    >>> code.toTxt(content="print(1)")
    'print(1)\\n'
    >>> code.toMd(content="print(1)")
    '`print(1)`'
    >>> code.toHtml(content="print(1)")
    '<pre>print(1)</pre>'
    """

    @staticmethod
    def toTxt(content, **kwargs):
        """Plain text -- code has no txt representation, delegate to base."""
        return convert.toTxt(content, **kwargs)

    @staticmethod
    def toMd(content, **kwargs):
        """Wrap content with backticks; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return f"`{content}`{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        """Wrap content in ``<pre>``; default ``end`` is empty."""
        end = kwargs.get("end", "")
        return (
            f"<pre{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</pre>{end}"
        )


@register("h")
class h(convert):
    """Generic heading whose level is given at call time (key ``"h"``).

    Arguments
    ---------
    level : int
        Heading level, 1 through 6.
    content : str
        Heading text.

    Examples
    --------
    >>> h.toMd(2, content="Title")
    '## Title\\n'
    >>> h.toHtml(3, content="Title")
    '<h3>Title</h3>\\n'
    >>> h.toMd(9, content="Title")
    Traceback (most recent call last):
        ...
    ValueError: invalid heading level 9; expected 1..6
    """

    #: HTML tag for each level (index 0 == h1).
    html = ["h1", "h2", "h3", "h4", "h5", "h6"]
    #: Markdown prefix for each level (index 0 == h1).
    md = ["#", "##", "###", "####", "#####", "######"]

    @staticmethod
    def _check_level(level):
        """Raise ``ValueError`` unless ``level`` is an int from 1 to 6."""
        if not isinstance(level, int) or level < 1 or level > 6:
            raise ValueError(f"invalid heading level {level!r}; expected 1..6")

    @classmethod
    def toMd(cls, level, content, **kwargs):
        """Render ``#`` repeated ``level`` times, a space, then content."""
        cls._check_level(level)
        return f"{cls.md[level - 1]} {content}{end_of(kwargs)}"

    @classmethod
    def toHtml(cls, level, content, **kwargs):
        """Render the matching ``<h1>``..``<h6>`` tag."""
        cls._check_level(level)
        tag = cls.html[level - 1]
        return (
            f"<{tag}{style_attr(kwargs.get('style'))}>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</{tag}>{end_of(kwargs)}"
        )


def _make_heading(level):
    """Build the fixed-level renderer class for ``h1`` ... ``h6``.

    The six classes only differ by their bound ``level``; this factory
    generates them at import time to avoid six near-identical copies. Each
    generated class is registered under ``f"h{level}"``.

    Parameters
    ----------
    level : int
        Heading level from 1 to 6.

    Returns
    -------
    type
        A renderer class behaving like :class:`h` with ``level`` fixed.
    """

    @register(f"h{level}")
    class _Heading(h):
        """Fixed-level heading generated by :func:`_make_heading`.

        ``toTxt`` outputs plain text (headings have no txt representation),
        while ``toMd`` / ``toHtml`` delegate to :class:`h` with the class's
        bound level.
        """

        @staticmethod
        def toTxt(content, **kwargs):
            """Plain text with the usual trailing ``end``."""
            return convert.toTxt(content, **kwargs)

        @staticmethod
        def toMd(content, **kwargs):
            """Render at the heading's fixed level."""
            return h.toMd(level, content, **kwargs)

        @staticmethod
        def toHtml(content, **kwargs):
            """Render at the heading's fixed level."""
            return h.toHtml(level, content, **kwargs)

    # Give the generated class a human-friendly name for reprs/tracebacks.
    _Heading.__name__ = f"h{level}"
    _Heading.__qualname__ = f"h{level}"
    return _Heading


#: Fixed-level heading renderers, generated once at import time.
h1 = _make_heading(1)
h2 = _make_heading(2)
h3 = _make_heading(3)
h4 = _make_heading(4)
h5 = _make_heading(5)
h6 = _make_heading(6)


@register("img")
class img(convert):
    """Image element (key ``"img"``).

    Arguments
    ---------
    url : str
        Image URL (required).
    alt : str
        Alternative text; defaults to ``"a image"``.

    Note the html output is a void tag (``<img .../>``) and has no trailing
    newline, while txt/markdown do append the usual ``end``.

    Examples
    --------
    >>> img.toTxt(url="u", alt="a")
    'a: u\\n'
    >>> img.toMd(url="u", alt="a")
    '![a](u)\\n'
    >>> img.toHtml(url="u", alt="a")
    "<img src='u' alt='a'/>"
    >>> img.toHtml(url="u")
    "<img src='u' alt='a image'/>"
    """

    @staticmethod
    def toTxt(url, **kwargs):
        """Render ``alt: url`` text."""
        alt = kwargs.get("alt", "a image")
        return f"{alt}: {url}{end_of(kwargs)}"

    @staticmethod
    def toMd(url, **kwargs):
        """Render the ``![alt](url)`` image syntax."""
        alt = kwargs.get("alt", "a image")
        return f"![{alt}]({url}){end_of(kwargs)}"

    @staticmethod
    def toHtml(url, **kwargs):
        """Render a void ``<img/>`` tag; url/alt are attribute-escaped."""
        alt = kwargs.get("alt", "a image")
        return (
            f"<img{style_attr(kwargs.get('style'))} "
            f"src='{escape_attr(url)}' alt='{escape_attr(alt)}'/>"
        )


@register("link")
class link(convert):
    """Hyperlink element (key ``"link"``).

    Arguments
    ---------
    url : str
        Target URL (required).
    content : str
        Link text; defaults to ``"a link"``.

    Examples
    --------
    >>> link.toTxt(url="u", content="go")
    'go: u\\n'
    >>> link.toMd(url="u", content="go")
    '[go](u)\\n'
    >>> link.toHtml(url="u", content="go")
    "<a href='u'>go</a>\\n"
    """

    @staticmethod
    def toTxt(url, **kwargs):
        """Render ``content: url`` text."""
        content = kwargs.get("content", "a link")
        return f"{content}: {url}{end_of(kwargs)}"

    @staticmethod
    def toMd(url, **kwargs):
        """Render the ``[content](url)`` link syntax."""
        content = kwargs.get("content", "a link")
        return f"[{content}]({url}){end_of(kwargs)}"

    @staticmethod
    def toHtml(url, **kwargs):
        """Render an ``<a>`` tag; url is attribute-escaped, text escaped."""
        content = kwargs.get("content", "a link")
        return (
            f"<a{style_attr(kwargs.get('style'))} href='{escape_attr(url)}'>"
            f"{escape_text(content, kwargs.get('escape', True))}"
            f"</a>{end_of(kwargs)}"
        )


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------


class _List(convert):
    """Shared rendering logic for ordered and unordered lists.

    Subclasses only set :attr:`tag` and the per-index markers
    (:meth:`_txt_marker` / :meth:`_md_marker`). Indentation is driven by the
    reserved :data:`LEVEL_KEY` depth received in ``kwargs``; each nested
    list renders at ``level + 1``.

    Entry shape: ``{"content": str, "items": {...}, "style": str}`` where
    ``items`` and ``style`` are optional.

    Markdown example (depth carried by ``_level``)::

        1. A
          - B
    """

    #: HTML container tag; overridden to ``"ol"`` by the ordered subclass.
    tag = "ul"

    @classmethod
    def _txt_marker(cls, index):
        """Return the txt bullet for zero-based ``index`` (default ``"·"``)."""
        return "·"

    @classmethod
    def _md_marker(cls, index):
        """Return the markdown bullet for zero-based ``index`` (default ``"-"``)."""
        return "-"

    @classmethod
    def toTxt(cls, contents, **kwargs):
        """Render a txt list, indenting each line by two spaces per level."""
        level = kwargs.get(LEVEL_KEY, 0)
        escape = kwargs.get("escape", True)
        end = end_of(kwargs)
        pad = "  " * level  # two spaces of indentation per nesting level

        parts = []
        for index, value in enumerate(contents):
            value = _require_entry(value)
            parts.append(f"{pad}{cls._txt_marker(index)} {value['content']}{end}")
            # Nested items are rendered one level deeper and appended inline
            # after their parent line.
            parts.append(
                render_nested(value.get("items"), "toTxt", level + 1, escape)
            )
        return "".join(parts)

    @classmethod
    def toMd(cls, contents, **kwargs):
        """Render a markdown list, indenting each line by two spaces per level."""
        level = kwargs.get(LEVEL_KEY, 0)
        escape = kwargs.get("escape", True)
        end = end_of(kwargs)
        pad = "  " * level

        parts = []
        for index, value in enumerate(contents):
            value = _require_entry(value)
            parts.append(f"{pad}{cls._md_marker(index)} {value['content']}{end}")
            parts.append(
                render_nested(value.get("items"), "toMd", level + 1, escape)
            )
        return "".join(parts)

    @classmethod
    def toHtml(cls, contents, **kwargs):
        """Render an indented ``<ol>``/``<ul>`` tree.

        ``outer`` is the indentation of the container tag itself; items and
        nested lists are indented one step further (``inner``). An entry with
        nested elements keeps the child list inside its ``<li>`` element.
        """
        level = kwargs.get(LEVEL_KEY, 0)
        escape = kwargs.get("escape", True)
        outer = "  " * level
        inner = "  " * (level + 1)

        items_html = []
        for value in contents:
            value = _require_entry(value)
            nested = render_nested(value.get("items"), "toHtml", level + 1, escape)
            content = escape_text(value["content"], escape)

            if nested:
                # Put the nested list between the opening <li> and its close.
                item_html = (
                    f"{inner}<li{style_attr(value.get('style'))}>{content}\n"
                    f"{nested}{inner}</li>\n"
                )
            else:
                item_html = (
                    f"{inner}<li{style_attr(value.get('style'))}>{content}</li>\n"
                )
            items_html.append(item_html)

        return (
            f"{outer}<{cls.tag}{style_attr(kwargs.get('style'))}>\n"
            f"{''.join(items_html)}"
            f"{outer}</{cls.tag}>\n"
        )


@register("orderedList", "ol")
class orderedList(_List):
    """Numbered list (keys ``"orderedList"`` and alias ``"ol"``).

    Examples
    --------
    >>> orderedList.toTxt(contents=[{"content": "A"}, {"content": "B"}])
    '1. A\\n2. B\\n'
    >>> orderedList.toMd(contents=[{"content": "A"}, {"content": "B"}])
    '1. A\\n2. B\\n'
    >>> orderedList.toHtml(contents=[{"content": "A"}]).splitlines()[0]
    '<ol>'
    """

    tag = "ol"

    @classmethod
    def _txt_marker(cls, index):
        """One-based decimal marker, e.g. ``"1."`` for the first entry."""
        return f"{index + 1}."

    @classmethod
    def _md_marker(cls, index):
        """One-based decimal marker, e.g. ``"1."`` for the first entry."""
        return f"{index + 1}."


@register("unOrderedList", "ul")
class unOrderedList(_List):
    """Bulleted list (keys ``"unOrderedList"`` and alias ``"ul"``).

    Examples
    --------
    >>> unOrderedList.toTxt(contents=[{"content": "A"}])
    '· A\\n'
    >>> unOrderedList.toMd(contents=[{"content": "A"}])
    '- A\\n'
    >>> unOrderedList.toHtml(contents=[{"content": "A"}]).splitlines()[0]
    '<ul>'
    """

    tag = "ul"


# ---------------------------------------------------------------------------
# Task list
# ---------------------------------------------------------------------------


@register("taskList", "tasklist")
class taskList(convert):
    """Checkable task list (keys ``"taskList"`` and alias ``"tasklist"``).

    Each entry is ``{"content": str, "complete": bool}``; ``complete``
    defaults to ``False``.

    Examples
    --------
    >>> taskList.toMd(contents=[{"content": "a"},
    ...                         {"content": "b", "complete": True}])
    '- [ ] a\\n- [x] b\\n'
    >>> taskList.toHtml(contents=[{"content": "a"}])
    "<label>\\n  <input type='checkbox' disabled/>a\\n</label>\\n"
    >>> taskList.toHtml(contents=[{"content": "b", "complete": True}])
    "<label>\\n  <input type='checkbox' disabled checked/>b\\n</label>\\n"
    """

    @staticmethod
    def toTxt(contents, **kwargs):
        """Prefix unfinished tasks with a red circle and done ones with green."""
        end = end_of(kwargs)
        parts = []
        for item in contents:
            _require_entry(item, "task item")
            if item.get("complete", False):
                parts.append(f"🟢 {item['content']}{end}")
            else:
                parts.append(f"🔴 {item['content']}{end}")
        return "".join(parts)

    @staticmethod
    def toMd(contents, **kwargs):
        """Render GitHub-style ``- [ ]`` / ``- [x]`` checkboxes."""
        end = end_of(kwargs)
        parts = []
        for item in contents:
            _require_entry(item, "task item")
            if item.get("complete", False):
                parts.append(f"- [x] {item['content']}{end}")
            else:
                parts.append(f"- [ ] {item['content']}{end}")
        return "".join(parts)

    @staticmethod
    def toHtml(contents, **_):
        """Render a disabled checkbox per entry.

        Per-entry options are read from the item itself (``end``, ``style``,
        ``escape``); the list-level ``kwargs`` is intentionally unused.
        ``disabled`` makes the checkbox read-only and ``checked`` marks done
        tasks. It is a void input, hence the self-closing ``/>``.
        """
        parts = []
        for item in contents:
            _require_entry(item, "task item")
            end = item.get("end", "\n")
            checked = " checked" if item.get("complete", False) else ""
            content = escape_text(item["content"], item.get("escape", True))
            box = (
                f"<label>\n  <input{style_attr(item.get('style'))} "
                f"type='checkbox' disabled{checked}/>{content}\n</label>{end}"
            )
            parts.append(box)
        return "".join(parts)


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------


def _normalized_rows(contents):
    """Validate table data and pad short rows to a common width.

    Parameters
    ----------
    contents : list or tuple
        Non-empty sequence of rows; the first row is treated as the header.
        Rows may have different lengths.

    Returns
    -------
    (list, int)
        A list of list-rows padded with ``""`` to the widest row's length,
        and that common width.

    Raises
    ------
    ValueError
        If ``contents`` is not a non-empty list/tuple.

    Examples
    --------
    >>> rows, width = _normalized_rows([("a", "b"), ("c",)])
    >>> rows
    [['a', 'b'], ['c', '']]
    >>> width
    2
    """
    if not isinstance(contents, (list, tuple)) or len(contents) == 0:
        raise ValueError("table 'contents' must be a non-empty list of rows")
    width = max(len(row) for row in contents)
    # Pad every shorter row with empty strings so columns line up.
    rows = [list(row) + [""] * (width - len(row)) for row in contents]
    return rows, width


@register("table")
class table(convert):
    """Table whose first row is the header (key ``"table"``).

    Arguments
    ---------
    contents : list/tuple
        Non-empty 2D data; rows may be lists or tuples and may have unequal
        lengths (short rows are padded with empty cells).
    position : str
        Markdown column alignment: ``"center"`` (default), ``"left"``,
        ``"right"``; any other value falls back to unaligned ``--``.
    style, th_style, td_style : str
        HTML-only CSS for the ``<table>``, header cells and body cells.
        Legacy spellings ``"th-style"`` / ``"tdStyle"`` are also accepted.

    Examples
    --------
    >>> table.toTxt(contents=[("a", "b"), ("1", "2")])
    'a\\tb\\n1\\t2\\n'
    >>> print(table.toMd(contents=[("a", "b"), ("1", "2")]), end="")
    |a|b|
    |:--:|:--:|
    |1|2|
    >>> table.toHtml(contents=[("a", "b"), ("1", "2")]).count("<tr>")
    2
    """

    @staticmethod
    def toTxt(contents, **kwargs):
        """Join cells with tabs and rows with ``end`` (default newline)."""
        rows, _ = _normalized_rows(contents)
        end = end_of(kwargs)
        parts = []
        for row in rows:
            parts.append("\t".join(str(cell) for cell in row) + end)
        return "".join(parts)

    @staticmethod
    def toMd(contents, **kwargs):
        """Render a GitHub-flavoured markdown table.

        Emits the header row, an alignment separator row (one segment per
        column), then the body rows. Cell text is cleaned by ``clean`` to
        avoid breaking the table syntax.
        """
        rows, width = _normalized_rows(contents)
        end = end_of(kwargs)

        def clean(cell):
            """Escape cell pipes, flatten newlines and trim whitespace."""
            return str(cell).replace("|", "\\|").replace("\n", " ").strip()

        # Map the position option to a markdown alignment separator.
        position = kwargs.get("position", "center")
        if position == "center":
            sep = ":--:"
        elif position == "left":
            sep = ":--"
        elif position == "right":
            sep = "--:"
        else:
            sep = "--"  # unknown value: unaligned column

        # First line = header, second line = alignment separators.
        lines = [
            "".join(f"|{clean(cell)}" for cell in rows[0]) + "|" + end,
            "".join(f"|{sep}" for _ in range(width)) + "|" + end,
        ]
        for row in rows[1:]:
            lines.append("".join(f"|{clean(cell)}" for cell in row) + "|" + end)
        return "".join(lines)

    @staticmethod
    def toHtml(contents, **kwargs):
        """Render a styled ``<table>`` with one ``<tr>`` per data row.

        Header cells use ``<th>``, body cells ``<td>``. Every input row --
        including extra body rows -- becomes its own ``<tr>`` (a previous
        implementation merged all body cells into one row).
        """
        rows, _ = _normalized_rows(contents)
        escape = kwargs.get("escape", True)

        # Default styles; callers may override any of the three.
        default_style = "width: 100%; border-collapse: collapse; margin-bottom: 10px;"
        style = kwargs.get("style", default_style)

        default_th_style = (
            "text-align: center; border: 1px solid #e6e6e6; "
            "background-color: #F5F5F5;"
        )
        # Accept the canonical th_style plus the legacy th-style spelling.
        th_style = kwargs.get("th_style", kwargs.get("th-style", default_th_style))

        default_td_style = "text-align: center; border: 1px solid #e6e6e6;"
        # Accept the canonical td_style plus the legacy tdStyle spelling.
        td_style = kwargs.get("td_style", kwargs.get("tdStyle", default_td_style))

        def render_row(cells, cell_tag, cell_style):
            """Render one row of cells (<tr> with <th> or <td> children)."""
            body = "".join(
                f"    <{cell_tag} style='{cell_style}'>"
                f"{escape_text(cell, escape)}</{cell_tag}>\n"
                for cell in cells
            )
            return f"  <tr>\n{body}  </tr>\n"

        head = render_row(rows[0], "th", th_style)  # first row is the header
        body = "".join(render_row(row, "td", td_style) for row in rows[1:])
        end = end_of(kwargs)

        return (
            f"<table{style_attr(style)}>\n{head}{body}</table>{end}"
        )
