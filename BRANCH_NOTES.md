# Scratch notes for this branch

This file will likely be tossed once I have finished testing on this
branched and squashed/merged any successful results back to master.

Well, that or the notes merged into a larger doc file.

## Handling keywords: static, dynamic

As of this writing, this is my plan for handling keywords:

- static keywords
    - composed of preset frequencies

- dynamic keyword
    - composed of date patterns

Currently static keywords rely on cron calling the script at specified
intervals with an appropriate "static" keyword (e.g., `monthly`, `daily`,
`weekly`). To better support both static and dynamic keywords, I'm thinking
that the cron.d file will be reduced (at least to begin with) a daily call
and then move the keyword/frequency static entries to a database table.

The script would then be modified to:

1. Determine current date keywords (limited list of dynamic patterns)
2. Search new table for those date keywords
    - This should return a list of valid/matching static keywords
3. Combine earlier dymamic date keywords with static keywords
4. Query events table for matching entries
5. Process normally

## Display format

What about display format (e.g., "Reimage laptops for June 2018 (monthly)"?
Here, `monthly` is the frequency and `June 2018` is the `coverage_period`.

## Keyword properties

Not sure yet if we'll turn these into custom objects, but they seem like a
good fit for a set of new db table fields:

- date_format
- name
    - not sure about this one
- display_format

## DATE_LABEL: How it was used before

The current `master` branch uses the key in `DATE_LABEL` dict to set frequency
that the ticket occcurs at the end of the ticket title.

Example:

> Reimage laptops for June 2018 (monthly)

Here, `June 2018` is the `coverage_period`. This is set using the value portion
of the pair in the `DATE_LABEL` dict. If we're replacing this data structure
(list of dictionaries), then we'll need to pull that information from
another place.

## Supported Dymamic keywords

Today is Jun 21st, 2018; this results in six potential keywords, more if
other patterns such as two digit years (decided against it) and single and
digits months and days.

Current plans:

- 2018_June_21
- June_21
- 21
    - this one will be fun
- 2018_06_21
- 2018_Jun_21
- Jun_21

## Notification subject details

The subject line of the generated emails (but hopefully in the future XMPP
messages, text messages, etc) is currently composed of these values:

    subject_prefix, coverage_period, frequency

which ends up looking like our earlier example:

> Reimage laptops for June 2018 (monthly)

Breakdown (using `pendulum` format specifiers):

| Variable | Value | Notes |
| -------- | ----- | ----- |
| `subject_prefix` | `Reimage laptops for {}` | From `events` table entry |
| `coverage_period` | `MMMM YYYY` | Keyword was used as key to retrieve this |
| `frequency` | `monthly` | Historically keyword; use `display_format` now? |

In this case, this is a reoccuring monthly task.

For static keywords this makes sense. For dynamic keywords, perhaps use the
`coverage_period` to dynamically create this value?

For example, if the keyword is 2018_06_21 then you'll have the year, the
month and the day to work from, so this could be your `coverage_period`
value:

    June 21, 2018

If June_21 is your key, then this would be the `coverage_period`:

    June 21

Regarding frequency, perhaps fall back to looking for a display value? This
could be done in a broad sense for *all* keywords. If present, use it and
note it in the subject line. If not present, don't add any value?


## References

- https://pendulum.eustace.io/
- https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
