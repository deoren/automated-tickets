#!/usr/bin/env python3

# Purpose: Prototype date keywords based off of specified date

import datetime
import logging
import logging.handlers
import pprint
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

    this_month_abbrv = date.strftime('%b')

    this_year_four_digit = date.strftime('%Y')
    this_year_two_digit = date.strftime('%y')

    # zero-padded decimal number (01, 02, 03, ...)
    this_month_two_digit = date.strftime('%m')

    this_month_one_digit = date.strftime('%m').lstrip('0')

    # June, July, ...
    this_month_full_name = date.strftime('%B')

    # 09, 10, ...
    this_day_two_digit = date.strftime('%d')

    # 9, 10, ...
    this_day_one_digit = date.strftime('%d').lstrip('0')

    # JUNE_09
    #
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

    #
    # TODO: Can I build the entries dynamically with inner/outer loops?
    #
    #
    #   year (four digit, two digit)
    #   month (fullname, abbrv, two digit, one digit)
    #   day (two digit, one digit)


    # 2018_JUNE_09
    date_yyyy_month_dd = "{}_{}_{}".format(
        this_year_four_digit,
        this_month_full_name,
        this_day_two_digit
    )

    # 2018_JUNE_9
    date_yyyy_month_d = "{}_{}_{}".format(
        this_year_four_digit,
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yyyy_month_d)

    # 18_JUNE_09
    date_yy_month_dd = "{}_{}_{}".format(
        this_year_two_digit,
        this_month_full_name,
        this_day_two_digit
    )
    valid_date_patterns.append(date_yy_month_dd)

    # 18_JUNE_9
    date_yy_month_d = "{}_{}_{}".format(
        this_year_two_digit,
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yy_month_d)

    # JUNE_09
    date_month_dd = "{}_{}".format(
        this_month_full_name,
        this_day_two_digit
    )
    valid_date_patterns.append(date_month_dd)

    # JUNE_9
    date_month_d = "{}_{}".format(
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_month_d)


    ######################################
    # numeric patterns
    ######################################

    # 2018_06_09
    date_yyyy_mm_dd = "{}_{}_{}".format(
        this_year_four_digit,
        this_month_two_digit,
        this_day_two_digit
    )
    valid_date_patterns.append(date_yyyy_mm_dd)

    # 2018_06_9
    date_yyyy_mm_d = "{}_{}_{}".format(
        this_year_four_digit,
        this_month_two_digit,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yyyy_mm_d)

    # 2018_6_9
    date_yyyy_m_d = "{}_{}_{}".format(
        this_year_four_digit,
        this_month_one_digit,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yyyy_m_d)

    # 18_06_09
    date_yy_mm_dd = "{}_{}_{}".format(
        this_year_two_digit,
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yy_mm_dd)

    # 18_06_9
    date_yy_mm_d = "{}_{}_{}".format(
        this_year_two_digit,
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yy_mm_d)

    # 18_6_9
    date_yy_m_d = "{}_{}_{}".format(
        this_year_two_digit,
        this_month_full_name,
        this_day_one_digit
    )
    valid_date_patterns.append(date_yy_m_d)

    pass

#date = datetime.date.today()
    #>>> chosen_date = '2018-06-18'
    #>>> datetime.datetime.strptime(chosen_date, '%Y-%m-%d')
    #datetime.datetime(2018, 6, 18, 0, 0)

chosen_date = '2018-06-09'
date = datetime.datetime.strptime(chosen_date, '%Y-%m-%d')


this_month_abbrv = date.strftime('%b')

this_year_four_digit = date.strftime('%Y')
this_year_two_digit = date.strftime('%y')

# zero-padded decimal number (01, 02, 03, ...)
this_month_two_digit = date.strftime('%m')

this_month_one_digit = date.strftime('%m').lstrip('0')

# June, July, ...
this_month_full_name = date.strftime('%B')

# 09, 10, ...
this_day_two_digit = date.strftime('%d')

# 9, 10, ...
this_day_one_digit = date.strftime('%d').lstrip('0')

month_patterns = set([
    this_month_abbrv,
    this_month_full_name,
    this_month_two_digit,
    this_month_one_digit
])
month_patterns = list(month_patterns)
month_patterns.sort()

year_patterns = set([
    this_year_four_digit,
    this_year_two_digit
])
year_patterns = list(year_patterns)
year_patterns.sort()

day_patterns = set([
    this_day_two_digit,
    this_day_one_digit
])
day_patterns = list(day_patterns)
day_patterns.sort()

#pprint.pprint(year_patterns)
#pprint.pprint(month_patterns)
#pprint.pprint(day_patterns)

valid_date_patterns = []

for month_pattern in month_patterns:
    for year_pattern in year_patterns:
        for day_pattern in day_patterns:
            valid_date_patterns.append("{}-{}-{}".format(
                year_pattern,
                month_pattern,
                day_pattern
            ))

valid_date_patterns.sort()

pprint.pprint(valid_date_patterns)
