Readinglist
===========

*Reading List* is a service that aims to synchronize a list of articles URLs
between a set of devices owned by a same account.

|travis| |readthedocs|

.. |travis| image:: https://travis-ci.org/mozilla-services/readinglist.svg?branch=master
    :target: https://travis-ci.org/mozilla-services/readinglist

.. |readthedocs| image:: https://readthedocs.org/projects/readinglist/badge/?version=latest
    :target: http://readinglist.readthedocs.org/en/latest/
    :alt: Documentation Status

API
===

* `Online documentation <http://readinglist.readthedocs.org/en/latest/>`_


Run locally
===========

*Reading List* is based on top of the `cliquet <https://cliquet.rtfd.org>`_ project, and
as such, please refer to cliquet's documentation for more details.


For development
---------------

By default, *Reading List* persists the records and internal cache in a PostgreSQL
database.

The default configuration will connect to the ``postgres`` database on
``localhost:5432``, with user/password ``postgres/``postgres``. See more details
below about installation and setup of PostgreSQL.

::

    make serve


Using Docker
------------

*Reading List* uses `Docker Compose <http://docs.docker.com/compose/>`_, which takes
care of running and connecting PostgreSQL:

::

    docker-compose up


Authentication
--------------

By default, *Reading List* relies on Firefox Account OAuth2 Bearer tokens to authenticate
users.

See `cliquet documentation <http://cliquet.readthedocs.org/en/latest/configuration.html#authentication>`_
to configure authentication options.


Install and setup PostgreSQL
============================

 (*requires PostgreSQL 9.3 or higher*).


Using Docker
------------

::

    docker run -e POSTGRES_PASSWORD=postgres -p 5434:5432 postgres


Linux
-----

On debian / ubuntu based systems:

::

    apt-get install postgresql postgresql-contrib


By default, the ``postgres`` user has no password and can hence only connect
if ran by the ``postgres`` system user. The following command will assign it:

::

    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"


OS X
----

Assuming `brew <http://brew.sh/>`_ is installed:

::

    brew update
    brew install postgresql

Create the initial database:

::

    initdb /usr/local/var/postgres


Install libffi
==============

Linux
-----

On debian / ubuntu based systems::

    apt-get install libffi-dev


OS X
----

Assuming `brew <http://brew.sh/>`_ is installed, libffi installation becomes:

::

    brew install libffi pkg-config


Run tests
=========

::

    make tests


Running in production
=====================

Recommended settings
--------------------

Most default setting values in the application code base are suitable for production.

But the set of settings mentionned below might deserve some review or adjustments:

::

    cliquet.http_scheme = https
    cliquet.batch_max_requests = 25
    cliquet.delete_collection_enabled = false
    cliquet.basic_auth_enabled = false
    fxa-oauth.cache_ttl_seconds = 3600

:note:

    For an exhaustive list of available settings and their default values,
    refer to `cliquet source code <https://github.com/mozilla-services/cliquet/blob/93b94a4ce7f6d8788e2c00b609ec270c377851eb/cliquet/__init__.py#L34-L59>`_.



PostgreSQL setup
----------------

In production, it is wise to run the application with a dedicated database and
user.

::

    postgres=# CREATE USER produser;
    postgres=# CREATE DATABASE proddb OWNER produser;
    CREATE DATABASE


On the first app run, the tables and objects are created. Currently, this process
requires superuser privileges (or a ``BackendError`` might occur).

Grant superuser temporarily:

::

    postgres=# ALTER USER produser SUPERUSER;
    ALTER ROLE

Run the application.

Revoke superuser privilege:

::

    postgres=# ALTER USER produser NOSUPERUSER;
    ALTER ROLE


:note:

    Alternatively the SQL initialization files can be found in the
    *cliquet* source code (``cliquet/cache/postgresql/schemal.sql`` and
    ``cliquet/storage/postgresql/schemal.sql``).

:warning:

    Using a `connection pool <http://pgpool.net>`_ is highly recommended to
    boost performances and bound memory usage (*work_mem per connection*).


Running with uWsgi
------------------

If you want to run the application using uWsgi, you can use
the provided **app.wsgi** file and this command::

    uwsgi --ini config/readinglist.ini

You can tweak the uWsgi configuration in the ini file in
the dedicated **[uwsgi]** section.

If you are using a different ini file, you need to set
its path in the **READINGLIST_INI** environment variable.
