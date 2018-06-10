#!/usr/bin/env python3

"""
Library module used by the automated_tickets.py script. Not intended for direct use.
"""

# TODO: Consider adding a hook to each function to provide this value
# for debug output (troubleshooting)
# name_of_this_function = sys._getframe().f_code.co_name


########################################
# Modules - Standard Library
########################################

import configparser
import datetime
import logging
import logging.handlers
import os
import re
import smtplib
import sys


if __name__ == "__main__":
    sys.exit("This module is meant to be imported, not executed directly.")

########################################
# Modules - Library/config settings
########################################

app_name = 'automated-tickets'

# Create module-level logger object that inherits from "app" logger settings
log = logging.getLogger(app_name).getChild(__name__)

# TODO: How to mute messages from this library module by default?
# TODO: Set NullHandler
# log.addHandler(logging.NullHandler)

log.debug("Logging initialized for %s", __name__)


########################################
# Modules - Third party
########################################

# Upstream module, actively maintained and official recommendation
# of the MariaDB project (per their documentation).
# Available via OS packages (including apt repo) or pip.
#
# Examples:
#
# * sudo apt-get install mysql-connector-python
# * pip install mysql-connector-python --user
log.debug("Attempting to import mysql.connector module")
import mysql.connector as mysql


#######################################################
# Variables, constants
#######################################################


DATE = datetime.date.today()
TODAY = DATE.strftime('%Y-%m-%d')


# TODO: Am I using these or SQL generated date values?
date = datetime.date.today()
WEEK = date.strftime('week %U')
WEEK_YEAR = date.strftime('week %U, %Y')
MONTH = date.strftime('%B')
MONTH_YEAR = date.strftime('%B %Y')
YEAR = date.strftime('%Y')

# NOTE: If we use datetime.date.today() or date as set above
# we will get the same result as what we're doing here
TODAY = date.strftime('%Y-%m-%d')

# These entries serve both as a mapping of display formats and also as
# valid parameter values. For example, when daily events are requested,
# active daily events will result in notifications generated which have
# subject lines that include the value that is paired with the keyword below.
DATE_LABEL = {
    'daily':TODAY,
    'twice_week':TODAY,
    'weekly':TODAY,
    'weekly_monday':TODAY,
    'weekly_tuesday':TODAY,
    'weekly_wednesday':TODAY,
    'weekly_thursday':TODAY,
    'weekly_friday':TODAY,
    'weekly_saturday':TODAY,
    'weekly_sunday':TODAY,
    'twice_month':TODAY,
    'monthly':MONTH_YEAR,
    'twice_year':MONTH_YEAR,
    'quarterly':MONTH_YEAR,
    'yearly':YEAR
}


# TODO: Extend this hard-coded list with dynamic "type:pattern" entries.
# For example:
#   2018_JUNE_09
#   JUNE_09
#   09
#
# In addition, the shorter *_9 (single digit vs double-digit single day)
# should also be supported as a valid frequency.


#######################################################
# Classes
#######################################################

class Event(object):
    """
    Represents an event from the event_reminders table
    """

    def __init__(self, event):

        self.log = log.getChild(self.__class__.__name__)

        self.log.debug("%s class, input tuple: %s", __class__, event)

        #log.warning("Test warning message to prove that the INI flag works")
        #log.error("Test error message to prove that the INI flag works")


        # Expand out incoming tuple without hard-coding specific index values
        (self.email_to_address,
         self.email_from_address,
         self.email_subject_prefix,
         self.redmine_wiki_page_name,
         self.redmine_wiki_page_project_shortname,
         self.redmine_new_issue_project,
         self.redmine_new_issue_category,
         self.redmine_new_issue_status,
         self.redmine_new_issue_due_date,
         self.redmine_new_issue_priority,
         self.event_schedule
        ) = event

        self.log.debug("%s: new instance of object created", __class__)


