##################
Resource endpoints
##################

.. _resource-endpoints:

In this section, the request example provided are performed using
`httpie <https://github.com/jkbr/httpie>`_ .


GET /articles
=============

**Requires authentication**

Returns all records of the current user for this resource.

The returned value is a JSON mapping containing:

- ``items``: the list of records, with exhaustive attributes

A ``Total-Records`` header is sent back to indicate the estimated
total number of records included in the response.

A header ``Last-Modified`` will provide the current timestamp of the
collection (*see Server timestamps section*).  It is likely to be used
by client to provide ``If-Modified-Since`` or ``If-Unmodified-Since``
headers in subsequent requests.


Filtering
---------

**Single value**

* ``/articles?unread=true``

.. **Multiple values**

.. * ``/articles?status=1,2``

**Minimum and maximum**

Prefix attribute name with ``min_`` or ``max_``:

* ``/articles?min_word_count=4000``

:note:
    The lower and upper bounds are inclusive (*i.e equivalent to
    greater or equal*).

:note:
   ``lt_`` and ``gt_`` can also be used to exclude the bound.

**Exclude**

Prefix attribute name with ``not_``:

* ``/articles?not_read_position=0``

:note:
    Will return an error if a field is unknown.

:note:
    The ``Last-Modified`` response header will always be the same as
    the unfiltered collection.

Sorting
-------

* ``/articles?_sort=-last_modified,title``

.. :note:
..     Articles will be ordered by ``-stored_on`` by default (i.e. newest first).

:note:
    Ordering on a boolean field gives ``true`` values first.

:note:
    Will return an error if a field is unknown.


Counting
--------

In order to count the number of records, for a specific field value for example,
without fetching the actual collection, a ``HEAD`` request can be
used. The ``Total-Records`` response header will then provide the
total number of records.

See :ref:`batch endpoint <batch>` to count several collections in one request.


Polling for changes
-------------------

The ``_since`` parameter is provided as an alias for
``gt_last_modified``.

* ``/articles?_since=123456``

The new value of the collection latest modification is provided in
headers (*see Server timestamps section*).

When filtering on ``last_modified`` (i.e. with ``_since`` or ``_to`` parameters),
every deleted articles will appear in the list with a deleted status
(``deleted=true``).

If the request header ``If-Modified-Since`` is provided, and if the
collection has not suffered changes meanwhile, a ``304 Not Modified``
response is returned.

:note:
   The ``_to`` parameter is also available, and is an alias for
   ``lt_last_modified`` (*strictly inferior*).


Paginate
--------

If the ``_limit`` parameter is provided, the number of items is limited.

If there are more items for this collection than the limit, the
response will provide a ``Next-Page`` header with the URL for the
Next-Page.

When there is not more ``Next-Page`` response header, there is nothing
more to fetch.

Pagination works with sorting and filtering.


List of available URL parameters
--------------------------------

- ``<prefix?><attribute name>``: filter by value(s)
- ``_since``: polling changes
- ``_sort``: order list
- ``_limit``: pagination max size
- ``_token``: pagination token


Combining all parameters
------------------------

Filtering, sorting and paginating can all be combined together.

* ``/articles?_sort=-last_modified&_limit=100``


Example
-------

::

    http POST http://localhost:8000/v1/articles?_sort=-last_modified -v --auth "admin:"


.. code-block:: http

    GET /v1/articles?_sort=-last_modified HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Host: localhost:8000
    User-Agent: HTTPie/0.8.0

    HTTP/1.1 200 OK
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Total-Records, Alert, Next-Page
    Content-Length: 610
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:20:08 GMT
    Last-Modified: 1425053903124
    Server: waitress
    Total-Records: 1

    {
        "items": [
            {
                "added_by": "Natim",
                "added_on": 1425053903123,
                "excerpt": "",
                "favorite": false,
                "id": "ff795c43c02145a4b7a5df5260ee182d",
                "is_article": true,
                "last_modified": 1425053903124,
                "marked_read_by": null,
                "marked_read_on": null,
                "read_position": 0,
                "resolved_title": "The Hawk Authorization protocol",
                "resolved_url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
                "archived": false,
                "stored_on": 1425053903123,
                "title": "The Hawk Authorization protocol",
                "unread": true,
                "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
                "word_count": null
            }
        ]
    }


POST /articles
==============

**Requires authentication**

Used to create a record on the server. The POST body is a JSON
mapping containing the values of the resource schema fields.

