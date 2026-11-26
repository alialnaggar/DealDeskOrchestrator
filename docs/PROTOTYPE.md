# Front-end prototype (review console)

`index.html` is one self-contained file: no build step and no backend. All data is mock data that follows the review package design and the fixed business date Wed 20 Jan 2027. It is a design reference; the real front end is rebuilt later on top of the running system.

Shows: deal queue with outcome filters; new deal form with intake validation; a run screen with the five steps in order, stopping at the first failing check and repair rounds (up to 5); the review package (outcome, actions by role, problems with a verified fix, results by round, credit gauges and discount ladders, findings, run record); a read-only chat drawer with references and one what-if.

Sample deals: DD-2027-0142 (needs correction), DD-2027-0145 (cannot confirm), DD-2027-0148 (ready for approval), DD-2027-0139 (intake rejected), DD-2027-0136 (run failed).

Run it: open `index.html` in a browser, or `python3 -m http.server 8080` in this folder.
