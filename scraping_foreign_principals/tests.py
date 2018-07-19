# pylint: disable=E0401, W0212
import json
import os
import unittest

from spiders.principals_spider import PrincipalsSpider
from test_responses import fake_response_from_file


class PrincipalsSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = PrincipalsSpider()

    def test_parse(self):
        """
        Test initial parsing, which disables grouping by country and forges
        POST request for data collection. The parser should gather all
        parameters required for POST requests.
        """
        results = next(
            self.spider.parse(fake_response_from_file('base_site.html'))
        )

        checks = {
            'headers': ['Cookie'],
            'form_data': [
                'p_widget_action_mod',
                'p_instance',
                'p_request',
                'p_flow_id',
                'p_flow_step_id',
                'p_widget_name',
                'p_widget_num_return',
                'x01',
            ],
        }
        for key in checks:
            self.assertIsNotNone(results.meta.get(key))

            for value in checks[key]:
                self.assertIsNotNone(results.meta[key].get(value))

    def test_parse_principals(self):
        """
        Test parsing single principal.
        """
        results = next(
            self.spider._parse_principals(
                fake_response_from_file('principals_table.html')
            )
        )

        expected = {
            'url': 'http://www.example.com/f?p=185:200:9224845945129::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:3690,Exhibit%20AB,TAIWAN',  # noqa pylint: disable=C0301
            'foreign_principal': 'Taipei Economic & Cultural Representative Office in the U.S.',  # noqa pylint: disable=C0301
            'date': '1995-08-28T00:00:00Z',
            'address': 'Washington',
            'state': 'DC',
            'country': 'TAIWAN',
            'registrant': 'International Trade & Development Agency, Inc.',
            'reg_num': '3690',
        }

        for key in expected:
            self.assertEqual(expected[key], results.meta['data'].get(key))

    def test_parse_documents(self):
        """
        Test parsing documents site.
        """
        results = next(
            self.spider._parse_documents(
                fake_response_from_file('documents.html')
            )
        )

        self.assertTrue(isinstance(results.get('exhibit_url'), list))
        self.assertEqual(28, len(results['exhibit_url']))

        for document in results['exhibit_url']:
            self.assertIsNotNone(document)

    def test_parse_date(self):
        """
        Test parsing date to RFC 3339.
        """
        examples = {
            '08/28/1995': '1995-08-28T00:00:00Z',
            '11/08/2013': '2013-11-08T00:00:00Z',
        }

        for key, value in examples.items():
            self.assertEqual(value, PrincipalsSpider._parse_date(key))

    def test_results(self):
        """
        Test if all params (except `state`) are not None.
        Also check if `exhibit_url` is a list.
        """
        keys = ['url', 'country', 'reg_num', 'address', 'date', 'registrant']

        script_dir = os.path.dirname(os.path.realpath(__file__))
        results_rel_path = 'test_responses/results.json'
        with open(os.path.join(script_dir, results_rel_path)) as file:
            results = json.load(file)

        for row in results:
            for key in keys:
                self.assertIsNotNone(row.get(key))

            self.assertTrue('state' in row)  # state can be None
            self.assertTrue(isinstance(row.get('exhibit_url'), list))


if __name__ == '__main__':
    unittest.main()
