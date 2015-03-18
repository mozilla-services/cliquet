Changelog
=========

This document describes changes between each past release.


1.1.0 (2015-03-18)
------------------

**Breaking changes**

* `cliquet.storage.postgresql` now uses UUID as record primary key (mozilla-services/cliquet#70)
* Settings ``cliquet.session_backend`` and ``cliquet.session_url`` were
  renamed ``cliquet.cache_backend`` and ``cliquet.cache_url`` respectively.
* FxA user ids are not hashed anymore (mozilla-services/cliquet#82)
* Setting ``cliquet.retry_after`` was renamed ``cliquet.retry_after_seconds``
* OAuth2 redirect url now requires to be listed in
  ``fxa-oauth.webapp.authorized_domains`` (e.g. ``*.mozilla.com``)
* Batch are now limited to 25 requests by default (mozilla-services/cliquet#90)
* OAuth relier has been disabled by default (#193)

**New features**

* Every setting can be specified via an environment variable
  (e.g. ``cliquet.storage_url`` with ``CLIQUET_STORAGE_URL``)
* Logging now relies on `structlog <http://structlog.org>`_ (mozilla-services/cliquet#78)
* Logging output can be configured to stream JSON (mozilla-services/cliquet#78)
* New cache backend for PostgreSQL (mozilla-services/cliquet#44)
* Documentation was improved on various aspects (mozilla-services/cliquet#64, mozilla-services/cliquet#86)
* Handle every backend errors and return 503 errors (mozilla-services/cliquet#21)
* State verification for OAuth2 dance now expires after 1 hour (mozilla-services/cliquet#83)
* Add the preview field for an article (#156)
* Setup the readinglist OAuth scope (#16)
* Add a uwsgi file (#180)

**Bug fixes**

* FxA OAuth views errors are now JSON formatted (mozilla-services/cliquet#67)
* Prevent error when pagination token has bad format (mozilla-services/cliquet#72)
* List of CORS exposed headers were fixed in POST on collection (mozilla-services/cliquet#54)
* Fix environment variables not overriding configuration (mozilla-services/cliquet#100)
* Got rid of custom *CAST* in PostgreSQL storage backend to prevent installation
  errors without superuser (ref #174, mozilla-services/cliquet#99)


1.0 (2015-03-03)
----------------

**Breaking changes**

- Most configuration entries were renamed, see `config/readinglist.ini`
  example to port your configuration
- Status field was removed, archived and deleted fields were added
  (requires a database flush.)
- Remove Python 2.6 support

**New features**

- Add the /fxa-oauth/params endpoint
- Add the DELETE /articles endpoint
  (Needs cliquet.delete_collection_enabled configuration)
- Add the Response-Behavior header on PATCH /articles
- Add HTTP requests / responses examples in the documentation
- Use Postgresql as the default database backend

**Internal changes**

- Main code base was split into a separate project
  `Cliquet <https://github.com/mozilla-services/cliquet>`_
- Perform continuated pagination in loadtests
- Use PostgreSQL for loadtests


0.2.2 (2015-02-13)
------------------

**Bug fixes**

- Fix CORS preflight request permissions (PR #119)


0.2.1 (2015-02-11)
------------------

**Breaking changes**

- Internal user ids for FxA are now prefixed, all existing records
  will be lost (refs #109)

**Bug fixes**

- Fix CORS headers on validation error responses (ref #104)
- Fix handling of defaults in batch requests (ref #111, #112)


0.2 (2015-02-09)
----------------

**Breaking changes**

- PUT endpoint was disabled (ref #42)
- ``_id`` field was renamed to ``id`` (ref PR #91)
- FxA now requires a redirection URL (ref PR #69)

**New features**

- URLs uniques by user (ref #20)
- Handle conflicts responses (ref #45)
- Conditional changes for some articles attributes (ref #6)
- Batching support (ref #2)
- Pagination support (ref #25)
- Online documentation available at http://readinglist.readthedocs.org (ref PR #73)
- Basic Auth nows support any user/password combination (ref PR #78)

**Bug fixes**

- ``marked_read_by`` was ignored on PATCH (ref PR #72)
- Timestamp was not incremented on DELETE (ref PR #95)
- Fix number of bugs regarding support of CORS in error views (ref PR #105)
- Previous Basic Auth could impersonate FxA user (ref PR #78)


0.1 (2015-01-30)
----------------

- Allow Cors (#67)
- Log incomming request to the console (#65)
- Add timestamp for 304 and 412 response (#40)
- Add time vector to GET /articles and GET /articles/<id> (#4)
- Preconditions Headers for Update and Creation (#60)
- Provide number of items in headers of GET /articles (#39)
- Check for filter values (#58)
- Handle article title length (#37)
- Support min, max and no keywords filters (#43)
- Prevent to modify read-only fields (#26)
- Filtering and sort querystring (#44)
- Redis storage (#50)
- Handle errors (#24 - #49)
- Add loadtests (#47)
- Handle API version in URL (#33)
