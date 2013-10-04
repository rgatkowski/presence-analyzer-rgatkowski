# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar

from flask import redirect, render_template, url_for

from presence_analyzer.main import app
from presence_analyzer.utils import jsonify, get_data, mean, \
    group_by_weekday, group_by_weekday_with_sec, get_users_xml

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('presence_weekday_view_page'))


@app.route('/presence_weekday/')
def presence_weekday_view_page():
    '''
    Render presence weekday view
    '''
    return render_template('presence_weekday.html')


@app.route('/mean_time_weekday/')
def mean_time_weekday_view_page():
    '''
    Render mean time weekday view
    '''
    return render_template('mean_time_weekday.html')


@app.route('/presence_start_end/')
def presence_start_end_view_page():
    '''
    Render presence start end view
    '''
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    data_xml = get_users_xml()
    result = []
    for i in data.keys():
        try:
            name = data_xml[i]['name']
            avatar = data_xml[i]['avatar']
        except KeyError:
            name = 'User {0}'.format(str(i))
            avatar = ''

        result.append({'user_id': i, 'name': name, 'avatar': avatar})

    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean time to come to the office and mean time he leaves.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday_with_sec(data[user_id])
    result = [
        (
            calendar.day_abbr[weekday],
            mean(dates["start"]),
            mean(dates["end"])
        ) for weekday, dates in weekdays.items()]

    return result
