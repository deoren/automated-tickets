#!/usr/bin/env python3

"""
Purpose: Parse collection of events and generate notifications for any events
matching the requested schedule.
"""



#######################################################
# Module Imports
#######################################################

#
# Standard Library
#

# parse command line arguments, 'sys.argv'
import argparse

import os
import os.path
import sys




##########################################################################
# This controls output display prior to user configurable values
# being read in and honored. Uncomment and disable/enable as needed
# for debugging purposes
#automated_tickets_lib.DISPLAY_DEBUG_MESSAGES = True
#automated_tickets_lib.DISPLAY_INFO_MESSAGES = True
#automated_tickets_lib.DISPLAY_WARNING_MESSAGES = True
#automated_tickets_lib.DISPLAY_ERROR_MESSAGES = True
#
# Basic import so that we can manipulate global variables
import automated_tickets_lib
##########################################################################



# Our custom classes
from automated_tickets_lib import Settings

# Consants
from automated_tickets_lib import DATE_LABEL

# Our custom "print" fuctions
from automated_tickets_lib import print_debug, print_error, print_info, print_warning

from automated_tickets_lib import get_events, get_wiki_page_contents, send_notification

from automated_tickets_lib import get_include_calls, get_included_wiki_pages


########################################################
# Collect command-line arguments passed by Cron
########################################################

parser = argparse.ArgumentParser(
    description='Check for applicable events and generate notices for matches'
    )

# This will need to be broken up later by the script
parser.add_argument(
    '--event_schedule',
    action='store',
    required=True,

    # Reuse keys from DATE_LABEL dict in library file instead of repeating here
    choices=list(DATE_LABEL.keys())
)

# NOTE: Probably want to leave this as not required and fall back to checking
# for the config file in the same location as this script. If it is not found
# THEN we can throw an error.
parser.add_argument('--config_file', action='store', required=False)

try:
    args = parser.parse_args()
except Exception as e:
    print_error("Unable to parse command-line arguments: {}".format(e), "argparse")
    sys.exit(1)

# NOTE: The command-line options parser enforces specific values and requires
# that at least one of those values is present.
event_schedule = args.event_schedule

if args.config_file:
    global_config_file = args.config_file
else:
    # FIXME:
    # The configuration parser will skip over requests for
    # non-existant files, so it SHOULD be safe for now to
    # set this location to an empty string.
    global_config_file = ""


#######################################################
# CONSTANTS - Modify INI config files instead
#######################################################

# Where this script is being called from. We will try to load local copies of all
# dependencies from this location first before falling back to default
# locations in order to support having all of the files bundled together for
# testing and portable use.
script_path = os.path.dirname(os.path.realpath(__file__))

# The name of this script. It is used as needed by error/debug messages
script_name = os.path.basename(sys.argv[0])

# Read in configuration file. Attempt to read local copy first, then
# fall back to using the copy specified on the command-line. We have
# hard-coded the name of the local file, but the user is free to specify
# a custom name/path using the command-line option.

config_file = {}
config_file['name'] = 'automated_tickets.ini'
config_file['local'] = os.path.join(script_path, config_file['name'])

# This location is (optionally) specified on the command-line. If it is not
# specified, then an empty string is set instead. The Settings class will
# confirm the file is actually present and complain if it is not.
config_file['global'] = global_config_file

# Prefer a local copy over a "global" one by loading it last (where the
# second config file overrides or "shadows" settings from the first). If
# a local copy does not exist, then the one specified on the command-line
# will be used. If that one does not exist, then this script will throw
# an error and quit.
config_file_candidates = [config_file['global'], config_file['local']]

# Generate configuration setting options
print_debug(
    "Passing in these config file locations for evalution: {}".format(
        config_file_candidates), "CONFIG")

settings = Settings(config_file_candidates)

# Controls status messages for each minor step of the process
# (e.g., pulling data, writing data, what flags are enabled, etc.)
DISPLAY_DEBUG_MESSAGES = settings.flags['display_debug_messages']
automated_tickets_lib.DISPLAY_DEBUG_MESSAGES = DISPLAY_DEBUG_MESSAGES

# Controls status messages for each major block
# (e.g., finishing table updates, reporting rows affected, etc.)
DISPLAY_INFO_MESSAGES = settings.flags['display_info_messages']
automated_tickets_lib.DISPLAY_INFO_MESSAGES = DISPLAY_INFO_MESSAGES

DISPLAY_WARNING_MESSAGES = settings.flags['display_warning_messages']
automated_tickets_lib.DISPLAY_WARNING_MESSAGES = DISPLAY_WARNING_MESSAGES

