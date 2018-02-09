/*

  Purpose:

      Import all existing Automated Ticket entries as of 2017-03-28

  Notes:

    * If 0 is used for redmine_new_issue_due_after_days, then the due date
      is set for the same day, otherwise it is generated as ticket
      creation date + the number of days specified

    * We do not specify a the from/to column values; the read query
      will use a default value for each from the config file

    * We are relying on each task to default to enabled

    * Tasks are not "intern" tasks by default

    * Priority is set to 'Normal' by default


  TODO:

    * Evaluate all categories for Automated Tickets and adjust as necessary
      ** Example: "Checks - Equipment" might be a better fit for weekly
         maintenance on the staff laptops, or, possibly for the public terminals

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

    (1,@ds_email,'Check email for {}','AutomatedTicketsEmailCheck','sysdocs',@ds,'Checks - Email',0,'High','daily','Candidate for future 2x, 3x daily task'),

    (1,@ds_email,'Pickup/Deliver mail for {}','AutomatedTicketsMailCheck','sysdocs',@ds,'Checks - Dept Email',0,'Normal','daily','no particular priority'),

    (1,@ds_email,'Equipment Checks for {}','AutomatedTicketsEquipmentCheck','sysdocs',@ds,'Checks - Equipment',0,'Normal','twice_week','no particular priority'),

    (1,@ds_email,'Inspect Public terminals and clean/repair as necessary for {}','AutomatedTicketsCleaningPublicTerminals','sysdocs',@ds,'Checks - Equipment',0,'Normal','weekly','no particular priority'),

    (1,@ds_email,'Inspect Staff Laptops and bags for {}','AutomatedTicketsCleaningLaptops','sysdocs',@ds,'Laptop Maintenance',0,'Normal','weekly','no particular priority'),

    (1,@ds_email,'Cleanup work areas for {}','AutomatedTicketsWorkAreaCleanup','sysdocs',@ds,'Cleanup/Sort',0,'Normal','twice_week','no particular priority'),

    (1,@ds_email,'Reimage Staff Laptops for {}','AutomatedTicketsReimagingStaffLaptops','sysdocs',@ds,'Laptop Maintenance',0,'Normal','weekly','no particular priority'),

    (1,@ds_email,'Check storage supplies for {}','AutomatedTicketsCheckStorageSupplies','sysdocs',@ds,'Checks - Storage',0,'Normal','weekly','no particular priority'),

    (1,@ds_email,'Process voicemails for {}','AutomatedTicketsVoicemailCheck','sysdocs',@ds,'Checks - Voicemail',0,'Urgent','weekly','Used to be daily task'),

    (0,@ds_email,'Refresh prototype base images for {}','AutomatedTicketsUpdateBaseImages','sysdocs',@ds,'Image: Create or update base, ISO, etc',21,'Normal','monthly','Due date of 21 days later attempts to flag around the time that second Patch Tuesday updates are released'),
    (0,@ds_email,'Generate new rollout image for RBD Circulation Laptops {}','AutomatedTicketsUpdateBaseImages','sysdocs',@ds,'Circ Laptops',21,'Normal','monthly','This task is dependent on us to refresh the base image and generate a new rollout image first before they can do their work'),

    (1,@ds_email,'Marcia''s laptop - Apply updates for {}','AutomatedTicketsMaricaLaptop','sysdocs',@ds,'On-Demand Updates',7,'Normal','monthly','Ticket is generated monthly, but Marcia brings laptop in less often than that'),

    (1,@ds_email,'Consumable supplies check for {}','AutomatedTicketsConsumablesCheck','sysdocs',@ds,'Inventory Management',7,'Normal','monthly','Historically no due date, but setting to creation + a reasonable time frame'),

    (1,@ds_email,'Graveyard Processing for {}','AutomatedTicketsSurplusProcessing','sysdocs',@ds,'Surplus',7,'Normal','monthly','Historically no due date, but setting to creation + a reasonable time frame'),

    (1,@ds_email,'Inventory check for {}','AutomatedTicketsInventoryCheck','sysdocs',@ds,'Inventory Management',7,'Normal','twice_month','Candidate for increased frequency'),

    (1,@ds_email,'Reimage RBD Circulation Laptops {}','AutomatedTicketsCirculatingStudentLaptops','sysdocs',@ds,'Circ Laptops',21,'Normal','monthly','This task is dependent on us to refresh the base image and generate a new rollout image first before they can do their work'),

    (1,@ds_email,'Verify dry-erase department calendar {}','AutomatedTicketsSystemsDryEraseCalendar','sysdocs',@ds,'Cleanup/Sort',7,'Normal','monthly','Historically no due date'),

    (1,@ds_email,'Process Renewals list for {}: Look for upcoming expirations, update prior reports if unacknowledged','AutomatedTicketsCheckRenewalDates','sysdocs',@ds,'Inventory Management',0,'Urgent','monthly','Historically no due date, normal priority'),

    (0,@ss_email,'mssql.example.com - Microsoft Updates for {}','AutomatedTicketsManualPatching','sysdocs',@ss,'Patch',21,'High','monthly','Historically no due date, normal priority'),

    (0,@ss_email,'storageserver1.example.com - Microsoft Updates for {}','AutomatedTicketsManualPatching','sysdocs',@ss,'Patch',21,'High','monthly','Historically no due date, normal priority'),

    (0,@ss_email,'loanserver.example.com - Microsoft Updates for {}','AutomatedTicketsManualPatching','sysdocs',@ss,'Patch',21,'High','monthly','Historically no due date, normal priority')

;
