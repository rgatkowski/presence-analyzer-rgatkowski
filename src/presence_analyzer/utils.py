# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime
from lxml import etree

from flask import Response

from presence_analyzer.main import app
from presence_analyzer.decorators import DecoratorCache

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


@DecoratorCache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def get_users_xml():
    """
    Extracts users data from XML file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            'name': 'full name',
            'avatar': avatar_url
        }
    }
    """
    data = {}
    tree = etree.parse(app.config['USERS_XML'])
    try:
        host = tree.xpath("//server/host/text()")[0]
    except KeyError:
        log.debug('No host in XML file', exc_info=True)
        host = ''
    try:
        protocol = tree.xpath("//server/protocol/text()")[0]
    except KeyError:
        log.debug('No protocol in XML file', exc_info=True)
        protocol = ''
    for i, user in enumerate(tree.iter('user')):
        try:
            user_id = int(user.get('id'))
            name = user.find('name').text
            avatar = user.find('avatar').text
        except (ValueError, TypeError):
            log.debug('Problem with line %d: ', i, exc_info=True)
            name = ''
            avatar = ''

        data[user_id] = {
            'name': name,
            'avatar': ''.join([protocol, '://', host, avatar])
        }

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_weekday_with_sec(items):
    """
    Groups data by weekday with seconds.
    """
    result = {i: {"start": [], "end": []} for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()]["start"].append(seconds_since_midnight(start))
        result[date.weekday()]["end"].append(seconds_since_midnight(end))
    return result
