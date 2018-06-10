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
import logging
import logging.handlers
import os
import os.path
import sys


app_name = 'automated-tickets'

# TODO: Configure formatter to log function/class info
syslog_formatter = logging.Formatter('%(name)s - %(levelname)s - %(funcName)s - %(message)s')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')

# Grab root logger and set initial logging level
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# The SysLogHandler class, supports sending logging messages to a remote
# or local Unix syslog.
# TODO: Expose this value elsewhere; move to logging_config.json?
syslog_socket = '/dev/log'
try:
    syslog_handler = logging.handlers.SysLogHandler(address=syslog_socket)
except AttributeError:
    # We're likely running on Windows, so use the NullHandler here
    syslog_handler = logging.NullHandler
else:
    # Good thus far, finish configuring SysLogHandler
    syslog_handler.ident = app_name + ": "
    syslog_handler.setFormatter(syslog_formatter)
    syslog_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setFormatter(stdout_formatter)
# Apply lax logging level since we will use a filter to examine message levels
# and compare against allowed levels set within the main config file. This
# filter is added later once the settings config object has been constructed.
console_handler.setLevel(logging.NOTSET)

file_handler = logging.FileHandler(app_name + '.log', mode='a')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

# Create logger object that inherits from root and will be inherited by
# all modules used by this project
# Note: The console_handler is added later after the settings config object
# has been constructed.
app_logger = logging.getLogger(app_name)
app_logger.addHandler(syslog_handler)
app_logger.addHandler(file_handler)
app_logger.setLevel(logging.DEBUG)

log = app_logger.getChild(__name__)

log.debug("Logging initialized for %s", __name__)


# TODO: Setup support for reading in environmental variable value
# in place of hard-coding values here.
#
import automated_tickets_lib as atlib
##########################################################################


log.debug("Finished importing standard modules and our custom library modules.")

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
    choices=list(atlib.DATE_LABEL.keys())
)

# NOTE: Probably want to leave this as not required and fall back to checking
# for the config file in the same location as this script. If it is not found
# THEN we can throw an error.
parser.add_argument('--config_file', action='store', required=False)

try:
    log.info('Parsing commandline options')
    args = parser.parse_args()
except Exception as error:
    log.exception("Unable to parse command-line arguments: %s", error)
    sys.exit(1)

# NOTE: The command-line options parser enforces specific values and requires
# that at least one of those values is present.
event_schedule = args.event_schedule

# TODO: Confirm 'None' is correct fallback value
if args.config_file is not None:
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
log.debug(
    "Passing in these config file locations for evalution: %s",
    config_file_candidates)

log.info('Parsing config files')
settings = atlib.Settings(config_file_candidates)

# Now that the settings object has been properly created, lets use it to
# finish configuring console logging for the main application logger.
console_handler.addFilter(atlib.ConsoleFilterFunc(settings=settings))
app_logger.addHandler(console_handler)

# Troubleshooting config file flag boolean conversion
for key, value in list(settings.flags.items()):
    log.debug("key: '%s' value: '%s' type of value: '%s'",
        key,
        value,
        type(value))

if settings.flags['testing_mode']:
    log.warning("Test warning message to prove that the INI flag works")
    log.error("Test error message to prove that the INI flag works")

# Generate list of matching events from database based on requested event
# schedule (daily, weekly, etc.)
events = []

log.info('Retrieving events')
events = atlib.get_events(settings, event_schedule)

message = {}

