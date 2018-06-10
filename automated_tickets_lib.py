#!/usr/bin/env python3

"""
Library module used by the automated_tickets.py script. Not intended for direct use.
"""



########################################
# Modules - Standard Library
########################################

import configparser
import datetime
import os
import re
import smtplib
import sys

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
import mysql.connector as mysql



if __name__ == "__main__":
    sys.exit("This module is meant to be imported, not executed directly.")

#######################################################
# Variables, constants
#######################################################


DATE = datetime.date.today()
TODAY = DATE.strftime('%Y-%m-%d')

# Disable various modes by default. Will be overriden by main script that
# imports this module
DISPLAY_DEBUG_MESSAGES = False
DISPLAY_INFO_MESSAGES = False

# Going to assume we want these by default, we can override in config file
DISPLAY_WARNING_MESSAGES = True
DISPLAY_ERROR_MESSAGES = True

# Ref #4: Background coloring provided by ASCII escape sequences
BACKGROUND_COLORS = {
    'DEBUG': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}


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



#######################################################
# Classes
#######################################################

class Event(object):
    """
    Represents an event from the event_reminders table
    """

    def __init__(self, event):

        print_debug("{}".format(event), "Event class, input tuple")

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

        print_debug("new instance of object created", "Event class")


class Settings(object):

    """
    Represents the user configurable settings retrieved from
    an external config file
    """

    def __init__(self, config_file_list):

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

            print_debug("Config files processed: {}".format(processed_files), "CONFIG")

            # FIXME: We can either pass a verified list of files to the parser
            # OR we can verify the number of processed files is 1 or greater.
            if len(processed_files) < 1:

                # Just raise the standard parsing error exception instead
                # of trying to handle a missing file differently than one
                # with parsing errors. We may change this later if found
                # to be too confusing.
                raise configparser.ParsingError(config_file_list)

        except configparser.ParsingError as err:

            error_message = "Unable to parse config file: {}".format(err)
            print_error(error_message, "CONFIG")
            sys.exit()


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

                print_debug("{} has a value of {} and a type of {}".format(
                    key,
                    self.flags[key],
                    type(self.flags[key])), "CONFIG")

        except configparser.NoSectionError as err:

            error_message = "{}: Unable to parse config file: {}".format("CONFIG", err)
            print_error(error_message)
            sys.exit(error_message)


#######################################################
# Functions
#######################################################

def open_db_connection(settings, database):

    """
    Open a connection to the database and return a cursor object
    """


    ####################################################################
    # Open connections to databases
    ####################################################################

    try:

        print_debug("""MySQL connection details:

        user: {}
        password: {}
        host: {}
        port: {}
        database: {}
        raise_on_warnings: {}
        raise_on_warnings (type): {}
        """.format(settings.mysqldb_config['user'],
                   settings.mysqldb_config['password'],
                   settings.mysqldb_config['host'],
                   settings.mysqldb_config['port'],
                   database,
                   settings.mysqldb_config['raise_on_warnings'],
                   type(settings.mysqldb_config['raise_on_warnings'])), "MySQL")

        mysql_connection = mysql.connect(
            user=settings.mysqldb_config['user'],
            password=settings.mysqldb_config['password'],
            host=settings.mysqldb_config['host'],
            port=settings.mysqldb_config['port'],
            database=database,
            raise_on_warnings=settings.mysqldb_config['raise_on_warnings']
        )

    except mysql.Error as error:
        error_message = "Unable to connect to database: {}".format(error)
        print_error(error_message, "MySQL")
        sys.exit("MySQL: {}".format(error_message))


    return mysql_connection


def get_wiki_page_contents(settings, wiki_page_name, wiki_page_project, wiki_page_database):

    """
    Retrieve contents of the specified Redmine wiki page for inclusion in notification
    """

    ####################################################################
    # Create cursor object so that we can interact with the database
    ####################################################################

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

        print_debug(query, "Wiki page retrieval query")

        mysql_cursor.execute(query)

    except Exception as e:
        print_error("Unable to execute wiki page retrieval query: {} ".format(e), "MySQL")
        sys.exit()

    try:
        # Grab first element of returned tuple, ignore everything else
        wiki_page_content = mysql_cursor.fetchone()[0]

    except Exception as e:

        # FIXME: Is there a Plan B for wiki page lookup failures?
        print_error("Unable to retrieve wiki page content: {} ".format(e), "MySQL")
        sys.exit()

    if wiki_page_content is not None:

        # Since the fetchone call returned a list of tuples, strip out just
        # the value and return it without the tuple or list enclosure.
        return wiki_page_content

    else:

        return "Unable to retrieve content from {}:{}".format(
            wiki_page_project, wiki_page_name
        )

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

    wiki_page_macro_calls = []
    wiki_page_macro_calls = re.findall(include_macro_pattern, wiki_page_contents)

    print_debug(wiki_page_macro_calls, "List of include macro calls")

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

        if included_page:
            # Append the first parenthesized subgroup of the match
            # The equivalent value appears to be 'included_page.groups()[0]'
            wiki_page_names.append(included_page.group(1))
        else:
            # This function should ONLY be called if there were include
            # macro calls in the primary wiki page. If this situation
            # occurred then there is a bug somewhere and we need to know
            # about it.
            print_error('No matches found', 'wiki_page_names search')
            sys.exit()

    print_debug("{}".format(wiki_page_names), "List of included wiki pages")

    return wiki_page_names



