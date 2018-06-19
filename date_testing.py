#!/usr/bin/env python3

# Purpose: Prototype date keywords based off of specified date

import datetime
import logging
import logging.handlers
import pprint
import sys


default_date_format_string = '%Y-%m-%d'

base_supported_date_format_patterns = [

    {
        'format_string': default_date_format_string,
        'name':'daily',
    },
    {
        'format_string': default_date_format_string,
        'name': 'twice_week',
        'display_name': 'twice weekly',
    },
    {
        'format_string': default_date_format_string,
        'name':'weekly',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_monday',
        'display_name': 'every monday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_tuesday',
        'display_name': 'every tuesday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_wednesday',
        'display_name': 'every wednesday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_thursday',
        'display_name': 'every thursday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_friday',
        'display_name': 'every friday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_saturday',
        'display_name': 'every saturday',
    },
    {
        'format_string': default_date_format_string,
        'name': 'weekly_sunday',
        'display_name': 'every sunday',
    },
    {
        'format_string': default_date_format_string,
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
        # Full month name
        'format_string': '%B_%d',
    },
    {
        # Abbreviated month name
        'format_string': '%b_%d',
    },
    {
        'format_string': '%y_%b_%d',
    },
    {
        'format_string': '%Y_%b_%d',
    },
    {
        'format_string': '%y_%B_%d',
    },
    {
        'format_string': '%Y_%B_%d',
    },
]



def get_valid_format_strings(date_format_patterns):
    """
    Receives a list of dictionaries which specify valid format strings.
    Returns a list of the original format strings + variations of those
    strings in order to permit additional date formats that users may wish
    to use.
    """

    format_strings = []
    for pattern in date_format_patterns:

        # Create variations of format string to allow for additional supported
        # patterns. We need to add that support here instead of later as
        # additional supported keywords since these format strings are used
        # for conversion.
        #
        # TODO: Are we validating in two places?
        #
        format_strings.append(pattern['format_string'].replace('_', "-"))
        format_strings.append(pattern['format_string'].replace('-', "_"))
        format_strings.append(pattern['format_string'].replace(' ', "_"))
        format_strings.append(pattern['format_string'].replace(' ', "-"))

    # Toss duplicate entries
    format_strings = list(set(format_strings))
    format_strings.sort()

    return format_strings


def convert_provided_date_string(date_string):

    conversion_error = False

    format_strings = \
        get_valid_format_strings(base_supported_date_format_patterns)

    # Any way to dynamically build this?
    for format_string in format_strings:

        try:
            #>>> chosen_date = '2018-06-18'
            #>>> datetime.datetime.strptime(chosen_date, default_date_format_string)
            #datetime.datetime(2018, 6, 18, 0, 0)

            # Try to convert the provided string to a datetime object
            date = datetime.datetime.strptime(date_string, format_string)
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
                format_strings
            )
        # Raise exception to indicate that we failed to convert the
        # requested "date" string to a valid datetime object
        raise ValueError(conversion_failure_message)


def get_valid_date_patterns(date_string=datetime.date.today()):

    """
    Return valid date keywords for specified date. Uses current date if
    not supplied.
    """

    valid_format_strings = \
        get_valid_format_strings(base_supported_date_format_patterns)

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


    for format_string in valid_format_strings:

        date_keyword = date.strftime(format_string)
        date_keyword_single_digit_day_month = date_keyword.replace('_0', "_")
        date_keyword_single_digit_month_double_day = \
            date_keyword.replace('_0', "_", 1)

        valid_date_patterns.extend(
            [date_keyword,
            date_keyword_single_digit_day_month,
            date_keyword_single_digit_month_double_day]
        )

        valid_date_patterns = list(set(valid_date_patterns))
        valid_date_patterns.sort()

    return valid_date_patterns




try:
    #patterns = get_valid_date_patterns('2018-01-10')
    patterns = get_valid_date_patterns('2017-01-07')

    # Missing item from pattern (there may be others):
    #
    # * 17-Jan-7
    #
    #
    # ['17-Jan-07',
    # '17-January-07',
    # '17_Jan_07',
    # '17_Jan_7',
    # '17_January_07',
    # '17_January_7',
    # '2017',
    # '2017-01-07',
    # '2017-Jan-07',
    # '2017-January-07',
    # '2017_01_07',
    # '2017_1_07',
    # '2017_1_7',
    # '2017_Jan_07',
    # '2017_Jan_7',
    # '2017_January_07',
    # '2017_January_7',
    # 'Jan-07',
    # 'Jan_07',
    # 'Jan_7',
    # 'January 2017',
    # 'January-07',
    # 'January-2017',
    # 'January_07',
    # 'January_2017',
    # 'January_7']


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
