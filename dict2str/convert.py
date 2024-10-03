def replace_tag(src, dest, tag):
    if dest is not None:
        return src.replace(tag, dest)

    return src.replace(tag, "")


def replace_style(src, dest, tag="$style"):
    if dest is not None:
        return replace_tag(src, f" style='{dest}'", tag)

    return replace_tag(src, dest, tag)


class convert:
    @staticmethod
    def toTxt(content, **kwargs):
        end = kwargs.get("end", "\n")
        return f"{content}{end}"

    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "\n")
        return f"{content}{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "\n")
        res = f"<div$style>{content}</div>{end}"
        return replace_style(res, kwargs.get("style"))


level = 0


class orderedList(convert):
    @staticmethod
    def toTxt(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        global level

        for idx, value in enumerate(contents):
            content = value["content"]

            res += f"{'  ' * level}{idx}. {content}{end}"

            level += 1
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    res += globals()[t].toTxt(**v)
            level -= 1

        return res

    @staticmethod
    def toMd(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        global level

        for idx, value in enumerate(contents):
            content = value["content"]

            res += f"{'  ' * level}{idx}. {content}{end}"

            level += 1
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    res += globals()[t].toMd(**v)
            level -= 1

        return res

    @staticmethod
    def toHtml(contents, **kwargs):
        tmp = item = ""

        global level

        level += 1
        for value in contents:
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    tmp = globals()[t].toHtml(**v)

            content = value["content"]
            if tmp != "":
                tmp = f"{'  ' * level}<li$style>{content}\n{tmp}{'  ' * level}</li>\n"
            else:
                tmp = f"{'  ' * level}<li$style>{content}</li>\n"

            item += replace_style(tmp, value.get("style"))
            tmp = ""
        level -= 1

        res = f"{'  ' * level}<ol$style>\n{item}{'  ' * level}</ol>\n"

        return replace_style(res, kwargs.get("style"))


class unOrderedList(convert):
    @staticmethod
    def toTxt(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        global level

        for value in contents:
            content = value["content"]

            res += f"{'  ' * level}· {content}{end}"

            level += 1
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    res += globals()[t].toTxt(**v)
            level -= 1

        return res

    @staticmethod
    def toMd(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        global level

        for value in contents:
            content = value["content"]

            res += f"{'  ' * level}- {content}{end}"

            level += 1
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    res += globals()[t].toMd(**v)
            level -= 1

        return res

    @staticmethod
    def toHtml(contents, **kwargs):
        tmp = item = ""

        global level

        level += 1
        for value in contents:
            items = value.get("items")
            if items is not None:
                for t, v in items.items():
                    tmp = globals()[t].toHtml(**v)

            content = value["content"]
            if tmp != "":
                tmp = f"{'  ' * level}<li$style>{content}\n{tmp}{'  ' * level}</li>\n"
            else:
                tmp = f"{'  ' * level}<li$style>{content}</li>\n"

            item += replace_style(tmp, value.get("style"))
            tmp = ""
        level -= 1

        res = f"{'  ' * level}<ul$style>\n{item}{'  ' * level}</ul>\n"

        return replace_style(res, kwargs.get("style"))


class h(convert):
    html = ["h1", "h2", "h3", "h4", "h5", "h6"]
    md = ["#", "##", "###", "####", "#####", "######"]

    @staticmethod
    def toMd(level, content, **kwargs):
        if level < 1 or level > 6:
            print("Invalid level. Level should be between 1 and 6.")
            return convert.toMd(content, **kwargs)

        tag = h.md[level - 1]
        end = kwargs.get("end", "\n")
        return f"{tag} {content}{end}"

    @staticmethod
    def toHtml(level, content, **kwargs):
        if level < 1 or level > 6:
            print("Invalid level. Level should be between 1 and 6.")
            return convert.toHtml(content, **kwargs)

        tag = h.html[level - 1]
        end = kwargs.get("end", "\n")
        res = f"<{tag}$style>{content}</{tag}>{end}"
        return replace_style(res, kwargs.get("style"))


class h1(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(1, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(1, content, **kwargs)


class h2(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(2, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(2, content, **kwargs)


class h3(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(3, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(3, content, **kwargs)


class h4(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(4, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(4, content, **kwargs)


class h5(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(5, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(5, content, **kwargs)


class h6(h):
    @staticmethod
    def toMd(content, **kwargs):
        return h.toMd(6, content, **kwargs)

    @staticmethod
    def toHtml(content, **kwargs):
        return h.toHtml(6, content, **kwargs)


class img(convert):
    @staticmethod
    def toTxt(url, **kwargs):
        end = kwargs.get("end", "\n")
        alt = kwargs.get("alt", "a image")
        return f"{alt}: {url}{end}"

    @staticmethod
    def toMd(url, **kwargs):
        end = kwargs.get("end", "\n")
        alt = kwargs.get("alt", "a image")
        return f"![{alt}]({url}){end}"

    @staticmethod
    def toHtml(url, **kwargs):
        alt = kwargs.get("alt", "a image")
        res = f"<img$style src='{url}' alt='{alt}'/>"
        return replace_style(res, kwargs.get("style"))


class link(convert):
    @staticmethod
    def toTxt(url, **kwargs):
        end = kwargs.get("end", "\n")
        content = kwargs.get("content", "a link")
        return f"{content}: {url}{end}"

    @staticmethod
    def toMd(url, **kwargs):
        end = kwargs.get("end", "\n")
        content = kwargs.get("content", "a link")
        return f"[{content}]({url}){end}"

    @staticmethod
    def toHtml(url, **kwargs):
        end = kwargs.get("end", "\n")
        content = kwargs.get("content", "link")
        res = f"<a$style href='{url}'>{content}</a>{end}"
        return replace_style(res, kwargs.get("style"))


class table(convert):
    @staticmethod
    def toTxt(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        for content in contents:
            for item in content:
                res += f"{item}\t"

            res += end

        return res + end

    @staticmethod
    def toMd(contents, **kwargs):
        end = kwargs.get("end", "\n")

        res = ""
        for i in contents[0]:
            res += f"|{i}"
        res += f"|{end}"

        pos = kwargs.get("position", "center")

        if pos == "center":
            s = ":--:"
        elif pos == "left":
            s = ":--"
        elif pos == "right":
            s = "--:"
        else:
            s = "--"

        for _ in range(len(contents[0])):
            res += f"|{s}"
        res += f"|{end}"

        for content in contents[1:]:
            for i in content:
                res += f"|{i}"
            res += f"|{end}"

        return res

    @staticmethod
    def toHtml(contents, **kwargs):
        default_style = "width: 100%; border-collapse: collapse; margin-bottom: 10px;"
        style = kwargs.get("style", default_style)

        default_th_style = "text-align: center; border: 1px solid #e6e6e6; background-color: #F5F5F5;"  # fmt: off
        thStyle = kwargs.get("th-style", default_th_style)

        default_td_style = "text-align: center; border: 1px solid #e6e6e6;"
        tdStyle = kwargs.get("tdStyle", default_td_style)

        end = kwargs.get("end", "\n")
        res = f"<table style='{style}'>\n$contents\n</table>{end}"

        th = "<tr>\n$th</tr>\n"
        tmp = ""
        for i in contents[0]:
            tmp += f"  <th style='{thStyle}'>{i}</th>\n"
        th = replace_tag(th, tmp, "$th")

        td = "<tr>\n$td</tr>"
        tmp = ""
        for item in contents[1:]:
            for i in item:
                tmp += f"  <td style='{tdStyle}'>{i}</td>\n"
        td = replace_tag(td, tmp, "$td")

        return replace_tag(res, th + td, "$contents")


class txt(convert):
    pass


class bold(convert):
    @staticmethod
    def toTxt(content, end="", **kwargs):
        return convert.toTxt(content, end, **kwargs)

    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "\n")
        return f"**{content}**{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "\n")
        res = f"<strong$style>{content}</strong>{end}"
        return replace_style(res, kwargs.get("style"))


class italic(convert):
    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "")
        return f"*{content}*{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "")
        res = f"<i$style>{content}</i>{end}"
        return replace_style(res, kwargs.get("style"))


class strikethrough(convert):
    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "")
        return f"~~{content}~~{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "")
        res = f"<del$style>{content}</del>{end}"
        return replace_style(res, kwargs.get("style"))


class blockQuote(convert):
    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "\n")
        return f"> {content}{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "\n")
        res = f"<blockquote$style>{content}</blockquote>{end}"
        return replace_style(res, kwargs.get("style"))


class taskList(convert):
    @staticmethod
    def toTxt(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        for item in contents:
            completed = item.get("complete", False)
            content = item.get("content")

            if completed:
                res += f"🟢 {content}{end}"
            else:
                res += f"🔴 {content}{end}"

        return res

    @staticmethod
    def toMd(contents, **kwargs):
        end = kwargs.get("end", "\n")
        res = ""

        for item in contents:
            completed = item.get("complete", False)
            content = item.get("content")

            if completed:
                res += f"- [x] {content}{end}"
            else:
                res += f"- [ ] {content}{end}"

        return res

    @staticmethod
    def toHtml(contents, **_):
        res = ""

        for item in contents:
            completed = item.get("complete", False)
            end = item.get("end", "\n")
            content = item.get("content")
            style = item.get("style")

            i = f"<label>\n  <input$style type='checkbox' disabled='true'$checked>{content}</input>\n</label>{end}"

            i = replace_style(i, style)

            if completed:
                i = i.replace("$checked", f" checked")
            else:
                i = i.replace("$checked", "")

            res += i

        return res


class code(convert):
    @staticmethod
    def toTxt(content, **kwargs):
        return convert.toTxt(content, **kwargs)

    @staticmethod
    def toMd(content, **kwargs):
        end = kwargs.get("end", "")
        return f"`{content}`{end}"

    @staticmethod
    def toHtml(content, **kwargs):
        end = kwargs.get("end", "")
        res = f"<pre$style>{content}</pre>{end}"
        return replace_style(res, kwargs.get("style"))
