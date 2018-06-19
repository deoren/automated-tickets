#!/usr/bin/env python3

import os
import pprint
import sys

supported_date_format_patterns = [

    # >>> d = {}
    # >>> d['dict1'] = {}
    # >>> d['dict1']['innerkey'] = 'value'
    # >>> d
    # {'dict1': {'innerkey': 'value'}}

        {
            'format_string': '%Y-%m-%d',
            'name':'daily',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'twice_week',
            'display_name': 'twice weekly',
        },
        {
            'format_string': '%Y-%m-%d',
            'name':'weekly',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_monday',
            'display_name': 'every monday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_tuesday',
            'display_name': 'every tuesday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_wednesday',
            'display_name': 'every wednesday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_thursday',
            'display_name': 'every thursday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_friday',
            'display_name': 'every friday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_saturday',
            'display_name': 'every saturday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'weekly_sunday',
            'display_name': 'every sunday',
        },
        {
            'format_string': '%Y-%m-%d',
            'name': 'twice_month',
            'display_name': 'twice monthly',
        },
        {
            'format_string': '%B %Y',
            'name':'monthly',
        },
        {
            'format_string': '%B %Y',
            'name': 'twice_year',
            'display_name': 'twice yearly',
        },
        {
            'format_string': '%B %Y',
            'name':'quarterly',
        },
        {
            'format_string': '%Y',
            'name':'yearly',
        },
        # End stock keywords
        {
            'format_string': '%B_%d',
            'name': 'month_abbrv_day',
            'display_name': '',
        },


]

pprint.pprint(supported_date_format_patterns)

#for i in range(0, my_list_len):
for date_pattern in supported_date_format_patterns:

    # This is where some logic can be used to dynamically calculate
    # the display value to the current day's date if it's not already
    # explicitly set.
    if 'display_name' in date_pattern:
        display_name = date_pattern['display_name']
    else:
        display_name = ''

    #print("date pattern is {}".format(date_pattern))
    print("pattern {} format string: {}, display name: {}".format(
        date_pattern['name'],
        date_pattern['format_string'],
        display_name
        ))

#print(supported_date_format_patterns[0]['daily']['format_string'])