- ``url``
- ``title``
- ``added_by``

The POST response body is the newly created record, if all posted values are valid.

If the request header ``If-Unmodified-Since`` is provided, and if the record has
changed meanwhile, a ``412 Precondition failed`` error is returned.

**Optional values**

- ``added_on``
- ``excerpt``
- ``favorite``
- ``unread``
- ``archived``
- ``is_article``
- ``resolved_url``
- ``resolved_title``

**Auto default values**

For v1, the server will assign default values to the following attributes:

- ``id``: *uuid*
- ``resolved_url``: ``url``
- ``resolved_title``: ``title``
- ``excerpt``: empty text
- ``archived``: false
- ``favorite``: false
- ``unread``: true
- ``read_position``: 0
- ``is_article``: true
- ``last_modified``: current server timestamp
- ``stored_on``: current server timestamp
- ``marked_read_by``: null
- ``marked_read_on``: null
- ``word_count``: null

For v2, the server will fetch the content, and assign the following attributes with actual values:

- ``resolved_url``: the final URL obtained after all redirections resolved
- ``resolved_title``: The fetched page's title (content of <title>)
- ``excerpt``: The first 200 words of the article
- ``word_count``: Total word count of the article


Validation
----------

If the posted values are invalid (e.g. *field value is not an integer*)
an error response is returned with status ``400``.


Conflicts
---------

Articles URL are unique per user (both ``url`` and ``resolved_url``).

:note:
    A ``url`` always resolves towards the same URL. If ``url`` is not unique, then
    its ``resolved_url`` won't either.

