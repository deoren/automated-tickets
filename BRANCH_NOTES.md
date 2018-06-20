# Scratch notes for this branch

This file will likely be tossed once I have finished testing on this
branched and squashed/merged any successful results back to master.

Well, that or the notes merged into a larger doc file.

## Handling predefined date keywords

Somehow I'll need to find a way to associate specific pre-existing keywords
with specific dates for execution.

In short, how does "yearly" map to a specific month/day?

One option here is to keep the behavior of using those predefined keywords
as a command-line option referenced from a cron job entry. If there is
an entry in the `base_supported_date_format_patterns` data structure (or
whatever I take to calling it later) with a matching `name` key, then matching
events in the database are reported.

## Handling specific dates

The idea is to have specific keywords referenced by a cron.d entry. That entry
calls the automated_tickets.py script and references the hard-coded keyword
which is intended to reflect the date/time when the script is called.

I am also planning to have an additional daily entry (at least until specific
times are supported) which is set to call a different reserved keyword. This
keyword would instruct the script to calculate an acceptable, dynamic list
of keywords that would be used to search for matching events in the database.

Those events would not have a `name` key in the
`base_supported_date_format_patterns` data structure. By lacking a `name` key,
that is how the script would be able to confirm that the value should be
computed dynamically.
