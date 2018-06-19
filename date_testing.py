#!/usr/bin/env python3

# Purpose: Prototype date keywords based off of specified date

import datetime
import logging
import logging.handlers
import pprint
import sys

supported_date_format_patterns = [

    # >>> d = {}
    # >>> d['dict1'] = {}
    # >>> d['dict1']['innerkey'] = 'value'
    # >>> d
    # {'dict1': {'innerkey': 'value'}}

        {'daily':{
            'display_string':'daily',
            'format_string':'%Y-%m-%d',
            }
        },
        # 'twice_week':TODAY,
        # 'weekly':TODAY,
        # 'weekly_monday':TODAY,
        # 'weekly_tuesday':TODAY,
        # 'weekly_wednesday':TODAY,
        # 'weekly_thursday':TODAY,
        # 'weekly_friday':TODAY,
        # 'weekly_saturday':TODAY,
        # 'weekly_sunday':TODAY,
        # 'twice_month':TODAY,
        # 'monthly':MONTH_YEAR,
        # 'twice_year':MONTH_YEAR,
        # 'quarterly':MONTH_YEAR,
        # 'yearly':YEAR

]


supported_date_format_strings = [
    # Four digit year
    '%Y_%m_%d',

    # Two digit year
    '%y_%m_%d',

    # Abbreviated month name
    '%y_%b_%d',
    '%b_%d',

    # Full month name
    '%y_%B_%d',
    '%B_%d',

]

def convert_provided_date_string(date_string):

    conversion_error = False

    # Any way to dynamically build this?
    for date_pattern in supported_date_format_strings:

        try:
            #>>> chosen_date = '2018-06-18'
            #>>> datetime.datetime.strptime(chosen_date, '%Y-%m-%d')
            #datetime.datetime(2018, 6, 18, 0, 0)

            # Try to convert the provided string to a datetime object
            date = datetime.datetime.strptime(date_string, date_pattern)
        except ValueError:
            # Try to convert using the next pattern
            conversion_error = True
            continue
        else:
            # return the first successful conversion
            return date

    if conversion_error:

        conversion_failure_message = \
            "Provided date value of {} does not match supported patterns ({})".format(
                date_string,
                supported_date_format_strings
            )
        # Raise exception to indicate that we failed to convert the
        # requested "date" string to a valid datetime object
        raise ValueError(conversion_failure_message)


def get_valid_date_patterns(date_string=datetime.date.today()):

    """
    Return valid date keywords for specified date. Uses current date if
    not supplied.
    """

    valid_date_patterns = []

    # TODO: What behavior should occur if we support YYYY-MM patterns?
    # Repeat the notification for every day that month?
    #
    #   >>> date = datetime.date.today()
    #   >>> date.strftime('%Y-%m')
    #   '2018-06'

    if date_string == datetime.date.today():

        # Looks like we're using the default argument of using a datetime
        # object using today's date.
        date = date_string
    else:
        try:
            date = convert_provided_date_string(date_string)
        except ValueError:

            # Fall back to using the current date if invalid value provided?
            # The ramifications are that notifications may be generated for
            # invalid dates. Things like "MUST DO THIS TODAY" could fire
            # months/years in advance. Probably better to fail?

            # Explicitly raise the error and let the caller deal with it
            # to indicate that the chosen date is invalid. Let the caller
            # try again (or give up as the situation demands)
            raise


    # Build valid date pattern "pieces" that we'll use to assemble supported
    # date keywords

    # this_month_abbrv = date.strftime('%b')

    # this_year_four_digit = date.strftime('%Y')
    # this_year_two_digit = date.strftime('%y')

    # # zero-padded decimal number (01, 02, 03, ...)
    # this_month_two_digit = date.strftime('%m')

    # this_month_one_digit = date.strftime('%m').lstrip('0')

    # # June, July, ...
    # this_month_full_name = date.strftime('%B')

    # # 09, 10, ...
    # this_day_two_digit = date.strftime('%d')

    # # 9, 10, ...
    # this_day_one_digit = date.strftime('%d').lstrip('0')

    # >>> datetime.datetime.strptime(chosen_date, '%Y%m%d')
    # Traceback (most recent call last):
    # File "<stdin>", line 1, in <module>
    # File "C:\Program Files\Python36\lib\_strptime.py", line 565, in _strptime_datetime
    #     tt, fraction = _strptime(data_string, format)
    # File "C:\Program Files\Python36\lib\_strptime.py", line 362, in _strptime
    #     (data_string, format))
    # ValueError: time data '2018-06-18' does not match format '%Y%m%d'

    # Build list of valid date keywords dynamically based off of
    # separate year, month and day patterns. Use 'set' to prevent
    # any duplicate items

    # month_patterns = set([
    #     this_month_abbrv,
    #     this_month_full_name,
    #     this_month_two_digit,
    #     this_month_one_digit
    # ])
    # month_patterns = list(month_patterns)
    # month_patterns.sort()

    # year_patterns = set([
    #     this_year_four_digit,
    #     this_year_two_digit
    # ])
    # year_patterns = list(year_patterns)
    # year_patterns.sort()

    # day_patterns = set([
    #     this_day_two_digit,
    #     this_day_one_digit
    # ])
    # day_patterns = list(day_patterns)
    # day_patterns.sort()

    # valid_date_patterns = []

    # for month_pattern in month_patterns:
    #     for year_pattern in year_patterns:
    #         for day_pattern in day_patterns:
    #             valid_date_patterns.append("{}-{}-{}".format(
    #                 year_pattern,
    #                 month_pattern,
    #                 day_pattern
    #             ))

    for format_string in supported_date_format_strings:


        date_keyword = date.strftime(format_string)
        date_keyword_single_digit_day_month = date_keyword.replace('_0', "_")
        date_keyword_single_digit_month_double_day = \
            date_keyword.replace('_0', "_", 1)

        valid_date_patterns.extend(
            [date_keyword,
            date_keyword_single_digit_day_month,
            date_keyword_single_digit_month_double_day]
        )

        valid_date_patterns.sort()

    return list(set(valid_date_patterns))




try:
    patterns = get_valid_date_patterns('2018-01-10')
    #patterns = get_valid_date_patterns()

# The function will attempt to convert the pattern found in the event
# db entry. If the conversion fails, a ValueError exception is thrown.
# In that case we do NOT wish to proceed as otherwise we could generate
# event notifications for events that are not scheduled to occur yet.
#
# TODO: Perhaps have an admin or error reporting address receive
# reports of invalid event entries? Perhaps that address could receive
# reports instead of the originally intended reminder address?
except ValueError as error:
    # log error

    print('Error converting requested date: {}'.format(error))
    pass
else:
    pprint.pprint(patterns)

