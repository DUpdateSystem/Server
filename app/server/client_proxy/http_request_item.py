from .http_request_body import HttpRequestBody


class HttpRequestItem:
    def __init__(self, method: str, url: str, headers: dict,
                 body: HttpRequestBody = None):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def to_dict(self):
        # 请求头数据
        headers_list = []
        for key, value in self.headers.items():
            headers_list.append({
                "key": key,
                "value": value
            })
        # 请求体数据
        body_type = self.body.type
        body_text = self.body.text
        if not body_type or not body_text:
            body = None
        else:
            body = {
                "type": body_type,
                "text": body_text
            }
        # 组装数据字典
        return {
            "method": self.method,
            "url": self.url,
            "headers": headers_list,
            "body": body
        }
