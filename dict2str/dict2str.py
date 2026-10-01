"""Public entry point of dict2str."""

from .constants import T
from .elements import REGISTRY, call_element, supported_elements


class dict2str:
    """Convert a dict (or a list of dicts) describing rich content into
    txt / markdown / html text.

    Parameters
    ----------
    content:
        A single element mapping (``{"h1": {"content": "..."}}``) or a
        list/tuple of such mappings. It is never mutated.
    type:
        ``"txt"``, ``"markdown"`` or ``"html"``. ``None`` keeps the raw
        ``str(content)`` passthrough behaviour.
    escape:
        Applies to HTML output only. When ``True`` (default) element
        content and attribute values are HTML-escaped. Pass ``False`` to
        render trusted HTML verbatim.
    """

    def __init__(self, content, type=None, *, escape=True):
        self.content = content
        self.escape = escape
        self.type = None
        self.func = None
        self.set(type)

    def set(self, type):
        """Switch the output format. Returns self so calls can chain."""
        if type is not None and type not in T:
            raise ValueError(
                f"unsupported output type {type!r}; "
                f"supported types: {', '.join(T)}"
            )
        self.type = type
        self.func = T.get(type)
        return self

    def _nodes(self):
        """Validate and normalize ``content`` without mutating it."""
        if isinstance(self.content, dict):
            nodes = (self.content,)
        elif isinstance(self.content, (list, tuple)):
            nodes = self.content
        else:
            raise TypeError(
                "content must be a dict or a list/tuple of dicts, "
                f"got {type(self.content).__name__}"
            )

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise TypeError(
                    f"node #{index} must be a dict, got {type(node).__name__}"
                )
            for name, data in node.items():
                if name not in REGISTRY:
                    raise ValueError(
                        f"unknown element {name!r} at node #{index}; "
                        f"supported elements: {', '.join(supported_elements())}"
                    )
                if not isinstance(data, dict):
                    raise TypeError(
                        f"element {name!r} at node #{index} must map to a dict, "
                        f"got {type(data).__name__}"
                    )

        return nodes

    def parse(self):
        if self.type is None:
            return str(self.content)

        parts = []
        for node in self._nodes():
            for name, data in node.items():
                payload = {"escape": self.escape}
                payload.update(data)
                parts.append(call_element(name, self.func, payload, 0))
        return "".join(parts)

    def __str__(self):
        return self.parse()

    def __repr__(self):
        return f"dict2str(type={self.type!r})"
