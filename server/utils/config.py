def get_url_list(url_template: str, number: int):
    return [url_template.replace('%d', str(i), 1) for i in range(number)]
