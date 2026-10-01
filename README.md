# dict2str

用 Python 字典/列表描述富文本内容，一键转换成 **txt / Markdown / HTML** 三种格式。

- 纯 Python 实现，零第三方依赖
- 支持 Python **3.9+**
- 无状态渲染，线程安全，可重复调用
- HTML 输出默认转义，防止内容注入
- 支持有序/无序列表任意层级嵌套、任务列表、表格、样式等

---

## 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [数据结构](#数据结构)
- [支持的元素](#支持的元素)
- [通用参数](#通用参数)
- [列表嵌套](#列表嵌套)
- [表格](#表格)
- [HTML 转义](#html-转义)
- [切换输出格式](#切换输出格式)
- [异常说明](#异常说明)
- [API 参考](#api-参考)
- [运行示例与测试](#运行示例与测试)

---

## 安装

要求 Python >= 3.9：

```bash
# 克隆后本地安装
git clone https://github.com/arcturus-script/dict2str.git
cd dict2str
pdm install
```

## 快速开始

```python
from dict2str import dict2str

d = dict2str(
    [
        {"h1": {"content": "今日任务", "style": "color: red"}},
        {"taskList": {"contents": [
            {"content": "跑 10 公里"},
            {"content": "写完作业", "complete": True},
        ]}},
    ],
    type="markdown",   # 可选："markdown" / "html" / "txt"
)

print(d)
# # 今日任务
# - [ ] 跑 10 公里
# - [x] 写完作业

d.set("html")
print(d)
# <h1 style='color: red'>今日任务</h1>
# <label>
#   <input type='checkbox' disabled/>跑 10 公里
# </label>
# <label>
#   <input type='checkbox' disabled checked/>写完作业
# </label>
```

## 数据结构

输入是 **一个元素节点**，或 **元素节点组成的列表/元组**：

```python
# 单个节点：{元素名: {参数}}
dict2str({"h1": {"content": "标题"}}, type="markdown")

# 多个节点（推荐，同一节点 dict 内可并排放多个不同元素，按字典顺序输出）
dict2str([
    {"h1": {"content": "标题"}},
    {"bold": {"content": "正文"}},
], type="markdown")
```

- **元素名**：见下表，如 `h1`、`bold`、`orderedList`
- **参数**：每个元素一个 dict，最常用的是 `content`
- 渲染过程**不会修改输入数据**，同一个对象可以反复 `str()` / 切换格式

## 支持的元素

| 元素名（别名）              | 说明                            | 关键参数                            |
| --------------------------- | ------------------------------- | ----------------------------------- |
| `txt`                       | 普通文本（HTML 下输出 `<div>`） | `content`                           |
| `bold`                      | 粗体 `**text**` / `<strong>`    | `content`                           |
| `italic`                    | 斜体 `*text*` / `<i>`           | `content`                           |
| `strikethrough`             | 删除线 `~~text~~` / `<del>`     | `content`                           |
| `code`                      | 行内代码 `` `text` `` / `<pre>` | `content`                           |
| `blockQuote` (`blockquote`) | 引用 `> text` / `<blockquote>`  | `content`                           |
| `h1` ~ `h6`                 | 一到六级标题                    | `content`                           |
| `h`                         | 通用标题                        | `level`(1~6)、`content`             |
| `link`                      | 链接                            | `url`、`content`（默认 `"a link"`） |
| `img`                       | 图片                            | `url`、`alt`（默认 `"a image"`）    |
| `orderedList` (`ol`)        | 有序列表                        | `contents`、`items`（嵌套）         |
| `unOrderedList` (`ul`)      | 无序列表                        | `contents`、`items`（嵌套）         |
| `taskList` (`tasklist`)     | 任务勾选列表                    | `contents`（每项含 `complete`）     |
| `table`                     | 表格                            | `contents`、`position`、样式参数    |

### 基础元素示例

```python
nodes = [
    {"txt":           {"content": "普通文本"}},
    {"bold":          {"content": "加粗"}},
    {"italic":        {"content": "斜体"}},
    {"strikethrough": {"content": "删除线"}},
    {"code":          {"content": "print('hi')"}},
    {"blockQuote":    {"content": "引用内容"}},
    {"h":             {"level": 2, "content": "二级标题"}},
]
```

| 元素            | txt           | markdown            | html                                |
| --------------- | ------------- | ------------------- | ----------------------------------- |
| `bold`          | `加粗`        | `**加粗**`          | `<strong>加粗</strong>`             |
| `italic`        | `斜体`        | `*斜体*`            | `<i>斜体</i>`                       |
| `strikethrough` | `删除线`      | `~~删除线~~`        | `<del>删除线</del>`                 |
| `code`          | `print('hi')` | `` `print('hi')` `` | `<pre>print('hi')</pre>`            |
| `blockQuote`    | `引用内容`    | `> 引用内容`        | `<blockquote>引用内容</blockquote>` |
| `h2`            | `二级标题`    | `## 二级标题`       | `<h2>二级标题</h2>`                 |

### 链接与图片

```python
[
    {"link": {"url": "https://example.com", "content": "示例网站"}},
    # txt:  示例网站: https://example.com
    # md :  [示例网站](https://example.com)
    # html: <a href='https://example.com'>示例网站</a>

    {"img": {"url": "https://example.com/a.png", "alt": "示意图"}},
    # txt:  示意图: https://example.com/a.png
    # md :  ![示意图](https://example.com/a.png)
    # html: <img src='https://example.com/a.png' alt='示意图'/>
]
```

### 任务列表

```python
{"taskList": {"contents": [
    {"content": "未完成任务"},
    {"content": "已完成任务", "complete": True},
]}}
```

txt：

```text
🔴 未完成任务
🟢 已完成任务
```

markdown：

```markdown
- [ ] 未完成任务
- [x] 已完成任务
```

html：

```html
<label> <input type="checkbox" disabled />未完成任务 </label>
<label> <input type="checkbox" disabled checked />已完成任务 </label>
```

## 通用参数

所有元素都支持以下参数（未使用到时自动忽略）：

| 参数      | 适用格式 | 默认值                                                                | 说明                                                         |
| --------- | -------- | --------------------------------------------------------------------- | ------------------------------------------------------------ |
| `content` | 全部     | —                                                                     | 元素正文                                                     |
| `end`     | 全部     | 多数元素为 `"\n"`；`italic`/`strikethrough`/`code` 的 md/html 为 `""` | 追加在输出末尾的字符串                                       |
| `style`   | html     | `None`                                                                | CSS 样式，渲染成 `style='...'`；txt/md 下忽略                |
| `escape`  | html     | `True`                                                                | 是否转义正文里的 HTML 特殊字符，详见 [HTML 转义](#html-转义) |

```python
{"bold": {"content": "注意", "end": " | ", "style": "color: red;"}}
# markdown: **注意** |
# html    : <strong style='color: red;'>注意</strong> |
```

## 列表嵌套

列表的每一项是 `{"content": ..., "items": {...}, "style": ...}`，
其中 `items` 又是一个或多个元素定义，从而支持任意层级、不同类型列表互相嵌套：

```python
{"orderedList": {"contents": [
    {"content": "A", "items": {"unOrderedList": {"contents": [
        {"content": "B"},
        {"content": "C", "items": {"orderedList": {"contents": [
            {"content": "D"},
            {"content": "E"},
        ]}}},
    ]}}},
    {"content": "F"},
]}}
```

markdown 输出（自动按层级缩进）：

```markdown
1. A

- B
- C
  1. D
  2. E

2. F
```

HTML 下列表容器和每个列表项都可以单独设置 `style`：

```python
{"orderedList": {
    "style": "color: red;",          # <ol style='...'>
    "contents": [
        {"content": "重点项", "style": "font-weight: bold;"},  # <li style='...'>
        {"content": "普通项"},
    ],
}}
```

## 表格

`contents` 是二维数据，**第一行是表头**；可以传 list 或 tuple，行列长度可以不一致（短行自动补空单元格）。

```python
{"table": {
    "contents": [
        ("姓名", "分数"),
        ("张三", "95"),
        ("李四", "88"),
    ],
    "position": "center",   # markdown 对齐：center(默认) / left / right / 其他值(无冒号)
}}
```

```markdown
| 姓名 | 分数 |
| :--: | :--: |
| 张三 |  95  |
| 李四 |  88  |
```

- `position="left"` → `:--`，`"right"` → `--:`，非法值 → `--`
- markdown 单元格中的 `|` 会自动转义成 `\|`，换行替换为空格
- HTML 表格每行数据渲染为独立的 `<tr>`，并支持自定义样式：

| 参数                              | 默认值                                                                      | 作用           |
| --------------------------------- | --------------------------------------------------------------------------- | -------------- |
| `style`                           | `width: 100%; border-collapse: collapse; margin-bottom: 10px;`              | `<table>` 样式 |
| `th_style`（兼容旧名 `th-style`） | `text-align: center; border: 1px solid #e6e6e6; background-color: #F5F5F5;` | 表头单元格样式 |
| `td_style`（兼容旧名 `tdStyle`）  | `text-align: center; border: 1px solid #e6e6e6;`                            | 数据单元格样式 |

txt 格式下表格用制表符分隔：`姓名\t分数\n张三\t95\n`。

## HTML 转义

为避免正文内容被浏览器当成 HTML 解析，html 输出**默认开启转义**：

```python
d = dict2str([{"bold": {"content": "<script>alert('x')</script>"}}], type="html")
print(d)
# <strong>&lt;script&gt;alert('x')&lt;/script&gt;</strong>
```

- 文本节点转义 `<`、`>`、`&`；属性值（`url`/`style` 等）额外转义单/双引号，无法逃逸属性
- 内容是自己拼接的可信 HTML 时，有两种方式放行：

```python
# 1) 全局关闭转义
dict2str(data, type="html", escape=False)

# 2) 只对某个元素关闭
[
    {"bold": {"content": "<b>保留标签</b>", "escape": False}},
    {"bold": {"content": "<b>仍然转义</b>"}},
]
```

## 切换输出格式

```python
d = dict2str(data, type="markdown")
str(d)                       # 当前格式渲染
d.set("html")                # 切换格式，返回 self，可链式调用
dict2str(data).set("txt")    # 链式写法
str(dict2str({"a": 1}))      # type=None（默认）时直接返回 str(content)
```

支持的格式：`"markdown"`、`"html"`、`"txt"`。

## 异常说明

遇到非法输入会抛出明确异常（旧版本部分错误只 `print` 提示）：

| 场景                                  | 异常                                       |
| ------------------------------------- | ------------------------------------------ |
| 不支持的输出格式，如 `type="pdf"`     | `ValueError`                               |
| 未知元素名                            | `ValueError`（信息中附带全部支持的元素名） |
| `content` 不是 dict / list / tuple    | `TypeError`                                |
| 节点列表中某项不是 dict               | `TypeError`                                |
| 元素参数不是 dict（如 `{"h1": "x"}`） | `TypeError`                                |
| 标题 `level` 不在 1~6                 | `ValueError`                               |
| 表格 `contents` 为空或不是列表        | `ValueError`                               |
| 列表项缺少 `content`                  | `ValueError`                               |
| 列表项 `items` 不是 dict              | `TypeError`                                |
| 参数中使用保留字 `_level`             | `ValueError`                               |

## API 参考

### `dict2str(content, type=None, *, escape=True)`

| 参数      | 说明                                                            |
| --------- | --------------------------------------------------------------- |
| `content` | 单个元素 dict，或元素 dict 组成的 list/tuple；不会被修改        |
| `type`    | `"markdown"` / `"html"` / `"txt"` / `None`（原样 `str()` 透传） |
| `escape`  | 仅对 html 生效，是否转义内容，默认 `True`                       |

| 方法 / 属性 | 说明                                               |
| ----------- | -------------------------------------------------- |
| `set(type)` | 切换输出格式，校验失败抛 `ValueError`，返回 `self` |
| `parse()`   | 执行渲染并返回字符串                               |
| `__str__()` | 等价于 `parse()`，因此可直接 `print(d)` / `str(d)` |

## 运行示例与测试

仓库根目录的 `example.py` 既是功能演示也是零参数测试脚本（119 个断言，覆盖全部元素、三种格式、嵌套、表格、转义与异常分支）：

```bash
pdm run python example.py        # 全部通过退出码为 0，任一失败退出码为 1
```

## License

MIT
