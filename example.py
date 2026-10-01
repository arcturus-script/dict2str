"""dict2str 功能演示 + 零参数测试脚本。

直接运行（无需任何参数）::

    python example.py

脚本按功能分区执行，每个分区：
1. 打印元素在 txt / markdown / html 三种格式下的实际输出；
2. 用断言核对输出是否与预期一致；
3. 异常分支单独验证。

全部用例通过时进程退出码为 0，任一用例失败退出码为 1。
要求 Python >= 3.9。
"""

import sys

from dict2str import dict2str

# 已通过用例计数
_passed = 0


def check(name, got, want):
    """断言渲染结果等于预期，并累计通过数。"""
    global _passed
    assert got == want, (
        f"\n[用例失败] {name}\n  期望: {want!r}\n  实际: {got!r}"
    )
    _passed += 1


def check_raises(name, exc, fn):
    """断言 fn() 抛出指定类型的异常。"""
    global _passed
    try:
        fn()
    except exc:
        _passed += 1
    except Exception as e:  # 抛出了其他类型的异常也算失败
        raise AssertionError(
            f"[用例失败] {name}: 期望抛出 {exc.__name__}，"
            f"实际抛出 {type(e).__name__}: {e}"
        )
    else:
        raise AssertionError(
            f"[用例失败] {name}: 期望抛出 {exc.__name__}，但未抛出任何异常"
        )


