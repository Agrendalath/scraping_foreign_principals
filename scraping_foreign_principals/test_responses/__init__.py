import os
from scrapy.http import HtmlResponse, Request


def fake_response_from_file(file_name: str, url: str = None) -> HtmlResponse:
    """
    Create a Scrapy fake HtmlResponse from a HTML file.
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    request.headers['Cookie'] = 'TEST'
    request.meta['data'] = {}
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    with open(file_path) as file_content:
        response = HtmlResponse(
            url=url,
            request=request,
            body=file_content.read(),
            encoding='utf-8')

    return response