class Settings(object):

    """
    Represents the user configurable settings retrieved from
    an external config file
    """

    def __init__(self, config_file_list):

        self.log = log.getChild(self.__class__.__name__)

        try:
            parser = configparser.SafeConfigParser()

            # Enable Extended Interpolation - allow values from one section
            # to be referenced from another section.
            parser._interpolation = configparser.ExtendedInterpolation()

            # Attempt to read and parse a list of filenames, returning a list
            # of filenames which were successfully parsed. If none of the
            # filenames exist, the configparser instance will contain an empty
            # dataset.
            processed_files = parser.read(config_file_list)

            self.log.debug("CONFIG: Config files processed: %s", processed_files)

            # FIXME: We can either pass a verified list of files to the parser
            # OR we can verify the number of processed files is 1 or greater.
            if len(processed_files) < 1:

                # Just raise the standard parsing error exception instead
                # of trying to handle a missing file differently than one
                # with parsing errors. We may change this later if found
                # to be too confusing.
                raise configparser.ParsingError(config_file_list)

        except configparser.ParsingError as error:
            self.log.exception("Unable to parse config file: %s", error)
            sys.exit(1)


        # Begin building object by creating dictionary member attributes
        # from config file sections/values.

        self.flags = {}
        self.mysqldb_config = {}
        self.queries = {}

        # Likely will be removed at some point
        self.notification_servers = {}

        # Not directly referenced yet, but exposing for future use
        self.email = {}

        try:
            # Grab all values from section as tuple pairs and convert
            # to dictionaries for easy reference

            # Not directly referenced yet, but exposing for future use
            self.email = dict(parser.items('email'))

            self.flags = dict(parser.items('flags'))
            self.mysqldb_config = dict(parser.items('mysqldb_config'))
            self.queries = dict(parser.items('queries'))

            # FIXME: This name will likely need adjusting later
            # to match whatever new section name is chosen for the config file
            self.notification_servers = dict(parser.items('notification_servers'))

            # FIXME: Is there a better to handle this?
            # This is a one-off boolean flag from a separate section
            self.mysqldb_config['raise_on_warnings'] = \
                parser.getboolean('mysqldb_config', 'raise_on_warnings')

            # Convert text "boolean" flag values to true boolean values
            for key in self.flags:
                self.flags[key] = parser.getboolean('flags', key)

                self.log.debug("%s has a value of %s and a type of %s",
                    key,
                    self.flags[key],
                    type(self.flags[key]))

        except configparser.NoSectionError as error:

            self.log.exception("Unable to parse config file: %s", error)
            sys.exit(1)

# Honor boolean flags set within main script config file and only
# output specific log levels to the console.
class ConsoleFilterFunc(logging.Filter):
    def __init__(self, settings):
        self.settings = settings
        #print("Just proving that this function is being called")
    def filter(self, record):
        if self.settings.flags['display_console_error_messages'] and record.levelname == 'ERROR':
            #print("Error messages enabled")
            return True
        if self.settings.flags['display_console_warning_messages'] and record.levelname == 'WARNING':
            #print("Warning messages enabled")
            return True
        if self.settings.flags['display_console_info_messages'] and record.levelname == 'INFO':
            #print("Info messages enabled")
            return True
        if self.settings.flags['display_console_debug_messages'] and record.levelname == 'DEBUG':
            #print("Debug messages enabled")
            return True
        else:
            #print("No matches")
            return False

#######################################################
# Functions
#######################################################

# TODO: Merge this function since we probably do not need a separate function
# for this.
def open_db_connection(settings, database):

    """
    Open a connection to the database and return a cursor object
    """


    ####################################################################
    # Open connections to databases
    ####################################################################

    try:

        log.debug("DB User: %s", settings.mysqldb_config["user"])
        log.debug("DB Name: %s", database)
        log.debug("DB Host Name/IP: %s", settings.mysqldb_config["host"])
        log.debug("DB Host Port: %s", settings.mysqldb_config["port"])
        log.debug("MySQL - raise_on_warnings: %s",
            settings.mysqldb_config["raise_on_warnings"])
        log.debug("MySQL - raise_on_warnings type: %s",
            type(settings.mysqldb_config["raise_on_warnings"]))

        log.info("Connecting to %s database on %s at port %s",
            database,
            settings.mysqldb_config["host"],
            settings.mysqldb_config["port"])

        mysql_connection = mysql.connect(
            user=settings.mysqldb_config['user'],
            password=settings.mysqldb_config['password'],
            host=settings.mysqldb_config['host'],
            port=settings.mysqldb_config['port'],
            database=database,
            raise_on_warnings=settings.mysqldb_config['raise_on_warnings']
        )

    except mysql.Error as error:
        log.exception("Unable to connect to database: %s", error)
        sys.exit(1)

    return mysql_connection


