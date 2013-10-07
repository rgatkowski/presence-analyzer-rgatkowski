# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday/')

    def test_presence_weekday_page(self):
        """
        Test presence weekday page.
        """
        resp = self.client.get('/presence_weekday/')
        self.assertEqual(resp.status_code, 200)

    def test_mean_time_weekday_page(self):
        """
        Test mean time weekday page.
        """
        resp = self.client.get('/mean_time_weekday/')
        self.assertEqual(resp.status_code, 200)

    def test_presence_start_end_page(self):
        """
        Test presence start end page.
        """
        resp = self.client.get('/presence_start_end/')
        self.assertEqual(resp.status_code, 200)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_users_v2(self):
        """
        Test users v2 listing.
        """
        resp = self.client.get('/api/v2/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(data[0], {
            u'user_id': 10,
            u'name': u'Maciej Zięba',
            u'avatar': u'https://intranet.stxnext.pl/api/images/users/10'
        })

    def test_api_mean_time_weekday(self):
        '''
        Test mean presence time of given user grouped by weekday.
        '''
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[0], ["Mon", 0])
        self.assertListEqual(data[1], ["Tue", 24222.0])

    def test_api_presence_weekday(self):
        '''
        Test total presence time of given user grouped by weekday.
        '''
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], ['Weekday', 'Presence (s)'])
        self.assertListEqual(data[2], ['Tue', 48444])

    def test_api_presence_start_end_view(self):
        '''
        Test mean time to come to the office and mean time he leaves.
        '''
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(data[0], ['Mon', 0, 0])
        self.assertListEqual(data[1], ['Tue', 34250.0, 58472.0])
        self.assertListEqual(data[2], ['Wed', 31572.0, 60157.0])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_seconds_since_midnight(self):
        '''
        Test change time to seconds.
        '''
        time_ = utils.seconds_since_midnight(datetime.time(10, 5, 35))
        self.assertEqual(time_, 36335)
        time_ = utils.seconds_since_midnight(datetime.time(18, 49, 7))
        self.assertEqual(time_, 67747)

    def test_interval(self):
        '''
        Test calculate interval
        '''
        start = datetime.time(9, 39, 5)
        stop = datetime.time(17, 59, 52)
        interval = utils.interval(start, stop)
        self.assertEqual(interval, 30047)
        start = datetime.time(3, 15, 41)
        stop = datetime.time(20, 55, 22)
        interval = utils.interval(start, stop)
        self.assertEqual(interval, 63581)

    def test_mean(self):
        '''
        Test calculate arithmetic mean
        '''
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([2345, 6789]), 4567)
        self.assertEqual(utils.mean([999, 111, 555]), 555)

    def test_group_by_weekend(self):
        '''
        Test group presence entries by weekday.
        '''
        data = utils.get_data()
        group_data = utils.group_by_weekday(data[10])
        self.assertIsInstance(group_data, dict)
        self.assertItemsEqual(group_data.keys(), [0, 1, 2, 3, 4, 5, 6])
        self.assertListEqual(group_data[5], [])
        self.assertIn(30047.0, group_data[1])

    def test_group_by_weekday_with_sec(self):
        '''
        Test group presence entries by weekday in seconds.
        '''
        data = utils.get_data()
        group_data = utils.group_by_weekday_with_sec(data[10])
        self.assertIsInstance(group_data, dict)
        self.assertItemsEqual(group_data.keys(), [0, 1, 2, 3, 4, 5, 6])
        self.assertIsInstance(group_data[0], dict)
        self.assertDictEqual(group_data[5], {'start': [], 'end': []})
        self.assertIsInstance(group_data[0]['start'], list)
        self.assertIsInstance(group_data[0]['end'], list)
        self.assertIn(34745, group_data[1]['start'])
        self.assertIn(64792, group_data[1]['end'])

    def test_get_users_xml(self):
        '''
        Test loads users from xml file
        '''
        data = utils.get_users_xml()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [141, 176, 170, 10])
        self.assertDictEqual(data[10], {
            u'name': u'Maciej Zięba',
            u'avatar': u'https://intranet.stxnext.pl/api/images/users/10'
        })


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
