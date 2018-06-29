-- Purpose: Useful queries for helping to fill out options in config file




-- The wiki id is not the same value as the project id. Projects may
-- have a wiki, or they may not and as a new wiki is created the wiki_id
-- number is incremented to track the new wiki. The 'wikis' table ties
-- together the project id with the wiki id, and then the 'wiki_pages'
-- table contains the name of the pages. The actual page content resides
-- in the 'wiki_contents' table.



-- Summary of events, useful for updating documentation manually
SELECT
    CASE
        WHEN intern_task = 1 THEN 'Yes'
        WHEN intern_task = 0 THEN 'No'
    END AS 'Student task',
    CASE
        WHEN enabled = 1 THEN 'Yes'
        WHEN enabled = 0 THEN 'No'
    END AS 'Enabled',
    SUBSTRING(email_subject_prefix FROM 1 FOR 60) AS 'Ticket title template (truncated)',
    redmine_wiki_page_name AS 'Wiki page',
    event_schedule AS 'Frequency',
    redmine_new_issue_due_after_days AS 'Due in X days'
FROM
    events
ORDER BY
    enabled,
    redmine_new_issue_project,
    event_schedule
;

-- "Dashboard" query
SELECT
    wp.title AS 'Wiki page name',
    p.name AS 'Project Name',
    p.identifier as 'Project shortname'
FROM
    projects AS p
INNER JOIN wikis AS w ON
    w.project_id = p.id
INNER JOIN wiki_pages AS wp ON
    wp.wiki_id = w.id
ORDER BY p.name, wp.title;


-- The query responsible for pulling wiki page content from a specified
-- wiki page within a specified project (identified by project shortname)
SET @project_shortname = 'docs';
SET @wiki_page_title = 'Creating_a_new_Git_repository';
SELECT
    wiki_contents.text
FROM
    wiki_contents
INNER JOIN wiki_pages ON
    wiki_pages.id = wiki_contents.id
INNER JOIN wikis ON
    wikis.id = wiki_pages.wiki_id
INNER JOIN projects ON
    projects.id = wikis.project_id
WHERE
    wiki_pages.title = @wiki_page_title
AND
    projects.identifier = @project_shortname;


-- Various details that will be needed for filling out the configuration file
-- and for general troubleshooting later on (ex: search/replace include macro)
SELECT
    p.name AS 'Project Name',
    p.id as 'Project id',
    p.identifier as 'Project shortname',
    w.id AS 'Wiki id',
    wp.title AS 'Wiki page name',
    wp.id AS 'Wiki page id'
FROM
    projects AS p
INNER JOIN wikis AS w ON
    -- tie together wikis table with projects table
    w.project_id = p.id
INNER JOIN wiki_pages AS wp ON
    wp.wiki_id = w.id
ORDER BY p.name, wp.title;


-- List the name of each wiki page in the specified project that uses
-- the '{{include()}}' Redmine macro. Leave off the trailing AND
-- bit in order to list all wiki pages that use the include macro.
SET @wiki_project_shortname = 'docs';
SELECT wiki_pages.title
FROM wiki_contents
INNER JOIN wiki_pages ON wiki_pages.id = wiki_contents.id
INNER JOIN wikis ON wikis.id = wiki_pages.wiki_id
INNER JOIN projects ON projects.id = wikis.project_id
WHERE wiki_contents.text LIKE '%include%' AND projects.identifier = @wiki_project_shortname;


-- List all enabled events
SELECT
  id,
  enabled,
  email_to_address,
  email_from_address,
  email_subject_prefix,
  event_schedule
FROM events
WHERE enabled = 1;


-- List all events that are overriding either the TO or FROM address
SELECT
  id,
  enabled,
  email_to_address,
  email_from_address,
  email_subject_prefix,
  event_schedule
FROM
  events
WHERE
  (email_to_address IS NOT NULL) OR (email_from_address IS NOT NULL)
ORDER BY
  event_schedule;


-- Retrieve members of a specific group so that they can be added as Watchers
-- via inclusion in the CC list of a newly created ticket
--
-- http://www.redmine.org/boards/1/topics/19470
/*
    Notes:

    * Groups are included in the users table
    * Users have a type. Known types are below:
    ** GroupNonMember
    ** GroupAnonymous
    ** Group
    ** User
    ** AnonymousUser
    * I should match against 'Group' type
    * The users.id value will need to be used against the groups_users table
      to map a group name to a group id and then look up users who are members
      of that group id in order to build a list of group members for a group.

*/