def get_wiki_page_contents(settings, wiki_page_name, wiki_page_project, wiki_page_database):

    """
    Retrieve contents of the specified Redmine wiki page for inclusion in notification
    """

    ####################################################################
    # Create cursor object so that we can interact with the database
    ####################################################################

    # TODO: Where is the cursor/connection closed/released?
    log.info('Opening connection to database')
    mysql_connection = open_db_connection(settings, wiki_page_database)

    # Cursor for the MySQL copy of the database
    mysql_cursor = mysql_connection.cursor()

    # Dynamically create the select query used to pull data from MySQL table
    # See automated_tickets.ini for the available queries
    try:

        # We're filtering events on the event schedule (daily, monthly etc.)
        # and also on whether the event is an intern task AND whether the
        # configuration file has enabled processing those tasks.

        query = settings.queries['wiki_page_contents'].format(
            wiki_page_name, wiki_page_project)

        log.debug("Wiki page retrieval query: %s", query)

        log.info('Executing query')
        mysql_cursor.execute(query)

    except Exception as error:
        log.exception("Unable to execute wiki page retrieval query: %s", error)
        sys.exit(1)

    try:
        # Grab first element of returned tuple, ignore everything else
        wiki_page_content = mysql_cursor.fetchone()[0]

    except Exception as error:
        # FIXME: Is there a Plan B for wiki page lookup failures?
        log.exception("Unable to retrieve wiki page content: %s", error)
        sys.exit(1)
    finally:
        log.debug("Closing cursor ...")
        mysql_cursor.close()

        log.debug("Closing connection ...")
        mysql_connection.close()

    if wiki_page_content is not None:

        # Since the fetchone call returned a list of tuples, strip out just
        # the value and return it without the tuple or list enclosure.
        return wiki_page_content

    else:

        # TODO: Is this an acceptable outcome? Should this be a hard error?
        # The assumption here is that while one entry may be bad, we wish
        # to continue processing the others and just note the problem.
        error_message = "Unable to retrieve content from {}:{}".format(
            wiki_page_project, wiki_page_name
        )
        log.warning(error_message)
        return error_message

def get_include_calls(wiki_page_contents, wiki_page_project):

    """
    Parse the contents of the initial wiki page and pull out every instance
    where the Redmine include macro is called. We'll use this list to
    find included wiki pages and then later to search/replace the include
    calls with the content of the wiki pages that the macro calls were
    pulling into the original wiki page.
    """

    # This pattern is intended to match the entire include macro call,
    # including the macro itself.
    #
    # NOTE: I could not get the syntax right to support using .format()
    # so I fell back to using classic string formatting
    # TODO: Consider moving this to external config file for easy maintenace
    include_macro_pattern = r'{{include\(%s:[a-zA-Z0-9 _\-\']+\)}}' % (wiki_page_project)

    # TODO: Do we properly handle zero results? Yes, the while loop which
    # calls this function checks for an empty list to know when to stop
    # looping.
    wiki_page_macro_calls = []
    wiki_page_macro_calls = re.findall(include_macro_pattern, wiki_page_contents)

    log.debug("List of include macro calls: %s", wiki_page_macro_calls)

    return wiki_page_macro_calls


