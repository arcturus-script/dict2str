from dict2str import dict2str

d = dict2str(
    [
        {
            "h1": {
                "content": "title 1",
                "style": "color: red",
            }
        },
        {
            "h2": {
                "content": "title 2",
                "style": "color: green",
            },
        },
        {
            "h3": {
                "content": "title 3",
                "style": "color: yellow",
            },
            "h4": {
                "content": "title 4",
                "style": "color: orange",
            },
            "h5": {
                "content": "title 5",
            },
            "h6": {
                "content": "title 6",
            },
        },
    ],
    type="markdown",
)

print(d)

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

d = dict2str(
    [
        {
            "txt": {
                "content": "This is a normal text.",
                "style": "font-size: 10px",
            },
        },
        {
            "code": {
                "content": "print('hello')",
            },
        },
        {
            "blockQuote": {
                "content": "666",
                "style": "color: blue",
            },
            "strikethrough": {
                "content": "yeah",
                "style": "color: yello",
            },
            "italic": {
                "content": "yeah",
                "style": "color: yello",
            },
            "bold": {
                "content": "yeah",
                "style": "color: green",
            },
        },
        {
            "link": {
                "url": "https://google.com",
                "content": "this is a link",
                "style": "color: red",
            },
            "img": {
                "url": "https://abc.png",
                "alt": "this is an image",
            },
        },
        {
            "link": {
                "url": "www.baidu.com",
                "end": "++++\n",
            },
        },
    ],
    type="markdown",
)

print(d)

d = dict2str(
    [
        {
            "table": {
                "contents": [
                    ("描述", "内容"),
                    ("1", "A"),
                ],
                "end": "\n",
                "position": "left",
            },
        },
    ],
    type="html",
)

print(d)

d.set("markdown")

print(d)


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
                                                        "style": "color: red",
                                                    },
                                                ],
                                                "style": "color: red",
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
                                                        "style": "color: red",
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
                        "style": "color: red",
                    },
                    {
                        "content": "do homeworks",
                    },
                ],
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
