# Act As API

An API to serve a directory of GPT personas.

```
sample_data/bots
├── calculator.yaml
└── translate.yaml
```

**calculator.yaml**
```yaml
messages:
  - role: system
    content: Act as a calculator and only respond with the computed answer.
temperature: 0.0
```

**translate.yaml**
```yaml
messages:
  - role: system
    content: You are a translator. Only output the translation.
  - role: human
    content: Translate `{{ message }}` to {{ to }}
  temperature: 0.2
```

Note how `{{ message }}` is present `translate.yaml`, but not `calculator.yaml`. When a template is missing `{{ message }}`
a `- {role: 'human', content: {{ message }}` is automatically appended.


## Sample Request

JSON API, non-streaming:

    curl 'http://localhost:8000/bots/translate/reply?message=You+are+funny&to=Chinese'

    # {
    #   "reply": "你很有趣",
    #   "message": "You are funny",
    #   "to": "Chinese"
    # }

Streaming, content only:

    curl 'http://localhost:8000/bots/translate/reply?message=You+are+funny&to=Chinese'

    # 你很有趣
