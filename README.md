# dict2str

Support converting dictionary to markdown、html、txt

## Usage

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