def get_included_wiki_pages(wiki_page_macro_calls, wiki_page_project):

    """
    Accepts a list of include page macro call strings and pulls out the
    names of the pages that are being included by the primary wiki page.
    This list of pages will be sourced and used to replace the original
    Redmine include macro calls so that when finished, a complete page
    (without any further include calls) is used to generate notifications.
    """

    # This is meant to match just the page name that is being included
    #
    # NOTE: I could not get the syntax right to support using .format()
    # so I fell back to using classic string formatting
    # TODO: Consider moving this to external config file for easy maintenace
    included_page_pattern = r'{{include\(%s:([a-zA-Z0-9 _\-\']+)\)}}' % (wiki_page_project)

    wiki_page_names = []

    for match in wiki_page_macro_calls:
        included_page = re.search(included_page_pattern, match)

        if included_page is not None:
            # Append the first parenthesized subgroup of the match
            # The equivalent value appears to be 'included_page.groups()[0]'
            wiki_page_names.append(included_page.group(1))
        else:
            # This function should ONLY be called if there were include
            # macro calls in the primary wiki page. If this situation
            # occurred then there is a bug somewhere and we need to know
            # about it.
            # TODO: Raise exception?
            log.error('No matching wiki page names found')
            sys.exit(1)

    log.debug("List of included wiki pages: %s", wiki_page_names)

    return wiki_page_names



def get_events(settings, event_schedule):

    """
    Builds a list of Event objects representing rows in the event_reminders db
    """

    ####################################################################
    # Create cursor object so that we can interact with the database
    ####################################################################

    log.info('Opening connection to database')
    mysql_connection = open_db_connection(settings, settings.mysqldb_config['events_database'])

    # Cursor for the MySQL copy of the database
    mysql_cursor = mysql_connection.cursor()

    # Dynamically create the select query used to pull data from MySQL table
    # See automated_tickets.ini for the available queries


    # Base query that filters just on the event schedule type. We may
    # further constrain depending on what configuration settings have
    # been toggled.
    base_query = "{} AND event_schedule = '{}'".format(
        settings.queries['event_table_entries'],
        event_schedule)

    # Check configuration setting to determine if we need to filter out
    # "intern" or student worker events.
    if not settings.flags['process_intern_events']:
        query = "{} AND event_schedule = '{}' AND intern_task = 0".format(
            settings.queries['event_table_entries'],
            event_schedule)
    else:
        # Use just the base query then
        query = base_query

    try:
        log.info("Executing query")
        mysql_cursor.execute(query)

    except Exception as error:
        log.exception("Unable to query event_reminders table: %s", error)

    log.debug("Pulling data from %s MySQL table ...", 'events')

    events = []
    for event in mysql_cursor.fetchall():

        # Prune whitespace from all fields
        # event = tuple([item.strip() else item for item in event])
        fields = []
        for field in event:
            if isinstance(field, str):
                field = field.strip()
            fields.append(field)
        event = tuple(fields)

        # Collect a list of all events we need to take action for
        events.append(Event(event))

    ####################################################################
    # Cleanup
    ####################################################################

    # FIXME: Can this be handled with a context manager since there are several
    # places where an exception may occur and cause the connecton to be
    # uncleanly closed?

    log.debug("Closing cursor ...")
    mysql_cursor.close()

    # Close database connections
    log.debug("Closing database connection ...")
    mysql_connection.close()

    return events

# Used by get_full_file_path() function, freestanding function
# in case it needs to be used elsewhere
def file_exists(full_path_to_file):
    """Verify that the file exists and is readable."""

    return bool(os.access(full_path_to_file, os.R_OK))

def file_can_be_modified(full_path_to_file):
    """Verify that the file exists and is writable."""

    return bool(os.access(full_path_to_file, os.W_OK))


# FIXME: Add the from_address and to_address values onto the message object
def send_notification(settings, from_address, to_address, message):
    """
    Long term, this should be an entry point to a validation and notification
    chain of functions, supporting email, text, XMPP and other types
    of notifications. For now, only email notifications are supported.
    """

    log.debug("Notification: %s", message)

    email_server = settings.notification_servers['email_server_ip_or_fqdn']
    email_debug_filename = 'email.txt'

    if settings.flags['testing_mode']:

        # TODO: With the automated-tickets-dev environment setting up a test
        # mail to HTTP submission environment, should the default for test
        # mode still be to write to a log file?
        #
        # Fill in details from this run at the end of the file. It is up to
        # the caller to prune the old file if they wish to have the new
        # results go to a clean file.
        with open(email_debug_filename, "a") as fh:
            fh.writelines(message)

    else:

        server = smtplib.SMTP(email_server)
        #server.set_debuglevel(1)
        server.sendmail(from_address, to_address, message)
        server.quit()
