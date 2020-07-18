class HttpRequestBody:
    type = None
    text = None

    def __init__(self, body_type: str, text: str):
        self.type = body_type
        self.text = text