:note:
    Unicity on URLs is determined the full URL, including location hash.
    (e.g. http://news.com/day-1.html#paragraph1, http://spa.com/#/content/3)

:note:
    Deleted records are not taken into account for field unicity.

If the a conflict occurs, an error response is returned with status ``409``.
A ``existing`` attribute in the response gives the offending record.

Example
-------

::

    http POST http://localhost:8000/v1/articles \
        title="The Hawk Authorization protocol" \
        url=https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/ \
        added_by=Natim \
        --auth "admin:" -v

.. code-block:: http

    POST /v1/articles HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Content-Length: 150
    Content-Type: application/json; charset=utf-8
    Host: localhost:8000
    User-Agent: HTTPie/0.8.0

    {
        "added_by": "Natim",
        "title": "The Hawk Authorization protocol",
        "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/"
    }

    HTTP/1.1 201 Created
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Total-Records, Alert, Next-Page
    Content-Length: 597
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:18:23 GMT
    Server: waitress

    {
        "added_by": "Natim",
        "added_on": 1425053903123,
        "archived": false,
        "excerpt": "",
        "favorite": false,
        "id": "ff795c43c02145a4b7a5df5260ee182d",
        "is_article": true,
        "last_modified": 1425053903124,
        "marked_read_by": null,
        "marked_read_on": null,
        "read_position": 0,
        "resolved_title": "The Hawk Authorization protocol",
        "resolved_url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "stored_on": 1425053903123,
        "title": "The Hawk Authorization protocol",
        "unread": true,
        "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "word_count": null
    }


DELETE /articles
================

**Requires authentication**

Delete multiple records. **Enabled by default**, see recommended production
settings to disable.

The DELETE response is a JSON mapping with an ``items`` attribute, returning
the list of records that were deleted.

It supports the same filtering capabilities as GET.

If the request header ``If-Unmodified-Since`` is provided, and if the collection
has changed meanwhile, a ``412 Precondition failed`` error is returned.

Example
-------

::

    http DELETE http://localhost:8000/v1/articles \
        --auth "admin:" -v

.. code-block:: http

    DELETE /v1/articles HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Content-Length: 0
    Host: localhost:8000
    User-Agent: HTTPie/0.8.0


    HTTP/1.1 200 OK
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Alert
    Content-Length: 100
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:27:55 GMT
    Server: waitress

    {
        "items": [
            {
                "deleted": true,
                "id": "30afb809ca7745a58496a09c6a4afcac",
                "last_modified": 1425054475110
            }
        ]
    }


GET /articles/<id>
==================

**Requires authentication**

Returns a specific record by its id.

For convenience and consistency, a header ``Last-Modified`` will also repeat the
value of ``last_modified``.

If the request header ``If-Modified-Since`` is provided, and if the record has not
changed meanwhile, a ``304 Not Modified`` is returned.

Example
-------

::

    http GET http://localhost:8000/v1/articles/30afb809ca7745a58496a09c6a4afcac \
        --auth "admin:" -v


.. code-block:: http

    GET /v1/articles/30afb809ca7745a58496a09c6a4afcac HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Host: localhost:8000
    User-Agent: HTTPie/0.8.0


    HTTP/1.1 200 OK
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Alert
    Content-Length: 597
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:22:38 GMT
    Last-Modified: 1425054146681
    Server: waitress

    {
        "added_by": "Natim",
        "added_on": 1425054146680,
        "archived": false,
        "excerpt": "",
        "favorite": false,
        "id": "30afb809ca7745a58496a09c6a4afcac",
        "is_article": true,
        "last_modified": 1425054146681,
        "marked_read_by": null,
        "marked_read_on": null,
        "read_position": 0,
        "resolved_title": "The Hawk Authorization protocol",
        "resolved_url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "stored_on": 1425054146680,
        "title": "The Hawk Authorization protocol",
        "unread": true,
        "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "word_count": null
    }


DELETE /articles/<id>
=====================

**Requires authentication**

Delete a specific record by its id.

The DELETE response is the record that was deleted.

If the record is missing (or already deleted), a ``404 Not Found`` is returned. The client might
decide to ignore it.

If the request header ``If-Unmodified-Since`` is provided, and if the record has
changed meanwhile, a ``412 Precondition failed`` error is returned.

:note:
    Once deleted, an article will appear in the collection with a deleted status
    (``deleted=true``) and will have most of its fields empty.


Example
-------

::

    http DELETE http://localhost:8000/v1/articles/ff795c43c02145a4b7a5df5260ee182d \
        --auth "admin:" -v

.. code-block:: http

    DELETE /v1/articles/ff795c43c02145a4b7a5df5260ee182d HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Content-Length: 0
    Host: localhost:8000
    User-Agent: HTTPie/0.8.0

    HTTP/1.1 200 OK
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Alert
    Content-Length: 87
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:21:00 GMT
    Server: waitress

    {
        "deleted": True,
        "id": "ff795c43c02145a4b7a5df5260ee182d",
        "last_modified": 1425054060041
    }


PATCH /articles/<id>
====================

**Requires authentication**

Modify a specific record by its id. The PATCH body is a JSON
mapping containing a subset of articles fields.

The PATCH response is the modified record (full).

Modifiable fields
-----------------

- ``title``
- ``excerpt``
- ``favorite``
- ``unread``
- ``archived``
- ``read_position``

Since article fields resolution is performed by the client in the first version
of the API, the following fields are also modifiable:

- ``is_article``
- ``resolved_url``
- ``resolved_title``

Response behavior
-----------------

On a ``PATCH`` it is possible to choose among different behaviors for the response content.

Three behaviors are available:

- ``full``: Returns the whole record (**default**).
- ``light``: Returns only the fields whose value was changed.
- ``diff``: Returns only the fields values that don't match those provided.

For example, using the default behavior :

::

    http PATCH http://localhost:8000/v1/articles/8412b7d7da40467e9afbad8b6f15c20f \
        unread=False marked_read_on=1425316211577 marked_read_by=Ipad \
        --auth 'Natim:' -v

.. code-block:: http
    :emphasize-lines: 15-35

    PATCH /v1/articles/8412b7d7da40467e9afbad8b6f15c20f HTTP/1.1
    Host: localhost:8000
    [...]

    {
        "marked_read_by": "Ipad", 
        "marked_read_on": "1425316211577", 
        "unread": "False"
    }

    HTTP/1.1 200 OK
    Content-Type: application/json; charset=UTF-8
    [...]

    {
        "added_by": "Natim", 
        "added_on": 1425383479321, 
        "archived": false, 
        "excerpt": "", 
        "favorite": false, 
        "id": "8412b7d7da40467e9afbad8b6f15c20f", 
        "is_article": true, 
        "last_modified": 1425383532546, 
        "marked_read_by": "Ipad", 
        "marked_read_on": 1425316211577, 
        "read_position": 0, 
        "resolved_title": "What’s Hawk authentication and how to use it?", 
        "resolved_url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/", 
        "stored_on": 1425383479321, 
        "title": "The Hawk Authorization protocol", 
        "unread": false, 
        "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/", 
        "word_count": null
    }


Using ``Response-Behavior: light``
::::::::::::::::::::::::::::::::::

::

    http PATCH http://localhost:8000/v1/articles/8412b7d7da40467e9afbad8b6f15c20f \
        unread=False marked_read_on=1425316211577 marked_read_by=Ipad \
        Response-Behavior:light \
        --auth 'Natim:' -v

.. code-block:: http
    :emphasize-lines: 3,16-20

    PATCH /v1/articles/8412b7d7da40467e9afbad8b6f15c20f HTTP/1.1
    Host: localhost:8000
    Response-Behavior: light
    [...]

    {
        "marked_read_by": "Ipad", 
        "marked_read_on": "1425316211577", 
        "unread": "False"
    }

    HTTP/1.1 200 OK
    [...]
    Content-Type: application/json; charset=UTF-8

    {
        "marked_read_by": "Ipad", 
        "marked_read_on": 1425316211577, 
        "unread": false
    }

Using ``Response-Behavior: diff``
:::::::::::::::::::::::::::::::::

::

    http PATCH http://localhost:8000/v1/articles/8412b7d7da40467e9afbad8b6f15c20f \
        unread=False marked_read_on=1425316211577 marked_read_by=Ipad \
        Response-Behavior:diff \
        --auth 'Natim:' -v

.. code-block:: http
    :emphasize-lines: 3,16

    PATCH /v1/articles/8412b7d7da40467e9afbad8b6f15c20f HTTP/1.1
    Host: localhost:8000
    Response-Behavior: diff
    [...]

    {
        "marked_read_by": "Ipad", 
        "marked_read_on": "1425316211577", 
        "unread": "False"
    }

    HTTP/1.1 200 OK
    Content-Type: application/json; charset=UTF-8
    [...]

    {}


Errors
------

If a read-only field is modified, a ``400 Bad request`` error is returned.

If the record is missing (or already deleted), a ``404 Not Found`` error is returned. The client might
decide to ignore it.

If the request header ``If-Unmodified-Since`` is provided, and if the record has
changed meanwhile, a ``412 Precondition failed`` error is returned.

:note:
    ``last_modified`` is updated to the current server timestamp, only if a
    field value was changed.

:note:
    Changing ``read_position`` never generates conflicts.

:note:
    ``read_position`` is ignored if the value is lower than the current one.

:note:
    If ``unread`` is changed to false, ``marked_read_on`` and ``marked_read_by``
    are expected to be provided.

:note:
    If ``unread`` was already false, ``marked_read_on`` and ``marked_read_by``
    are not updated with provided values.

:note:
    If ``unread`` is changed to true, ``marked_read_by``, ``marked_read_on``
    and ``read_position`` are reset to their default value.


Conflicts
---------

If changing the article ``resolved_url`` violates the unicity constraint, a
``409 Conflict`` error response is returned (see :ref:`error channel <_error-responses>`).

:note:

    Note that ``url`` is a readonly field, and thus cannot generate conflicts
    here.

Example
-------

::

    http PATCH http://localhost:8000/v1/articles/30afb809ca7745a58496a09c6a4afcac \
        title="What’s Hawk authentication and how to use it?" \
        If-Unmodified-Since:1425054146681 \
        --auth "admin:" -v

.. code-block:: http

    PATCH /v1/articles/30afb809ca7745a58496a09c6a4afcac HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Authorization: Basic YWRtaW46
    Content-Length: 63
    Content-Type: application/json; charset=utf-8
    Host: localhost:8000
    If-Unmodified-Since: 1425054146681
    User-Agent: HTTPie/0.8.0

    {
        "title": "What’s Hawk authentication and how to use it?"
    }

    HTTP/1.1 200 OK
    Access-Control-Expose-Headers: Backoff, Retry-After, Last-Modified, Alert
    Content-Length: 616
    Content-Type: application/json; charset=UTF-8
    Date: Fri, 27 Feb 2015 16:24:21 GMT
    Server: waitress

    {
        "added_by": "Natim",
        "added_on": 1425054146680,
        "archived": false,
        "excerpt": "",
        "favorite": false,
        "id": "30afb809ca7745a58496a09c6a4afcac",
        "is_article": true,
        "last_modified": 1425054261938,
        "marked_read_by": null,
        "marked_read_on": null,
        "read_position": 0,
        "resolved_title": "The Hawk Authorization protocol",
        "resolved_url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "stored_on": 1425054146680,
        "title": "What’s Hawk authentication and how to use it?",
        "unread": true,
        "url": "https://blog.mozilla.org/services/2015/02/05/whats-hawk-and-how-to-use-it/",
        "word_count": null
    }