def get_events(settings, event_schedule):

    """
    Builds a list of Event objects representing rows in the event_reminders db
    """

    ####################################################################
    # Create cursor object so that we can interact with the database
    ####################################################################

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
        mysql_cursor.execute(query)

    except Exception as e:
        print_error("Unable to query event_reminders table: {} ".format(e), "MySQL")

    print_debug("Pulling data from {} MySQL table ...".format('events'), "MySQL")

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

    # Close database connections
    print_debug("Closing database connection ...", "MySQL")
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

# FIXME: Consider tossing this function since I'm not using it
def get_full_file_path(local_dir, global_dir, file_name):
    """
    Returns the full path to an external resource. If the file can be found
    locally (same directory as this script) that full path will be returned,
    otherwise the full path will be built from the "normal" location
    """

    local_file = os.path.join(local_dir, file_name)

    global_file = os.path.join(global_dir, file_name)

    # TODO: Consider adding a hook to each function to provide this value
    # for debug output (troubleshooting)
    name_of_this_function = sys._getframe().f_code.co_name

    print_debug("local file is {}".format(local_file), name_of_this_function)
    print_debug("global file is {}".format(global_file), name_of_this_function)

    # Attempt to reference local file
    if file_exists(local_file):
        return local_file

    elif file_exists(global_file):
        return global_file

    else:
        # FIXME: Raise exception instead?
        error_message = "[!] Unable to verify access for '{}' at '{}' or '{}'. Exiting ..."
        sys.exit(error_message.format(file_name, local_file, global_file))


def print_debug(message, prefix=""):
    """Prints message if the DISPLAY_DEBUG_MESSAGES flag is set"""

    if DISPLAY_DEBUG_MESSAGES:

        if len(prefix) > 0:
            prefix = "{}:".format(prefix)

        print("{}[d] {} {}{}".format(
            BACKGROUND_COLORS['DEBUG'],
            prefix,
            # Explicitly convert passed message to string for display
            str(message),
            BACKGROUND_COLORS['ENDC']))

def print_info(message, prefix=""):
    """Prints message if the DISPLAY_INFO_MESSAGES flag is set"""

    if DISPLAY_INFO_MESSAGES:

        if len(prefix) > 0:
            prefix = "{}:".format(prefix)

        print("{}[i] {} {}{}".format(
            BACKGROUND_COLORS['BOLD'],
            prefix,
            # Explicitly convert passed message to string for display
            str(message),
            BACKGROUND_COLORS['ENDC']))

def print_warning(message, prefix=""):
    """Prints warning message to console"""

    if DISPLAY_WARNING_MESSAGES:

        if len(prefix) > 0:
            prefix = "{}:".format(prefix)

        print("{}[w] {} {}{}".format(
            BACKGROUND_COLORS['WARNING'],
            prefix,
            # Explicitly convert passed message to string for display
            str(message),
            BACKGROUND_COLORS['ENDC']))

def print_error(message, prefix=""):
    """Prints warning message to console"""

    if DISPLAY_ERROR_MESSAGES:

        if len(prefix) > 0:
            prefix = "{}:".format(prefix)

        print("{}[!] {} {}{}".format(
            BACKGROUND_COLORS['FAIL'],
            prefix,
            # Explicitly convert passed message to string for display
            str(message),
            BACKGROUND_COLORS['ENDC']))

# FIXME: Add the from_address and to_address values onto the message object
def send_notification(settings, from_address, to_address, message):
    """
    Long term, this should be an entry point to a validation and notification
    chain of functions, supporting email, text, XMPP and other types
    of notifications. For now, only email notifications are supported.
    """

    print_debug(message, "Notification")

    email_server = settings.notification_servers['email_server_ip_or_fqdn']
    email_debug_filename = 'email.txt'

    if settings.flags['testing_mode']:

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
