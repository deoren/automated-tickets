/*

  Purpose:

      Template for creating new automated tickets.

  Notes:

    * If 0 is used for redmine_new_issue_due_after_days, then the due date
      is set for the same day, otherwise it is generated as ticket
      creation date + the number of days specified

    * We do not specify a the from/to column values; the read query
      will use a default value for each from the config file

    * We are relying on each task to default to enabled

    * Tasks are not "intern" tasks by default

    * Priority is set to 'Normal' by default

*/

-- Variables, because I'm feeling lazy
SET @ds = 'desktop-support';
SET @ss = 'server-support';

SET @ds_email = 'ds-automated-reminders@help.example.com';
SET @ss_email = 'ss-automated-reminders@help.example.com';


-- Here we are inserting a row with the redmine_new_issue_due_after_days
-- value set to 0. This results in the read query subsituting that value
-- for the current date so that tickets have the due date set to the
-- same day the ticket was generated. We are also overriding the default
-- priority.
INSERT INTO `event_reminders`.`events`
  (
    `intern_task`,
    `email_from_address`,
    `email_subject_prefix`,
    `redmine_wiki_page_name`,
    `redmine_wiki_page_project_shortname`,
    `redmine_new_issue_project`,
    `redmine_new_issue_category`,
    `redmine_new_issue_due_after_days`,
    `redmine_new_issue_priority`,
    `event_schedule`,
    `comments`
  )
VALUES

    -- Template entry for a Desktop Support task
    --
    -- * 'sysdocs' is the usual value for 'WIKI_PROJECT_SHORT_NAME_HERE'
    -- * Valid values for FREQUENCY_HERE are (all lowercase): daily, twice_week, weekly, weekly_monday, weekly_tuesday, weekly_wednesday, weekly_thursday, weekly_friday, twice_month, monthly, twice_year, yearly
    --   See the DATE_LABEL dictionary for an authoratative list.
    (1,@ds_email,'SUBJECT_LINE_TEMPLATE_HERE for {}','WIKI_PAGE_NAME_HERE','WIKI_PROJECT_SHORT_NAME_HERE',@ds,'CATEGORY_NAME_HERE',DUE_AFTER_DAYS_HERE_AS_UNQUOTED_NUMBER,'PRIORITY_HERE','frequency_here','OPTIONAL_COMMENT_HERE_REMOVE_THIS_IF_NOT_USING'),

    -- Template entry for a Server Support task
    --
    -- * 'sysdocs' is the usual value for 'WIKI_PROJECT_SHORT_NAME_HERE'
    -- * Valid values for FREQUENCY_HERE are (all lowercase): daily, twice_week, weekly, weekly_monday, weekly_tuesday, weekly_wednesday, weekly_thursday, weekly_friday, twice_month, monthly, twice_year, yearly
    --   See the DATE_LABEL dictionary for an authoratative list.
    (0,@ss_email,'SUBJECT_LINE_TEMPLATE_HERE for {}','WIKI_PAGE_NAME_HERE','WIKI_PROJECT_SHORT_NAME_HERE',@ss,'CATEGORY_NAME_HERE',DUE_AFTER_DAYS_HERE_AS_UNQUOTED_NUMBER,'PRIORITY_HERE','frequency_here','OPTIONAL_COMMENT_HERE_REMOVE_THIS_IF_NOT_USING')

;
