import scrapy
from copy import deepcopy
from datetime import datetime
from scrapy.http.response.html import HtmlResponse
from scrapy.selector.unified import Selector
from typing import Generator, Iterator, Union


class PrincipalsSpider(scrapy.Spider):
    name = 'principals'

    SITE = 'https://efile.fara.gov/pls/apex/f?p=185:130:0::NO:RP,130:P130_DATERANGE:N'  # noqa
    ROWS_FETCH = 30

    def start_requests(self):
        """
        Parse arguments.
        """
        rows = getattr(self, 'rows', None)
        if rows and rows.isdigit():
            self.ROWS_FETCH = int(rows)
        yield scrapy.Request(self.SITE, callback=self.parse, dont_filter=True)

    def parse(self, response: HtmlResponse):
        """
        Parse initial site.
        Remove grouping by countries and gather data for POST requests.
        """
        url = 'https://efile.fara.gov/pls/apex/wwv_flow.show'
        headers = {
            'Cookie': response.request.headers['Cookie'].decode('utf-8')
        }
        form_data = {
            'p_widget_action_mod': self.generate_next_page_action(0),
            'p_instance': response.xpath(
                '//input[@name="p_instance"]/@value').extract_first(),
            'p_request': 'APXWGT',
            'p_flow_id': '185',
            'p_flow_step_id': '130',
            'p_widget_name': 'worksheet',
            'x01': response.xpath(
                '//input[@id="apexir_WORKSHEET_ID"]/@value').extract_first(),
            'p_widget_num_return': str(self.ROWS_FETCH)
        }
        oneshot = deepcopy(form_data)
        disable_country_grouping = {
            'p_widget_mod': 'ACTION',
            'p_widget_action': 'BREAK_TOGGLE',
            'x03': 'COUNTRY_NAME',
            'x04': 'N'
        }
        oneshot.update(disable_country_grouping)

        request = scrapy.FormRequest(
            url=url,
            headers=headers,
            callback=self.parse_principals,
            formdata=oneshot,
        )

        request.meta['url'] = url
        request.meta['headers'] = headers
        request.meta['form_data'] = form_data
        request.meta['first_row'] = 0
        yield request

    def generate_next_page_action(self, from_: int) -> str:
        """
        Generate param for requesting next paginated data set.
        """
        return f'pgR_min_row={from_}max_rows={self.ROWS_FETCH}rows_fetched=' \
               f'{self.ROWS_FETCH} '

    @staticmethod
    def retrieve_table_field(response: HtmlResponse) -> \
            Generator[Selector, None, None]:
        """
        Yield single table cell.
        """
        for field in response.css('.apexir_WORKSHEET_DATA td'):
            yield field

    @staticmethod
    def extract_next(field: Iterator[Selector]) -> Union[str, None]:
        """
        Extract text from Selector from Iterator. Strip whitespaces.
        """
        result: str = next(field).css('::text').extract_first()
        if result is not None:
            return result.strip()

    @staticmethod
    def parse_date(date: str) -> Union[str, None]:
        """
        Parse date to RFC 3339 (https://tools.ietf.org/html/rfc3339).
        """
        result = None
        try:
            result = datetime.strptime(date, '%m/%d/%Y').isoformat() + 'Z'
        except ValueError:
            pass

        return result

    def parse_principals(self, response: HtmlResponse):
        """
        Parse principal and yield to retrieve one's documents.
        Parsing documents is not cached because different principals of the
        same country can have the same documents.
        """
        field = self.retrieve_table_field(response)

        processed_rows = 0
        while True:
            try:
                data = {
                    'url': response.urljoin(
                        next(field).css('a::attr(href)').extract_first()),
                    'foreign_principal': self.extract_next(field),
                    'date': self.parse_date(self.extract_next(field)),
                    'address': self.extract_next(field),
                    'state': self.extract_next(field),
                    'country': self.extract_next(field),
                    'registrant': self.extract_next(field),
                    'reg_num': self.extract_next(field),
                    # TODO: Find out what to do about the one below.
                    # 'reg_date': self.parse_date(self.extract_next(field)),

                }
                next(field)  # just skip 'reg_date'

                documents_request = scrapy.Request(
                    url=data['url'],
                    callback=self.parse_documents,
                    dont_filter=True,
                )
                documents_request.meta['data'] = data
                yield documents_request

            except StopIteration:
                break

            processed_rows += 1

        if not processed_rows:
            return

        meta = response.meta
        meta['first_row'] += processed_rows
        meta['form_data']['p_widget_action_mod'] = \
            self.generate_next_page_action(meta['first_row'])

        request = scrapy.FormRequest(
            url=meta['url'],
            headers=meta['headers'],
            formdata=meta['form_data'],
            callback=self.parse_principals,
        )

        for s in ['url', 'headers', 'form_data', 'first_row']:
            request.meta[s] = meta[s]

        yield request

    @staticmethod
    def parse_documents(response: HtmlResponse):
        """
        Parse principal's documents.
        """
        data = response.meta['data']
        data['exhibit_url'] = response.css(
            'td[headers=DOCLINK] ::attr(href)').extract()
        yield data
