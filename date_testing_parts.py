#!/usr/bin/env python3

supported_date_patterns = [
    {
        # Full month name
        'format_string': '%B',
        'name': 'full_month_name'
    },
    {
        # Abbreviated month name
        'format_string': '%b',
        'name': 'abbrv_month_name'
    },
    {
        'format_string': '%y',
        'name': 'two_digit_year'
    },
    {
        'format_string': '%Y',
        'name': 'four_digit_year'
    },
    {
        'format_string': '%d',
        'name': 'two_digit_day'
    },
   {
        'format_string': '%d',
        'name': 'one_digit_day'

        # Flag that the result of the format_string operation needs to be
        # stripped of '_0' or '-0' values.
        'computed': True,
    },


    {
        'format_string': '%Y_%B_%d',
    },
    {
        'format_string': '%Y_%B_%d',
    },

]

# this_month_abbrv = date.strftime('%b')


# # zero-padded decimal number (01, 02, 03, ...)
# this_month_two_digit = date.strftime('%m')

# this_month_one_digit = date.strftime('%m').lstrip('0')

# # June, July, ...
# this_month_full_name = date.strftime('%B')

# # 09, 10, ...
# this_day_two_digit = date.strftime('%d')

# # 9, 10, ...
# this_day_one_digit = date.strftime('%d').lstrip('0')