def banner(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def render(data, type_name):
    """渲染并打印结果，返回输出字符串供断言使用。"""
    out = str(dict2str(data, type=type_name))
    print(f"[{type_name}]\n{out}", end="")
    if not out.endswith("\n"):
        print()  # 元素自身不带换行时补一个空行，方便阅读
    return out


# ---------------------------------------------------------------------------
# 1. 基础行内元素：txt / bold / italic / strikethrough / code / blockQuote
# ---------------------------------------------------------------------------


def test_inline_elements():
    banner("1. 基础行内元素（txt / bold / italic / strikethrough / code / blockQuote）")

    cases = [
        # (元素名, 数据, txt 预期, markdown 预期, html 预期)
        ("txt", {"content": "plain text"},
         "plain text\n", "plain text\n", "<div>plain text</div>\n"),
        ("bold", {"content": "strong"},
         "strong\n", "**strong**\n", "<strong>strong</strong>\n"),
        ("italic", {"content": "slanted"},
         "slanted\n", "*slanted*", "<i>slanted</i>"),
        ("strikethrough", {"content": "deleted"},
         "deleted\n", "~~deleted~~", "<del>deleted</del>"),
        ("code", {"content": "print('hi')"},
         "print('hi')\n", "`print('hi')`", "<pre>print('hi')</pre>"),
        ("blockQuote", {"content": "quoted"},
         "quoted\n", "> quoted\n", "<blockquote>quoted</blockquote>\n"),
    ]

    for name, data, want_txt, want_md, want_html in cases:
        node = [{name: data}]
        print(f"\n>>> {name}")
        check(f"{name}.txt", render(node, "txt"), want_txt)
        check(f"{name}.md", render(node, "markdown"), want_md)
        check(f"{name}.html", render(node, "html"), want_html)

    # 同一个节点里可以并排放多个元素，按字典顺序输出
    node = [{"italic": {"content": "I"}, "bold": {"content": "B"}}]
    check("同一节点多元素.txt", str(dict2str(node, type="txt")), "I\nB\n")
    check("同一节点多元素.md", str(dict2str(node, type="markdown")), "*I***B**\n")
    check("同一节点多元素.html",
          str(dict2str(node, type="html")),
          "<i>I</i><strong>B</strong>\n")


# ---------------------------------------------------------------------------
# 2. 标题：h1~h6 以及通用 h + level
# ---------------------------------------------------------------------------


def test_headings():
    banner("2. 标题（h1~h6 / h + level）")

    for level in range(1, 7):
        name = f"h{level}"
        node = [{name: {"content": f"title {level}"}}]
        print(f"\n>>> {name}")
        check(f"{name}.txt", render(node, "txt"), f"title {level}\n")
        check(f"{name}.md", render(node, "markdown"),
              f"{'#' * level} title {level}\n")
        check(f"{name}.html", render(node, "html"),
              f"<h{level}>title {level}</h{level}>\n")

    # 通用 h 元素：用 level 参数指定层级
    print("\n>>> h(level=3)")
    node = [{"h": {"level": 3, "content": "via h"}}]
    check("h.level.md", render(node, "markdown"), "### via h\n")
    check("h.level.html", render(node, "html"), "<h3>via h</h3>\n")

    # level 越界必须报错（旧版本只 print，现在抛 ValueError）
    check_raises("h.level=0", ValueError,
                 lambda: str(dict2str([{"h": {"level": 0, "content": "x"}}],
                                      type="html")))
    check_raises("h.level=7", ValueError,
                 lambda: str(dict2str([{"h": {"level": 7, "content": "x"}}],
                                      type="html")))


# ---------------------------------------------------------------------------
# 3. 链接与图片
# ---------------------------------------------------------------------------


def test_link_and_image():
    banner("3. 链接 link 与图片 img")

    print("\n>>> link（提供 content）")
    node = [{"link": {"url": "https://example.com", "content": "示例网站"}}]
    check("link.txt", render(node, "txt"), "示例网站: https://example.com\n")
    check("link.md", render(node, "markdown"), "[示例网站](https://example.com)\n")
    check("link.html", render(node, "html"),
          "<a href='https://example.com'>示例网站</a>\n")

    print("\n>>> link（省略 content，使用默认文案 'a link'）")
    node = [{"link": {"url": "https://example.com"}}]
    check("link 默认文案.txt", str(dict2str(node, type="txt")),
          "a link: https://example.com\n")
    check("link 默认文案.md", str(dict2str(node, type="markdown")),
          "[a link](https://example.com)\n")
    check("link 默认文案.html", str(dict2str(node, type="html")),
          "<a href='https://example.com'>a link</a>\n")

    print("\n>>> img（提供 alt）")
    node = [{"img": {"url": "https://example.com/a.png", "alt": "示意图"}}]
    check("img.txt", render(node, "txt"), "示意图: https://example.com/a.png\n")
    check("img.md", render(node, "markdown"),
          "![示意图](https://example.com/a.png)\n")
    check("img.html", render(node, "html"),
          "<img src='https://example.com/a.png' alt='示意图'/>")

    print("\n>>> img（省略 alt，使用默认文案 'a image'，html 不带结尾换行）")
    node = [{"img": {"url": "https://example.com/a.png"}}]
    check("img 默认alt.txt", str(dict2str(node, type="txt")),
          "a image: https://example.com/a.png\n")
    check("img 默认alt.md", str(dict2str(node, type="markdown")),
          "![a image](https://example.com/a.png)\n")
    check("img 默认alt.html", str(dict2str(node, type="html")),
          "<img src='https://example.com/a.png' alt='a image'/>")


# ---------------------------------------------------------------------------
# 4. 任务列表 taskList（含别名 tasklist）
# ---------------------------------------------------------------------------


def test_task_list():
    banner("4. 任务列表 taskList")

    data = {"contents": [
        {"content": "未完成任务"},
        {"content": "已完成任务", "complete": True},
    ]}
    node = [{"taskList": data}]

    check("taskList.txt", render(node, "txt"),
          "🔴 未完成任务\n🟢 已完成任务\n")
    check("taskList.md", render(node, "markdown"),
          "- [ ] 未完成任务\n- [x] 已完成任务\n")
    check("taskList.html", render(node, "html"),
          "<label>\n"
          "  <input type='checkbox' disabled/>未完成任务\n"
          "</label>\n"
          "<label>\n"
          "  <input type='checkbox' disabled checked/>已完成任务\n"
          "</label>\n")

    # 别名 tasklist 输出必须完全一致
    alias = [{"tasklist": data}]
    check("tasklist 别名.txt",
          str(dict2str(alias, type="txt")), str(dict2str(node, type="txt")))
    check("tasklist 别名.html",
          str(dict2str(alias, type="html")), str(dict2str(node, type="html")))


# ---------------------------------------------------------------------------
# 5. 表格 table：三种格式 + 四种对齐 + 不规则行列 + 多行数据
# ---------------------------------------------------------------------------


def test_table():
    banner("5. 表格 table")

    rows = [("姓名", "分数"), ("张三", "95"), ("李四", "88")]

    print("\n>>> table txt（制表符分隔，每行一条 <tr> 等价物）")
    check("table.txt", render([{"table": {"contents": rows}}], "txt"),
          "姓名\t分数\n张三\t95\n李四\t88\n")

    print("\n>>> table markdown（默认居中对齐）")
    check("table.md center", render([{"table": {"contents": rows}}], "markdown"),
          "|姓名|分数|\n|:--:|:--:|\n|张三|95|\n|李四|88|\n")

    print("\n>>> table markdown（左对齐 / 右对齐 / 非法值回退无冒号）")
    check("table.md left",
          str(dict2str([{"table": {"contents": rows, "position": "left"}}],
                       type="markdown")),
          "|姓名|分数|\n|:--|:--|\n|张三|95|\n|李四|88|\n")
    check("table.md right",
          str(dict2str([{"table": {"contents": rows, "position": "right"}}],
                       type="markdown")),
          "|姓名|分数|\n|--:|--:|\n|张三|95|\n|李四|88|\n")
    check("table.md 非法position回退",
          str(dict2str([{"table": {"contents": rows, "position": "weird"}}],
                       type="markdown")),
          "|姓名|分数|\n|--|--|\n|张三|95|\n|李四|88|\n")

    print("\n>>> table html（每个数据行必须是独立的 <tr>）")
    html_out = render([{"table": {"contents": rows}}], "html")
    check("table.html 行数", html_out.count("<tr>"), 3)
    check("table.html 表头", html_out.count("<th"), 2)
    check("table.html 数据格", html_out.count("<td"), 4)
    check("table.html 包含姓名", "姓名" in html_out, True)

    print("\n>>> table html 自定义样式（th_style / td_style / style）")
    html_custom = str(dict2str([{"table": {"contents": rows,
                                           "style": "border: 1px solid #000;",
                                           "th_style": "color: red;",
                                           "td_style": "color: blue;"}}],
                               type="html"))
    check("table.html 自定义table样式",
          "border: 1px solid #000;" in html_custom, True)
    check("table.html 自定义th样式", "color: red;" in html_custom, True)
    check("table.html 自定义td样式", "color: blue;" in html_custom, True)
    # 旧参数名 th-style / tdStyle 仍然兼容
    html_legacy = str(dict2str([{"table": {"contents": rows,
                                           "th-style": "color: red;",
                                           "tdStyle": "color: blue;"}}],
                               type="html"))
    check("table.html 旧样式参数兼容",
          "color: red;" in html_legacy and "color: blue;" in html_legacy, True)

    print("\n>>> table 不规则行列（短行自动补空单元格）")
    ragged = [("a", "b"), ("只有一列",)]
    check("table.md 短行补齐",
          str(dict2str([{"table": {"contents": ragged}}], type="markdown")),
          "|a|b|\n|:--:|:--:|\n|只有一列||\n")
    check("table.html 短行补齐仍为2行",
          str(dict2str([{"table": {"contents": ragged}}], type="html")
              ).count("<tr>"), 2)

    print("\n>>> table markdown 单元格中的管道符会被转义")
    pipe = [("key", "value"), ("a|b", "x")]
    check("table.md 管道符转义",
          str(dict2str([{"table": {"contents": pipe}}], type="markdown")),
          "|key|value|\n|:--:|:--:|\n|a\\|b|x|\n")

    # 空表格 / 非法 contents
    check_raises("table 空contents", ValueError,
                 lambda: str(dict2str([{"table": {"contents": []}}],
                                      type="markdown")))
    check_raises("table contents不是列表", ValueError,
                 lambda: str(dict2str([{"table": {"contents": "x"}}],
                                      type="markdown")))


# ---------------------------------------------------------------------------
# 6. 有序/无序列表，含多层嵌套、列表项样式
# ---------------------------------------------------------------------------


def test_lists():
    banner("6. 有序列表 orderedList 与无序列表 unOrderedList（含嵌套）")

    plain = {"contents": [{"content": "第一项"}, {"content": "第二项"}]}

    print("\n>>> unOrderedList")
    ul = [{"unOrderedList": plain}]
    check("ul.txt", render(ul, "txt"), "· 第一项\n· 第二项\n")
    check("ul.md", render(ul, "markdown"), "- 第一项\n- 第二项\n")
    check("ul.html", render(ul, "html"),
          "<ul>\n  <li>第一项</li>\n  <li>第二项</li>\n</ul>\n")

    print("\n>>> orderedList")
    ol = [{"orderedList": plain}]
    check("ol.txt", render(ol, "txt"), "1. 第一项\n2. 第二项\n")
    check("ol.md", render(ol, "markdown"), "1. 第一项\n2. 第二项\n")
    check("ol.html", render(ol, "html"),
          "<ol>\n  <li>第一项</li>\n  <li>第二项</li>\n</ol>\n")

    print("\n>>> 多层嵌套（ol > ul > ol）")
    nested = [{"orderedList": {"contents": [
        {"content": "A", "items": {"unOrderedList": {"contents": [
            {"content": "B"},
            {"content": "C", "items": {"orderedList": {"contents": [
                {"content": "D"}, {"content": "E"},
            ]}}},
        ]}}},
        {"content": "F"},
    ]}}]
    check("嵌套.md", render(nested, "markdown"),
          "1. A\n"
          "  - B\n"
          "  - C\n"
          "    1. D\n"
          "    2. E\n"
          "2. F\n")
    check("嵌套.txt", render(nested, "txt"),
          "1. A\n"
          "  · B\n"
          "  · C\n"
          "    1. D\n"
          "    2. E\n"
          "2. F\n")
    check("嵌套.html", render(nested, "html"),
          "<ol>\n"
          "  <li>A\n"
          "  <ul>\n"
          "    <li>B</li>\n"
          "    <li>C\n"
          "    <ol>\n"
          "      <li>D</li>\n"
          "      <li>E</li>\n"
          "    </ol>\n"
          "    </li>\n"
          "  </ul>\n"
          "  </li>\n"
          "  <li>F</li>\n"
          "</ol>\n")

    print("\n>>> 列表容器与列表项的 style（仅 html）")
    styled = [{"orderedList": {"style": "color: red;", "contents": [
        {"content": "带样式的项", "style": "font-weight: bold;"},
        {"content": "普通项"},
    ]}}]
    styled_html = str(dict2str(styled, type="html"))
    check("ol 容器style", "<ol style='color: red;'>" in styled_html, True)
    check("li 项style", "<li style='font-weight: bold;'>" in styled_html, True)

    print("\n>>> 别名 ol / ul 与全名输出一致")
    check("ol 别名.md",
          str(dict2str([{"ol": plain}], type="markdown")),
          str(dict2str(ol, type="markdown")))
    check("ul 别名.html",
          str(dict2str([{"ul": plain}], type="html")),
          str(dict2str(ul, type="html")))

    print("\n>>> 列表项缺少 content 必须报错")
    check_raises("列表项缺content", ValueError,
                 lambda: str(dict2str([{"ol": {"contents": [{}]}}],
                                      type="markdown")))
    check_raises("items不是dict", TypeError,
                 lambda: str(dict2str([{"ol": {"contents": [
                     {"content": "x", "items": []}]}}], type="markdown")))


# ---------------------------------------------------------------------------
# 7. style 样式参数（仅 html 生效）
# ---------------------------------------------------------------------------


def test_style():
    banner("7. style 样式（仅 html 输出生效）")

    node = [{"h1": {"content": "红色标题", "style": "color: red;"},
             "bold": {"content": "加粗", "style": "font-size: 20px;"}}]
    html_out = render(node, "html")
    check("h1 style",
          "<h1 style='color: red;'>红色标题</h1>" in html_out, True)
    check("bold style",
          "<strong style='font-size: 20px;'>加粗</strong>" in html_out, True)

    # txt / markdown 下样式不产生任何输出
    check("style 不影响md", str(dict2str(node, type="markdown")),
          "# 红色标题\n**加粗**\n")
    check("style 不影响txt", str(dict2str(node, type="txt")),
          "红色标题\n加粗\n")


# ---------------------------------------------------------------------------
# 8. end 自定义结尾符
# ---------------------------------------------------------------------------


def test_end():
    banner("8. end 自定义结尾符")

    node = [{"bold": {"content": "A", "end": " | "}},
            {"bold": {"content": "B", "end": "\n\n"}}]
    check("自定义end.md", render(node, "markdown"), "**A** | **B**\n\n")
    check("空end.md",
          str(dict2str([{"bold": {"content": "x", "end": ""}}],
                       type="markdown")),
          "**x**")
    check("自定义end.html",
          str(dict2str([{"link": {"url": "u", "end": "<br>\n"}}],
                       type="html")),
          "<a href='u'>a link</a><br>\n")


# ---------------------------------------------------------------------------
# 9. HTML 转义：默认转义，可全局或逐元素关闭
# ---------------------------------------------------------------------------


def test_escape():
    banner("9. HTML 转义（防注入）")

    xss = [{"bold": {"content": "<script>alert('x')</script>"}}]
    print("\n>>> 默认转义文本节点")
    out = render(xss, "html")
    check("文本节点转义", out,
          "<strong>&lt;script&gt;alert('x')&lt;/script&gt;</strong>\n")
    check("md 不转义尖括号", str(dict2str(xss, type="markdown")),
          "**<script>alert('x')</script>**\n")

    print("\n>>> 属性值转义（url 中的引号无法逃逸属性）")
    node = [{"img": {"url": "x' onerror='alert(1)"}}]
    out = str(dict2str(node, type="html"))
    check("属性值转义", out,
          "<img src='x&#x27; onerror=&#x27;alert(1)' alt='a image'/>")
    check("属性中的 & 也转义",
          "a?b=1&amp;c=2" in str(dict2str([{"img": {"url": "a?b=1&c=2"}}],
                                          type="html")),
          True)

    print("\n>>> 全局 escape=False：信任内容，原样输出")
    raw = str(dict2str(xss, type="html", escape=False))
    check("全局关闭转义", raw,
          "<strong><script>alert('x')</script></strong>\n")

    print("\n>>> 逐元素 escape=False，只放行指定节点")
    mixed = [{"bold": {"content": "<b>保留</b>", "escape": False}},
             {"bold": {"content": "<b>转义</b>"}}]
    check("逐元素转义控制", str(dict2str(mixed, type="html")),
          "<strong><b>保留</b></strong>\n"
          "<strong>&lt;b&gt;转义&lt;/b&gt;</strong>\n")


# ---------------------------------------------------------------------------
# 10. 输入形态：单 dict / list / tuple；set 切换；type=None 透传
# ---------------------------------------------------------------------------


def test_input_forms():
    banner("10. 输入形态与格式切换")

    print("\n>>> 直接传入单个 dict（自动包成单节点）")
    single = {"img": {"url": "https://a.png", "alt": "x"}}
    check("单dict输入", str(dict2str(single, type="markdown")),
          "![x](https://a.png)\n")

    print("\n>>> 输入 tuple[dict, ...] 也可接受")
    check("tuple输入",
          str(dict2str(({"h1": {"content": "T"}},), type="markdown")),
          "# T\n")

    print("\n>>> set() 在三种格式间切换，并返回 self 支持链式调用")
    d = dict2str([{"bold": {"content": "x"}}])
    check("set html", str(d.set("html")), "<strong>x</strong>\n")
    check("set markdown", str(d.set("markdown")), "**x**\n")
    check("set 链式", str(dict2str([{"h1": {"content": "T"}}]).set("html")),
          "<h1>T</h1>\n")

    print("\n>>> type=None 时原样 str() 透传，且渲染不会修改输入")
    data = {"a": 1}
    check("type=None 透传", str(dict2str(data)), str(data))
    d = dict2str(single, type="markdown")
    str(d)
    str(d)  # 旧版本第二次渲染会出错（dict 被改成 list）
    check("渲染幂等且不改输入", isinstance(single, dict) and str(d),
          "![x](https://a.png)\n")

    print("\n>>> set 不支持的格式直接报错")
    check_raises("非法格式", ValueError, lambda: dict2str([], type="pdf"))


# ---------------------------------------------------------------------------
# 11. 输入校验：所有错误都应得到明确异常
# ---------------------------------------------------------------------------


def test_validation():
    banner("11. 输入校验（明确的异常信息）")

    check_raises("未知元素名",
                 ValueError,
                 lambda: str(dict2str([{"notExist": {"content": "x"}}],
                                      type="html")))
    check_raises("content 是字符串",
                 TypeError,
                 lambda: str(dict2str("hello", type="html")))
    check_raises("列表节点不是dict",
                 TypeError,
                 lambda: str(dict2str(["hello"], type="html")))
    check_raises("元素参数不是dict",
                 TypeError,
                 lambda: str(dict2str([{"h1": "x"}], type="html")))
    check_raises("保留字 _level",
                 ValueError,
                 lambda: str(dict2str([{"h1": {"content": "x", "_level": 1}}],
                                      type="html")))
    print("（5 类非法输入均已抛出对应异常）")


# ---------------------------------------------------------------------------
# main：依次执行所有分区，任一断言失败则以退出码 1 结束
# ---------------------------------------------------------------------------


SECTIONS = [
    test_inline_elements,
    test_headings,
    test_link_and_image,
    test_task_list,
    test_table,
    test_lists,
    test_style,
    test_end,
    test_escape,
    test_input_forms,
    test_validation,
]


def main():
    print("dict2str 功能演示与测试（Python "
          + ".".join(map(str, sys.version_info[:2])) + "）")

    for section in SECTIONS:
        section()

    banner(f"全部通过：共 {_passed} 个断言")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as e:
        print(e)
        sys.exit(1)
