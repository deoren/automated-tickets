/*

   Purpose: Collection of SQL statements to create initial database for events

   WARNING: Requires MySQL >= 5.5.3 due to length of table/field comments

   References:

      http://dev.mysql.com/doc/refman/5.5/en/create-table.html
      http://dev.mysql.com/doc/refman/5.5/en/create-view.html
      http://www.mysqltutorial.org/create-sql-views-mysql.aspx

   Notes:

      * View column comments via:
          show full columns from TABLE_NAME;
          show create TABLE_NAME;

      * A comment for a column can be specified with the COMMENT option, up to
        1024 characters long (255 characters before MySQL 5.5.3).

      * A comment for the table, up to 2048 characters long (60 characters
        before MySQL 5.5.3).

*/


-- Create database for event entries. Our script will parse those entries and
-- generate notifications. The first design will be strictly to replace the
-- existing crude/hard-coded scripts, each dedicated to a specific time period.
CREATE DATABASE event_reminders CHARACTER SET utf8;

-- Emphasizing what database we're working with
USE event_reminders;

-- Milestone one database schema design
--
-- All columns are near 1:1 entries from the old "list of dictionaries" setup
-- that I used in the various scripts used to generate automated tickets.
-- Later revisions will see many columns from this table moved into separate
-- tables.



CREATE TABLE `event_reminders`.`events`
(
  `id` int(11) NOT NULL auto_increment,

  `enabled` TINYINT(1) NOT NULL DEFAULT 1
    COMMENT "If set to 1, then email notifications will be generated. Later designs might incorporate other actions for enabled entries. If set to 0, no actions will be taken for the entry.",

  `intern_task` TINYINT(1) NOT NULL DEFAULT 0
    COMMENT "Whether this event is something a student worker or intern handles. The default value is 0, or not an intern task. This value is used as a filter so that we can turn on/off events/tasks for times when students are not available to perform the task.",

  /* Matching the same field type/length as the email_addresses table */
  `email_to_address` varchar(255) NULL
    COMMENT "FIXME: For automated tickets this address will usually be the same for all events. If this is left blank the the default set in the config file applies.",

  /* Matching the same field type/length as the email_addresses table */
  -- Note: The old one-script-per-schedule approach used different sender addresses depending on the destination project
  `email_from_address` varchar(255) NULL
    COMMENT "FIXME: For automated tickets this address will be the same for all events. This should be moved to its own table in the next milestone.",

  `email_subject_prefix` text NOT NULL
    COMMENT "The prefix for notifications related to this event. The script referencing this table will append an auto-generated suffix to denote the date or date range.",

  /* Matching the same field type/length as the wiki_pages table */
  `redmine_wiki_page_name` varchar(255) NOT NULL
    COMMENT "The name of the wiki page (without project prefix) whose text will be inserted into the body of the email notification.",

  /* Matching the same field type/length as the projects table */
  `redmine_wiki_page_project_shortname` varchar(255) NOT NULL
    COMMENT "The tag or project identifier displayed in the project URL. Used to match the wiki page whose text will be pulled for email notification.",

  /* Matching the same field type/length as the projects table */
  `redmine_new_issue_project` varchar(255) NOT NULL
    COMMENT "The full name of the project where the ticket generated from the email notification will be routed",

  /* Matching the same field type/length as issue_categories table */
  `redmine_new_issue_category` varchar(60) NOT NULL
    COMMENT "The full category name for the routed ticket.",

  /* Matching the same field/type length as issue_statuses table */
  `redmine_new_issue_status` varchar(30) NOT NULL DEFAULT 'Assigned'
    COMMENT "The status that should be set for newly created tickets (the workflow must allow for this initial status)",

  /* Custom approach to handling due dates. At some future milestone we may need to add support for "trigger" dates
     to complement this setting */
  `redmine_new_issue_due_after_days` smallint NULL
    COMMENT "Supported values: The number of days after the ticket is generated when it should be due. Whole, positive numbers only.",

  /* Matching the same field type as enumerations table */
  `redmine_new_issue_priority` varchar(30) NOT NULL DEFAULT 'Normal'
    COMMENT "Supported values: Real date value or lowercase 'today'. That keyword is replaced as part of the retrieval query.",

   /* Fixed options that reflect entries in the /etc/cron.d/automated_tickets file */
  `event_schedule` varchar(30) NOT NULL
    COMMENT "Specific keywords that the controller script uses to calcuate due dates for newly generated tickets. Supported values are found in the DATE_LABEL dictionary. A few examples: daily, weekly, twice_month, twice_year",

  `last_modified` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `comments` text NULL,
  PRIMARY KEY (`id`)
)
    ENGINE=InnoDB
    DEFAULT CHARSET=utf8
    COMMENT="Milestone one design for automated_tickets project. This table represents various events and tasks that we should receive notifications for."
;