DISPLAY_ERROR_MESSAGES = settings.flags['display_error_messages']
automated_tickets_lib.DISPLAY_ERROR_MESSAGES = DISPLAY_ERROR_MESSAGES



# Troubleshooting config file flag boolean conversion
for key, value in list(settings.flags.items()):
    print_debug("key: '{}' value: '{}' type of value: '{}'".format(key, value, type(value)), "MySQL")


# Generate list of matching events from database based on requested event
# schedule (daily, weekly, etc.)
events = []
events = get_events(settings, event_schedule)

message = {}

for event in events:

    # FIXME: Perform string substitution on object instantiation where all
    # validity checks can be grouped together. This can simply be a reference
    # to those pre-computed values.
    # FIXME: Reintroduce support for multiple destination email addresses
    message['envelope'] = "From: {}\nTo: {}\nSubject: {} ({})\n".format(
        event.email_from_address, event.email_to_address,

        # Formatting the prefix string before then using the result in
        # the larger format string we're building here
        # NOTE: Explicitly lowering the case of the dictionary key values
        # pulled from the events table entry in order to properly reference
        # the associated value.
        # FIXME: Add try/except blocks around expansion so that any KeyError
        # exceptions can be caught and processing can continue.
        event.email_subject_prefix.format(DATE_LABEL[event.event_schedule].lower()),
        event.event_schedule.lower()
        )

    print_debug(message['envelope'], "Email envelope details")

    # If this task has a known due date ...
    if event.redmine_new_issue_due_date:
        message['footer'] = "\nProject: {}\nCategory: {}\nStatus: {}\nPriority: {}\nDue date: {}\n".format(
            event.redmine_new_issue_project,
            event.redmine_new_issue_category,
            event.redmine_new_issue_status,
            event.redmine_new_issue_priority,
            event.redmine_new_issue_due_date
        )
    else:
        message['footer'] = "\nProject: {}\nCategory: {}\nStatus: {}\nPriority: {}\n".format(
            event.redmine_new_issue_project,
            event.redmine_new_issue_category,
            event.redmine_new_issue_status,
            event.redmine_new_issue_priority
        )

    # Get the raw contents of the wiki page associated with the event
    wiki_page_contents = get_wiki_page_contents(
        settings,
        event.redmine_wiki_page_name,
        event.redmine_wiki_page_project_shortname,
        settings.mysqldb_config['redmine_database']
    )


    # Optionally expand any include macro calls so that a full expanded
    # (dependency free) page is used as the body of the message
    if settings.flags['expand_include_macros_in_wiki_pages']:

        # Check wiki_page_contents for include macro calls and build a
        # list of included pages to fetch the content from.
        wiki_page_macro_calls = get_include_calls(
            wiki_page_contents,
            event.redmine_wiki_page_project_shortname
            )

        while wiki_page_macro_calls:

            print_debug(wiki_page_macro_calls)

            # proceed with getting the list of included pages
            included_wiki_pages = []
            included_wiki_pages = get_included_wiki_pages(
                wiki_page_macro_calls,
                event.redmine_wiki_page_project_shortname)

            # for every included page, lets grab the contents
            while included_wiki_pages:
                wiki_page_to_process = included_wiki_pages.pop()

                included_wiki_page_contents = get_wiki_page_contents(
                    settings,
                    wiki_page_to_process,
                    event.redmine_wiki_page_project_shortname,
                    settings.mysqldb_config['redmine_database'])

                # At this point we have a page name which was included by the
                # initial page and we also have the contents of that page
                search_value = '{{include(%s:%s)}}' % (
                    event.redmine_wiki_page_project_shortname,
                    wiki_page_to_process)

                print_debug(search_value, "Search string for include call")

                wiki_page_contents = wiki_page_contents.replace(search_value, included_wiki_page_contents)

            # After we have processed all initial include pages, check again to
            # see if pulling in the content from those included pages resulted
            # in us finding more include macro calls.
            wiki_page_macro_calls = get_include_calls(
                wiki_page_contents,
                event.redmine_wiki_page_project_shortname
                )


    # Use wiki page contents as the message body. This is either the fully
    # expanded content after include macro calls have been processed or the
    # original page content if the expansion option has been disabled in the
    # automated_tickets.ini config file.
    message['body'] = wiki_page_contents


    # FIXME: Revisit this?
    message['header'] = ""

    # Note:
    #
    #  The spacing should be EXACTLY as shown here. Having one space
    #  between the envelope and header content results in Redmine adding
    #  header values (Message-Id for example) directly into the OP
    email_message = "{}{}\n{}\n{}\n".format(
        message['envelope'],
        message['header'],
        message['body'],
        message['footer']
    )

    # Send notification
    send_notification(settings, event.email_from_address, event.email_to_address, email_message)