for event in events:

    # FIXME: Perform string substitution on object instantiation where all
    # validity checks can be grouped together. This can simply be a reference
    # to those pre-computed values.
    # FIXME: Reintroduce support for multiple destination email addresses
    message['subject'] = "{} ({})".format(
        # Formatting the prefix string before then using the result in
        # the larger format string we're building here
        # NOTE: Explicitly lowering the case of the dictionary key values
        # pulled from the events table entry in order to properly reference
        # the associated value.
        # FIXME: Add try/except blocks around expansion so that any KeyError
        # exceptions can be caught and processing can continue.
        event.email_subject_prefix.format(atlib.DATE_LABEL[event.event_schedule].lower()),
        event.event_schedule.lower()
    )
    message['envelope'] = "From: {}\nTo: {}\nSubject: {}\n".format(
        event.email_from_address, event.email_to_address, message['subject']
        )

    log.debug("Email envelope details: %s", message['envelope'])

    # If this task has a known due date ...
    if event.redmine_new_issue_due_date:
        log.debug("Due date of %s is set for task: %s",
            event.redmine_new_issue_due_date,
            message['subject'])

        message['footer'] = "\nProject: {}\nCategory: {}\nStatus: {}\nPriority: {}\nDue date: {}\n".format(
            event.redmine_new_issue_project,
            event.redmine_new_issue_category,
            event.redmine_new_issue_status,
            event.redmine_new_issue_priority,
            event.redmine_new_issue_due_date
        )
    else:
        log.debug("No due date set for %s", message['envelope'])
        message['footer'] = "\nProject: {}\nCategory: {}\nStatus: {}\nPriority: {}\n".format(
            event.redmine_new_issue_project,
            event.redmine_new_issue_category,
            event.redmine_new_issue_status,
            event.redmine_new_issue_priority
        )

    log.debug("Fetching initial wiki page contents for page %s from project %s",
        event.redmine_wiki_page_name,
        event.redmine_wiki_page_project_shortname)

    # Get the raw contents of the wiki page associated with the event
    wiki_page_contents = atlib.get_wiki_page_contents(
        settings,
        event.redmine_wiki_page_name,
        event.redmine_wiki_page_project_shortname,
        settings.mysqldb_config['redmine_database']
    )


    # Optionally expand any include macro calls so that a full expanded
    # (dependency free) page is used as the body of the message
    if settings.flags['expand_include_macros_in_wiki_pages']:

        log.debug("Enabled: Expand include macros found in wiki pages")
        # Check wiki_page_contents for include macro calls and build a
        # list of included pages to fetch the content from.
        wiki_page_macro_calls = []
        wiki_page_macro_calls = atlib.get_include_calls(
            wiki_page_contents,
            event.redmine_wiki_page_project_shortname
            )

        log.debug("Include calls found: %s", bool(wiki_page_macro_calls))

        # TODO: used in a strictly boolean context; from PEP8:
        # For sequences, (strings, lists, tuples), use the fact that
        # empty sequences are false
        while wiki_page_macro_calls:

            log.debug("Wiki page include macro calls found: %s",
                wiki_page_macro_calls)

            # proceed with getting the list of included pages
            log.debug("Fetching included wiki pages ...")
            included_wiki_pages = []
            included_wiki_pages = atlib.get_included_wiki_pages(
                wiki_page_macro_calls,
                event.redmine_wiki_page_project_shortname)

            # for every included page, lets grab the contents
            while included_wiki_pages:
                wiki_page_to_process = included_wiki_pages.pop()


                log.debug("Fetching wiki page contents for included page %s from project %s",
                    wiki_page_to_process,
                    event.redmine_wiki_page_project_shortname)

                included_wiki_page_contents = atlib.get_wiki_page_contents(
                    settings,
                    wiki_page_to_process,
                    event.redmine_wiki_page_project_shortname,
                    settings.mysqldb_config['redmine_database'])

                # At this point we have a page name which was included by the
                # initial page and we also have the contents of that page
                search_value = '{{include(%s:%s)}}' % (
                    event.redmine_wiki_page_project_shortname,
                    wiki_page_to_process)

                log.debug("Search string for include call: %s", search_value)

                wiki_page_contents = wiki_page_contents.replace(search_value, included_wiki_page_contents)

            # After we have processed all initial include pages, check again to
            # see if pulling in the content from those included pages resulted
            # in us finding more include macro calls.
            log.debug("Parsing wiki page contents for further include calls ...")
            wiki_page_macro_calls = atlib.get_include_calls(
                wiki_page_contents,
                event.redmine_wiki_page_project_shortname
                )
    else:
        log.debug("Disabled: Expand include macros found in wiki pages")
        log.debug("Redmine will substitute macros with live include page contents")

    # Use wiki page contents as the message body. This is either the fully
    # expanded content after include macro calls have been processed or the
    # original page content if the expansion option has been disabled in the
    # automated_tickets.ini config file.
    message['body'] = wiki_page_contents


    # FIXME: Revisit this?
    log.debug("FIXME: Leaving header empty")
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
    log.info('Sending email notification')
    atlib.send_notification(settings, event.email_from_address, event.email_to_address, email_message)

# Informs the logging system to perform an orderly shutdown by flushing and
# closing all handlers.
logging.shutdown()
