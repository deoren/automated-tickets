#!/usr/bin/env python3

# Purpose: Prototype date keywords based off of specified date

import datetime
import logging
import logging.handlers
import pendulum
import pprint
import sys

# Timezone of the server hosting this script
# TODO: Set this automatically based on OS setting
our_timezone = 'America/Chicago'

default_date_format_string = 'YYYY-MM-DD'

# Pre-defined static keywords that directly correspond to keyword references
# within the provided cron.d file. Limited number, primarily for common
# reoccuring patterns.
static_supported_date_format_patterns = [

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
        'format_string': 'MMMM YYYY',
        'name':'monthly',
    },
    {
        'format_string': 'MMMM YYYY',
        'name': 'twice_year',
        'display_name': 'twice yearly',
    },
    {
        'format_string': 'MMMM YYYY',
        'name':'quarterly',
    },
    {
        # TODO: This one is going to be problematic.
        'format_string': 'YYYY',
        'name':'yearly',
    },
    # End stock keywords
]

dynamic_supported_date_format_patterns = [

    # Full year
    {
        'format_string': 'YYYY_MMMM_DD',
    },
    {
        'format_string': 'YYYY_MMM_DD',
    },
    {
        'format_string': 'YYYY_MM_DD',
    },
    {
        'format_string': 'YYYY_M_DD',
    },

    {
        'format_string': 'YYYY_MMMM_D',
    },
    {
        'format_string': 'YYYY_MMM_D',
    },
    {
        'format_string': 'YYYY_MM_D',
    },
    {
        'format_string': 'YYYY_M_D',
    },

    # Partial year
    {
        'format_string': 'YY_MMMM_DD',
    },
    {
        'format_string': 'YY_MMM_DD',
    },
    {
        'format_string': 'YY_MM_DD',
    },
    {
        'format_string': 'YY_M_DD',
    },

    {
        'format_string': 'YY_MMMM_D',
    },
    {
        'format_string': 'YY_MMM_D',
    },
    {
        'format_string': 'YY_MM_D',
    },
    {
        'format_string': 'YY_M_D',
    },

    # Full month name
    {

        'format_string': 'MMMM_DD',
    },
    {
        'format_string': 'MMMM_D',
    },

    # Abbreviated month name
    {
        'format_string': 'MMM_DD',
    },
    {
        'format_string': 'MMM_D',
    },


]



# TODO: Append to the original list/dictionary structure instead of
# creating a separate list. Perhaps create objects instead?
def get_valid_format_strings(date_format_patterns=dynamic_supported_date_format_patterns):
    """
    Receives a list of dictionaries which specify valid format strings to be
    used for dynamically generating date keywords.

    Returns a list of the original format strings + variations of those
    strings in order to permit additional date formats that users may wish
    to use.
    """

    format_strings = []

    for pattern in date_format_patterns:

        # Create variations of format string to allow support for both
        # underscores as well as dashes.
        format_strings.append(pattern['format_string'])
        format_strings.append(pattern['format_string'].replace('_', "-"))

    # Toss any duplicates
    format_strings = list(set(format_strings))
    format_strings.sort()

    return format_strings


def convert_provided_date_string(date_string):

    conversion_error = False

    format_strings = get_valid_format_strings()

    for format_string in format_strings:

        try:
            date = pendulum.from_format(
                date_string,
                format_string,
                tz=our_timezone,
                locale="en")
        except ValueError as error:
            # Try to convert using the next pattern
            print("Failed to convert {} using {} format code: {}".format(
                date_string,
                format_string,
                error
            ))
            conversion_error = True
            continue
        else:
            # return the first successful conversion
            print("{} was converted from format string {} and is of type {}".format(
                date,
                format_string,
                type(date)
                ))
            print(date.year)
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

def get_valid_static_keywords(static_keywords=static_supported_date_format_patterns):
    """
    Utility function to return a list of pre-defined static keywords that
    directly correspond to keyword references within the provided cron.d
    file.
    """

    # TODO: Validation?
    return static_keywords


def get_valid_date_keywords(date_string=pendulum.today(),
    date_format_patterns=dynamic_supported_date_format_patterns):

    """
    Return valid date keywords for specified date. Uses current date if
    not supplied.
    """

    valid_format_strings = get_valid_format_strings()

    valid_date_keywords = []

    # TODO: What behavior should occur if we support YYYY-MM patterns?
    # Repeat the notification for every day that month?
    #
    #   >>> date = datetime.date.today()
    #   >>> date.strftime('%Y-%m')
    #   '2018-06'

    # Check to see if we're using the default DateTime function argument
    if isinstance(date_string, pendulum.DateTime):

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

        date_keyword = date.format(format_string)
        valid_date_keywords.append(date_keyword)

        # Throw away any duplicates, sort what remains
        valid_date_keywords = list(set(valid_date_keywords))
        valid_date_keywords.sort()

        # Force all keywords to upper case for consistency
        valid_date_keywords = [x.upper() for x in valid_date_keywords]
    return valid_date_keywords




try:
    #patterns = get_valid_date_keywords('2018-01-10')
    #dynamic_keywords = get_valid_date_keywords('2017-01-07')
    dynamic_keywords = get_valid_date_keywords()
    #dynamic_keywords = get_valid_date_keywords('02-03-04')

# The function will attempt to convert the pattern found in the event
# db entry. If the conversion fails, a ValueError exception is thrown.
# In that case we do NOT wish to proceed as otherwise we could generate
# event notifications for events that are not scheduled to occur yet.
#
# TODO: Perhaps have an admin or error reporting address receive
# reports of invalid event entries? Perhaps that address could receive
# reports instead of the originally intended reminder address?
except ValueError as error:
    print('Error converting requested date: {}'.format(error))
else:
    print("List of dynamic keywords:")
    pprint.pprint(dynamic_keywords)




try:
    static_keywords = \
        get_valid_static_keywords(static_supported_date_format_patterns)
except ValueError as error:
    # log error
    print('Error retrieving static keywords: {}'.format(error))
else:
    print("List of static keywords:")
    pprint.pprint(static_keywords)


sys.exit()

#for i in range(0, my_list_len):
for date_pattern in dynamic_supported_date_format_patterns:

    # This is where some logic can be used to dynamically calculate
    # the display value to the current day's date if it's not already
    # explicitly set.
    if 'display_name' in date_pattern:
        display_name = date_pattern['display_name']
    else:
        display_name = ''

    # Only the baked-in keywords have a "name" key/value entry
    if 'name' in date_pattern:
        name = date_pattern['name']
    else:
        # Would we also dynamically generate a name here?
        name = ''

    #print("date pattern is {}".format(date_pattern))
    print("pattern {} format string: {}, display name: {}".format(
        name,
        date_pattern['format_string'],
        display_name
        ))
