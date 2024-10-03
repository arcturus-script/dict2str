# dict2str

Support converting dictionary to markdown, html and txt

## Usage

### Input list

```python
d = dict2str(
    [
        {
            "taskList": {
                "contents": [
                    {
                        "content": "run 100 kilometers",
                        "style": "color: red",
                    },
                    {
                        "content": "do homeworks",
                        "complete": True,
                    },
                ]
            },
        },
    ],
    type="html",
)

print(d)

d.set("markdown")

print(d)

d.set("txt")

print(d)

# <label>
#   <input style='color: red' type='checkbox' disabled='true'>run 100 kilometers</input>
# </label>
# <label>
#   <input type='checkbox' disabled='true' checked>do homeworks</input>
# </label>

# - [ ] run 100 kilometers
# - [x] do homeworks

# 🔴 run 100 kilometers
# 🟢 do homeworks
```

```python
d = dict2str(
    [
        {
            "orderedList": {
                "contents": [
                    {
                        "content": "A",
                        "items": {
                            "unOrderedList": {
                                "contents": [
                                    {
                                        "content": "B",
                                        "items": {
                                            "orderedList": {
                                                "contents": [
                                                    {
                                                        "content": "C",
                                                    },
                                                    {
                                                        "content": "D",
                                                    },
                                                ],
                                            }
                                        },
                                    },
                                    {
                                        "content": "E",
                                        "items": {
                                            "unOrderedList": {
                                                "contents": [
                                                    {
                                                        "content": "F",
                                                    },
                                                    {
                                                        "content": "G",
                                                    },
                                                ],
                                            }
                                        },
                                    },
                                ],
                            }
                        },
                    },
                    {
                        "content": "H",
                    },
                ],
            },
            "unOrderedList": {
                "contents": [
                    {
                        "content": "run 100 kilometers",
                    },
                    {
                        "content": "do homeworks",
                    },
                ],
            },
        },
    ],
    type="markdown",
)

print(d)

# 1. A
#   - B
#     1. C
#     2. D
#   - E
#     - F
#     - G
# 2. H
# - run 100 kilometers
# - do homeworks
```

### Input dictionary

```python
d = dict2str(
    {
        "img": {
            "url": "https://abc.png",
            "alt": "this is an image",
        }
    },
    type="markdown",
)

print(d)

# ![this is an image](https://abc.png)
```

## Support elements

| type            | Element        | Example                                                                                                            |
| --------------- | -------------- | ------------------------------------------------------------------------------------------------------------------ |
| `h1`            | Heading 1      | `{ "h1": { "content": "title 1" } }`                                                                               |
| `h2`            | Heading 2      | `{ "h2": { "content": "title 2" } }`                                                                               |
| `h3`            | Heading 3      | `{ "h3": { "content": "title 3" } }`                                                                               |
| `h4`            | Heading 4      | `{ "h4": { "content": "title 4" } }`                                                                               |
| `h5`            | Heading 5      | `{ "h5": { "content": "title 5" } }`                                                                               |
| `h6`            | Heading 6      | `{ "h6": { "content": "title 6" } }`                                                                               |
| `blockquote`    | Blockquote     | `{ "blockquote": { "content": "This is a blockquote" } }`                                                          |
| `img`           | Image          | `{ "img": { "url": "https://abc.png", "alt": "this is an image", } }`                                              |
| `ul`            | Unordered list | `{ "unOrderedList": { "contents": [{"content": "run 100 kilometers"}, {"content": "do homeworks"}]}}`              |
| `ol`            | Ordered list   | `{ "orderedList": { "contents": [{"content": "run 100 kilometers"}, {"content": "do homeworks"}]}}`                |
| `table`         | Table          | `{ "table": { "contents": [("desc", "content"), ("A", "B")], "position": "left" }`                                 |
| `link`          | Link           | `{ "link": { "url": "https://google.com", "content": "this is a link" }`                                           |
| `tasklist`      | Task list      | `{ "tasklist": "contents": [{"content": "run 100 kilometers" },{ "content": "do homeworks", "complete": True }] }` |
| `code`          | Code           | `{ "code": { "content": "print('hello')" } }`                                                                      |
| `italic`        | Italic         | `{ "italic": { "content": "good" } }`                                                                              |
| `strikethrough` | Strikethrough  | `{ "strikethrough": { "content": "nice" } }`                                                                       |
| `bold`          | Bold           | `{ "bold": { "content": "excellent", "end": "\n" } }`                                                              |
