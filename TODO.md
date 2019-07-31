# TODO
Here is a list of things that still needs to be done to improve Botos.

## General
 * **[ PRIORITY ]** Add public bulletin board feature where voters can confirm if their votes have been tampered or not.
 * Find the rest of the TODO items and move them to here.
 * Maybe add a MBUI file, and add the MBUI texts and the project file path of the file it is residing in to it.

## Voting
 * Disallow superusers/admins from voting.

## Election Settings
 * Only allow opening of elections if the election keys have been generated already.

## Settings
 * Move static and media URLs and directories settings to `local_settings.py`.

## Utilities
 * Maybe create a utility that will handle serialization and deserialization of the election keys and votes.

## Views
 * Add the crsf_protect, sensitive_post_parameters, and never_cache decorators,
   if need be, to the POST functions of views.
 * Maybe we should not redirect unallowed GETs or POSTs to some URL? Or just show an error 404 page?
 * **[ REFACTOR ]** POST function in `VoteProcessingView`, located in `core/views/vote.py`, _may_ still be improved.

## Templates
 * Allow for setting the page title on a per sub-view basis.

### Default Template
 * Make the template more mobile-friendly.
   * Make the login form in the login subview of the index view transform into a vertically-stacked form, from its original horizontally-stacked form.

## Performance
 * For the `_cast_votes()` function of `VoteProcessingView`, located in `core/views/vote.py`, we need to do a benchmark to confirm if calling to the database to check if a candidate is part of the candidates voted takes more time to perform than iterating through an evaluated list of candidates voted.

## Tests
 * Replace app URLs in tests with URL names, i.e. use reverse() instead of
   hard-coded URLs.
 * In test comments, replace hard-coded URLs with their equivalent URL names.
 * Add tests in the test classes in core/tests/index_views.py and
   core/tests/auth_views.py that will test the GET requests of logged-in users.
 * Add a test in VotedSubviewTest in core/tests/index_views.py that will make
   sure that users are shown the voted sub-view immediately after they have
   voted.
 * Add tests for the authentication views to test whether or not the proper
   message has been sent back after the user has entered the wrong
   username/password combination.
 * Add tests to make sure that the logging out gives back a message.
 * Add tests for the index view. We only have tests for the subviews of index.
 * We need more integration tests.
 * Add unit tests for the private functions in VoteProcessingView, located in `core/views/vote.py`.