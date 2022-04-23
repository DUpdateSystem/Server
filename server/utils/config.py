import re


def get_url_list(url_template: str, number: int):
    port = int(re.search(r'\([0-9]+\)', url_template).group(0)[1:-1])
    return [
        url_template.replace(f'({port})', str(port + i)) for i in range(number)
    ]
