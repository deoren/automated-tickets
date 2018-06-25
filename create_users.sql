
-- Purpose: CREATE USER accounts and GRANT permissions to work with event_reminders DATABASE

-- This should already be taken care of by importing database_schema.sql
-- CREATE DATABASE event_reminders CHARACTER SET utf8;


-- The below examples all use a UNIX socket for connections. MySQL specifies
-- users as a username/hostname pair, so to have an account accessed by a
-- remote client IP, you will need to specify that remote IP at creation time.
-- https://dev.mysql.com/doc/refman/5.5/en/account-names.html
--
-- Update the CREATE USER and GRANT examples below to reference the remote IP
-- instead of localhost if the account needs to be accessible remotely.


-- Create read-write user for existing database. Useful for admin work now
-- and for use by the future web app (though best practice likely dictates
-- creating a separate account just for the web app
CREATE USER 'events_rw'@'localhost' IDENTIFIED BY 'ChangeM3';
GRANT ALL PRIVILEGES ON event_reminders.* TO 'events_rw'@'localhost';




-- Create read-only user for (existing) database. Useful for creating backups
-- and for scripted access. This account needs not only read access to the
-- event_reminders database, but the Redmine database containing wiki pages
-- that are referenced by this project.
CREATE USER 'events_ro'@'localhost' IDENTIFIED BY 'ChangeM3';
GRANT SELECT,LOCK TABLES ON event_reminders.* TO 'events_ro'@'localhost';

-- The following permissions are needed to pull wiki page contents from
-- the Redmine database. See the query in the automated_tickets.ini config
-- file for how these columns are used.
GRANT SELECT(text) ON redmine.wiki_contents TO 'events_ro'@'localhost';
GRANT SELECT(id) ON redmine.wiki_contents TO 'events_ro'@'localhost';

GRANT SELECT(id) ON redmine.wiki_pages TO 'events_ro'@'localhost';
GRANT SELECT(wiki_id) ON redmine.wiki_pages TO 'events_ro'@'localhost';
GRANT SELECT(title) ON redmine.wiki_pages TO 'events_ro'@'localhost';

GRANT SELECT(id) ON redmine.wikis TO 'events_ro'@'localhost';
GRANT SELECT(project_id) ON redmine.wikis TO 'events_ro'@'localhost';

GRANT SELECT(identifier) ON redmine.projects TO 'events_ro'@'localhost';
GRANT SELECT(id) ON redmine.projects TO 'events_ro'@'localhost';

FLUSH PRIVILEGES;





