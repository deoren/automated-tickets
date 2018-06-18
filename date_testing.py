#!/usr/bin/env python3

# Purpose: Prototype date keywords based off of specified date

import datetime
import logging
import logging.handlers
import sys

def get_valid_date_patterns(YYYYMMDD_DATE):

    valid_date_patterns = []
    specified_date = YYYYMMDD_DATE


    # TODO: What behavior should occur if we support YYYY-MM patterns?
    # Repeat the notification for every day that month?
    #
    #   >>> date = datetime.date.today()
    #   >>> date.strftime('%Y-%m')
    #   '2018-06'

    # https://docs.python.org/3.5/library/datetime.html#strftime-and-strptime-behavior
    date = datetime.date.today()
    # date.strftime('%Y')
    # '2018'
    # >>> date.strftime('%Y-%M')
    # '2018-00'
    # >>> date.strftime('%Y-%m')
    # '2018-06'
    # >>> date.strftime('%Y-%m-%d')
    # '2018-06-17'



    this_year_four_digit = date.strftime('%Y')
    this_year_two_digit = date.strftime('%y')

    # zero-padded decimal number (01, 02, 03, ...)
    this_month_two_digit = date.strftime('%m')

    # June, July, ...
    this_month_full_name = date.strftime('%B')

    # 09, 10, ...
    this_day_two_digit = date.strftime('%d')

    # 9, 10, ...
    this_today_one_digit = date.strftime('%d').lstrip('0')

    # JUNE_09

    #>>> chosen_date = '2018-06-18'
    #>>> datetime.datetime.strptime(chosen_date, '%Y-%m-%d')
    #datetime.datetime(2018, 6, 18, 0, 0)

    # >>> datetime.datetime.strptime(chosen_date, '%Y%m%d')
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # File "C:\Program Files\Python36\lib\_strptime.py", line 565, in _strptime_datetime
    #     tt, fraction = _strptime(data_string, format)
    # File "C:\Program Files\Python36\lib\_strptime.py", line 362, in _strptime
    #     (data_string, format))
    # ValueError: time data '2018-06-18' does not match format '%Y%m%d'

    # TODO: Extend this hard-coded list with dynamic "type:pattern" entries.
    # For example:
    #   2018_JUNE_09
    #   JUNE_09
    #   09
    #
    # In addition, the shorter *_9 (single digit vs double-digit single day)
    # should also be supported as a valid frequency.

    pass
