.. _resource-endpoints:

####################################
{{resource_name|capitalize}} endpoints
####################################

All :term:`endpoints` URLs are prefixed by the major version of the :term:`HTTP API`
(e.g /v1 for 1.4).

e.g. the URL for all the endpoints is structured as follows:::

    https://<server name>/<api MAJOR version>/<further instruction>


The full URL prefix will be implied throughout the rest of this document and
it will only describe the **<further instruction>** part.

{% block collection_get %}

GET {{collection_url}}
===={{ "=" * collection_url|count}}

{% block collection_get_description %}
**Requires authentication**

Returns all {{record_name}}s of the current user for this collection.
{% endblock collection_get_description %}

The returned value is a JSON mapping containing:

- ``data``: the list of {{record_name}}s, with exhaustive fields;

A ``Total-Records`` response header indicates the total number of {{record_name}}s
of the {{collection_name}}.

A ``Last-Modified`` response header provides a human-readable (rounded to second)
of the current {{collection_name}} timestamp.

For cache and concurrency control, an ``ETag`` response header gives the
value that consumers can provide in subsequent requests using ``If-Match``
and ``If-None-Match`` headers (see :ref:`section about timestamps <server-timestamps>`).

**Request**:

.. code-block:: http

    GET {{collection_example_url}} HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Host: localhost:8000

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length, ETag, Next-Page, Total-Records, Last-Modified
    Content-Length: 436
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:08:11 GMT
    Last-Modified: Mon, 12 Apr 2015 11:12:07 GMT
    ETag: "1430222877724"
    Total-Records: 2

    {
        "data": [
            {
                "id": "dc86afa9-a839-4ce1-ae02-3d538b75496f",
                "last_modified": 1430222877724,
                "title": "MoCo",
                "url": "https://mozilla.com",
            },
            {
                "id": "23160c47-27a5-41f6-9164-21d46141804d",
                "last_modified": 1430140411480,
                "title": "MoFo",
                "url": "https://mozilla.org",
            }
        ]
    }


Filtering
---------

**Single value**

* ``{{collection_url}}?field=value``

.. **Multiple values**
..
.. * ``{{collection_url}}?field=1,2``

**Minimum and maximum**

Prefix attribute name with ``min_`` or ``max_``:

* ``{{collection_url}}?min_field=4000``

.. note::

    The lower and upper bounds are inclusive (*i.e equivalent to
    greater or equal*).

.. note::

   ``lt_`` and ``gt_`` can also be used to exclude the bound.

**Multiple values**

Prefix attribute with ``in_`` and provide comma-separated values.

* ``{{collection_url}}?in_status=1,2,3``

**Exclude**

Prefix attribute name with ``not_``:

* ``{{collection_url}}?not_field=0``

**Exclude multiple values**

Prefix attribute name with ``exclude_``:

* ``{{collection_url}}?exclude_field=0,1``

{% if with_schema %}
.. note::

    Will return an error if a field is unknown.
{% endif %}

.. note::

    The ``ETag`` and ``Last-Modified`` response headers will always be the same as
    the unfiltered collection.

Sorting
-------

* ``{{collection_url}}?_sort=-last_modified,field``

.. note::

    Ordering on a boolean field gives ``true`` values first.

{% if with_schema %}
.. note::

    Will return an error if a field is unknown.
{% endif %}


Counting
--------

In order to count the number of {{record_name}}s, for a specific field value for example,
without fetching the actual collection, a ``HEAD`` request can be
used. The ``Total-Records`` response header will then provide the
total number of records.

See :ref:`batch endpoint <batch>` to count several collections in one request.


Polling for changes
-------------------

The ``_since`` parameter is provided as an alias for ``gt_last_modified``.

* ``{{collection_url}}?_since=1437035923844``

When filtering on ``last_modified`` every deleted {{record_name}}s will appear in the
list with a ``deleted`` flag and a ``last_modified`` value that corresponds
to the deletion event.

If the request header ``If-None-Match`` is provided as described in
the :ref:`section about timestamps <server-timestamps>` and if the
{{collection_name}} was not changed, a ``304 Not Modified`` response is returned.

.. note::

   The ``_before`` parameter is also available, and is an alias for
   ``lt_last_modified`` (*strictly inferior*).

.. note::

    ``_since`` and ``_before`` also accept a value between quotes (``"``) as
    it would be returned in the ``ETag`` response header
    (see :ref:`response timestamps <server-timestamps>`).

**Request**:

.. code-block:: http

    GET {{collection_example_url}}?_since=1437035923844 HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Host: localhost:8000

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length, ETag, Next-Page, Total-Records, Last-Modified
    Content-Length: 436
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:08:11 GMT
    Last-Modified: Mon, 12 Apr 2015 11:12:07 GMT
    ETag: "1430222877724"
    Total-Records: 2

    {
        "data": [
            {
                "id": "dc86afa9-a839-4ce1-ae02-3d538b75496f",
                "last_modified": 1430222877724,
                "title": "MoCo",
                "url": "https://mozilla.com",
            },
            {
                "id": "23160c47-27a5-41f6-9164-21d46141804d",
                "last_modified": 1430140411480,
                "title": "MoFo",
                "url": "https://mozilla.org",
            },
            {
                "id": "11130c47-37a5-41f6-9112-32d46141804f",
                "deleted": true,
                "last_modified": 1430140411480
            }
        ]
    }


Paginate
--------

If the ``_limit`` parameter is provided, the number of {{record_name}}s returned is limited.

If there are more {{record_name}}s for this {{collection_name}} than the limit, the
response will provide a ``Next-Page`` header with the URL for the
Next-Page.

When there is no more ``Next-Page`` response header, there is nothing
more to fetch.

Pagination works with sorting, filtering and polling.

.. note::

    The ``Next-Page`` URL will contain a continuation token (``_token``).

    It is recommended to add precondition headers (``If-Match`` or
    ``If-None-Match``), in order to detect changes on collection while
    iterating through the pages.

Partial response
----------------

If the ``_fields`` parameter is provided, only the fields specified are returned.
Fields are separated with a comma. It is currently not possible to ask
for nested fields.

This is vital in mobile contexts where bandwidth usage must be optimized.

Nested objects fields are specified using dots (e.g. ``address.street``).

.. note::

    The ``id`` and ``last_modified`` fields are always returned.


**Request**:

.. code-block:: http

    GET {{collection_example_url}}?_fields=title,url
    Accept: application/json
    Authorization: Basic bWF0Og==
    Host: localhost:8000

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length, ETag, Next-Page, Total-Records, Last-Modified
    Content-Length: 436
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:08:11 GMT
    Last-Modified: Mon, 12 Apr 2015 11:12:07 GMT
    ETag: "1430222877724"
    Total-Records: 2

    {
        "data": [
            {
                "id": "dc86afa9-a839-4ce1-ae02-3d538b75496f",
                "last_modified": 1430222877724,
                "title": "MoCo",
                "url": "https://mozilla.com",
            },
            {
                "id": "23160c47-27a5-41f6-9164-21d46141804d",
                "last_modified": 1430140411480,
                "title": "MoFo",
                "url": "https://mozilla.org",
            }
        ]
    }


List of available URL parameters
--------------------------------

- ``<prefix?><attribute name>``: filter by value(s)
- ``_since``, ``_before``: polling changes
- ``_sort``: order list
- ``_limit``: pagination max size
- ``_token``: pagination token
- ``_fields``: filter the fields of the records


Filtering, sorting, partial responsses and paginating can all be combined together.

* ``{{collection_url}}?_sort=-last_modified&_limit=100&_fields=title``


HTTP Status Codes
-----------------

* ``200 OK``: The request was processed
* ``304 Not Modified``: {{resource_name}} did not change since value in ``If-None-Match`` header
* ``400 Bad Request``: The request querystring is invalid
* ``412 Precondition Failed``: {{resource_name}} changed since value in ``If-Match`` header

{% endblock collection_get %}


{% block collection_post %}

POST {{collection_url}}
====={{ "=" * collection_url|count}}

{% block collection_post_description %}
**Requires authentication**

Used to create a record in the collection.
{% endblock collection_post_description %}

The POST body is a JSON mapping containing:

- ``data``: the values of the fields;
- ``permissions``: *optional* a json dict containing the permissions for
  the {{record_name}} to be created.

The POST response body is a JSON mapping containing:

- ``data``: the newly created {{record_name}}, if all posted values are valid;
- ``permissions``: *optional* a json dict containing the permissions for
  the created {{record_name}}.

If the request header ``If-Match`` is provided, and if the {{collection_name}} has
changed meanwhile, a ``412 Precondition failed`` error is returned.


**Request**:

.. code-block:: http

    POST {{collection_example_url}} HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Content-Type: application/json; charset=utf-8
    Host: localhost:8000

    {
        "data": {
            "title": "Wikipedia FR",
            "url": "http://fr.wikipedia.org"
        }
    }

**Response**:

.. code-block:: http

    HTTP/1.1 201 Created
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length
    Content-Length: 422
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:35:02 GMT

    {
        "data": {
            "id": "cd30c031-c208-4fb9-ad65-1582d2a7ad5e",
            "last_modified": 1430224502529,
            "title": "Wikipedia FR",
            "url": "http://fr.wikipedia.org"
        }
    }


Validation
----------

If the posted values are invalid (e.g. *field value is not an integer*)
an error response is returned with status ``400``.

See :ref:`details on error responses <error-responses>`.

Conflicts
---------

Since some fields can be defined as unique per collection, some conflicts
may appear when creating records.

.. note::

    Empty values are not taken into account for field unicity.

.. note::

    Deleted records are not taken into account for field unicity.

If a conflict occurs, an error response is returned with status ``409``.
A ``details`` attribute in the response provides the offending record and
field name. See :ref:`dedicated section about errors <error-responses>`.


Timestamp
---------

When a record is created, the timestamp of the collection is incremented.

It is possible to force the timestamp if the specified record has a
``last_modified`` attribute.

If the specified timestamp is in the past, the collection timestamp does not
take the value of the created record but is bumped into the future as usual.


HTTP Status Codes
-----------------

* ``200 OK``: This record already exists, here is the one stored on the database;
* ``201 Created``: The record was created
* ``400 Bad Request``: The request body is invalid
* ``406 Not Acceptable``: The client doesn't accept supported responses Content-Type.
* ``409 Conflict``: Unicity constraint on fields is violated
* ``412 Precondition Failed``: Collection changed since value in ``If-Match`` header
* ``415 Unsupported Media Type``: The client request was not sent with a correct Content-Type.

{% endblock collection_post %}


{% block collection_delete %}

DELETE {{collection_url}}
======={{ "=" * collection_url|count}}

{% block collection_delete_description %}
**Requires authentication**

Delete multiple records. **Disabled by default**, see :ref:`configuration`.
{% endblock collection_delete_description %}

The DELETE response is a JSON mapping containing:

- ``data``: list of {{record_name}}s that were deleted, without attributes fields.

It supports the same filtering capabilities as GET.

If the request header ``If-Match`` is provided, and if the {{resource_name}}
has changed meanwhile, a ``412 Precondition failed`` error is returned.


**Request**:

.. code-block:: http

    DELETE {{collection_example_url}} HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Host: localhost:8000

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length
    Content-Length: 193
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:38:36 GMT

    {
        "data": [
            {
                "deleted": true,
                "id": "cd30c031-c208-4fb9-ad65-1582d2a7ad5e",
                "last_modified": 1430224716097
            },
            {
                "deleted": true,
                "id": "dc86afa9-a839-4ce1-ae02-3d538b75496f",
                "last_modified": 1430224716098
            }
        ]
    }


HTTP Status Codes
-----------------

* ``200 OK``: The records were deleted;
* ``405 Method Not Allowed``: This endpoint is not available;
* ``406 Not Acceptable``: The client doesn't accept supported responses Content-Type.
* ``412 Precondition Failed``: Collection changed since value in ``If-Match`` header

{% endblock collection_delete %}

{% block record_get %}

GET {{collection_url}}/<id>
===={{"=" * collection_url|count}}=====


{% block record_get_description %}
**Requires authentication**

Returns a specific record by its id.
{% endblock record_get_description %}

The GET response body is a JSON mapping containing:
- ``data``: the {{record_name}} with exhaustive schema fields;
- ``permissions``: *optional* a json dict containing the permissions for
  the requested record.

If the request header ``If-None-Match`` is provided, and if the {{record_name}} has not
changed meanwhile, a ``304 Not Modified`` is returned.

**Request**:

.. code-block:: http

    GET {{collection_example_url}}/d10405bf-8161-46a1-ac93-a1893d160e62 HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Host: localhost:8000

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length, ETag, Last-Modified
    Content-Length: 438
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:42:42 GMT
    ETag: "1430224945242"

    {
        "data": {
            "id": "d10405bf-8161-46a1-ac93-a1893d160e62",
            "last_modified": 1430224945242,
            "title": "No backend",
            "url": "http://nobackend.org"
        }
    }

HTTP Status Code
----------------

* ``200 OK``: The request was processed
* ``304 Not Modified``: {{record_name|capitalize}} did not change since value in ``If-None-Match`` header
* ``412 Precondition Failed``: {{record_name|capitalize}} changed since value in ``If-Match`` header

{% endblock record_get %}


{% block record_delete %}

DELETE {{collection_url}}/<id>
======={{"=" * collection_url|count}}=====

{% block record_delete_description %}
**Requires authentication**

Delete a specific record by its id.
{% endblock record_delete_description %}

The DELETE response is a JSON mapping containing:

- ``data``: the {{record_name}} that was deleted, without attributes fields.

If the {{record_name}} is missing (or already deleted), a ``404 Not Found`` is returned.
The consumer might decide to ignore it.

If the request header ``If-Match`` is provided, and if the {{record_name}} has
changed meanwhile, a ``412 Precondition failed`` error is returned.

The timestamp value of the deleted {{record_name}} can be enforced via the
``last_modified`` QueryString parameter.

.. note::

    Once deleted, a {{record_name}} will appear in the {{collection_name}} when polling for changes,
    with a deleted status (``delete=true``) and will have its fields erased.

{% if cliquet_changes %}
.. versionadded:: 2.13::

  Enforcement of the timestamp value for {{record_name}}s has been added.
{% endif %}

HTTP Status Code
----------------

* ``200 OK``: The {{record_name}} was deleted
* ``412 Precondition Failed``: The {{record_name}} changed since value in ``If-Match`` header

{% endblock record_delete %}

{% block record_put %}

PUT {{collection_url}}/<id>
===={{"=" * collection_url|count}}=====


{% block record_put_description %}
**Requires authentication**
Create or replace a {{record_name}} with its id.
{% endblock record_put_description %}

The PUT body is a JSON mapping containing:

- ``data``: the values of the attributes fields;
- ``permissions``: *optional* a json dict containing the permissions for
  the {{record_name}} to be created/replaced.

The PUT response body is a JSON mapping containing:

- ``data``: the newly created/updated {{record_name}}, if all posted values are valid;
- ``permissions``: *optional* the newly created permissions dict, containing
  the permissions for the created/updated {{record_name}}.

Validation and conflicts behaviour is similar to creating {{record_name}}s (``POST``).

If the request header ``If-Match`` is provided, and if the {{record_name}} has
changed meanwhile, a ``412 Precondition failed`` error is returned.

{% if cliquet_changes %}
.. versionadded:: 2.13::

  Enforcement of the timestamp value for {{record_name}}s has been added.
{% endif %}

**Request**:

.. code-block:: http

    PUT {{collection_example_url}}/d10405bf-8161-46a1-ac93-a1893d160e62 HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Content-Type: application/json; charset=utf-8
    Host: localhost:8000

    {
        "data": {
            "title": "Static apps",
            "url": "http://www.staticapps.org"
        }
    }

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length
    Content-Length: 439
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:46:36 GMT
    ETag: "1430225196396"

    {
        "data": {
            "id": "d10405bf-8161-46a1-ac93-a1893d160e62",
            "last_modified": 1430225196396,
            "title": "Static apps",
            "url": "http://www.staticapps.org"
        }
    }


Timestamp
---------

When a record is created or replaced, the timestamp of the collection is incremented.

It is possible to force the timestamp if the specified record has a
``last_modified`` attribute.

For replace, if the specified timestamp is less or equal than the existing record,
the value is simply ignored and the timestamp is bumped into the future as usual.

For creation, if the specified timestamp is in the past, the collection timestamp does not
take the value of the created/updated record but is bumped into the future as usual.


HTTP Status Code
----------------

* ``201 Created``: The {{record_name}} was created
* ``200 OK``: The {{record_name}} was replaced
* ``400 Bad Request``: The {{record_name}} is invalid
* ``409 Conflict``: If replacing this {{record_name}} violates a field unicity constraint
* ``412 Precondition Failed``: The {{record_name}} was changed or deleted since value
  in ``If-Match`` header.
* ``415 Unsupported Media Type``: The client request was not sent with a correct Content-Type.

.. note::

    A ``If-None-Match: *`` request header can be used to make sure the ``PUT``
    won't overwrite any {{record_name}}.

{% endblock record_put %}

{% block record_patch %}

PATCH /{collection}/<id>
======{{"=" * collection_url|count}}=====

{% block record_patch_description %}
**Requires authentication**

Modify a specific {{record_name}} by its id.
{% endblock record_patch_description %}

The PATCH body is a JSON mapping containing:

- ``data``: a subset of the attributes fields (*key-value replace*);
- ``permissions``: *optional* a json dict containing the permissions for
  the {{record_name}} to be modified.

The PATCH response body is a JSON mapping containing:

- ``data``: the modified {{record_name}} (*full by default*);
- ``permissions``: *optional* the modified permissions dict, containing
  the permissions for the modified {{record_name}}.

If a request header ``Response-Behavior`` is set to ``light``,
only the fields whose value was changed are returned. If set to
``diff``, only the fields whose value became different than
the one provided are returned.

**Request**:

.. code-block:: http

    PATCH {{collection_example_url}}/d10405bf-8161-46a1-ac93-a1893d160e62 HTTP/1.1
    Accept: application/json
    Authorization: Basic bWF0Og==
    Content-Type: application/json; charset=utf-8
    Host: localhost:8000

    {
        "data": {
            "title": "No Backend"
        }
    }

**Response**:

.. code-block:: http

    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: *
    Access-Control-Expose-Headers: Backoff, Retry-After, Alert, Content-Length
    Content-Length: 439
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 28 Apr 2015 12:46:36 GMT
    ETag: "1430225196396"

    {
        "data": {
            "id": "d10405bf-8161-46a1-ac93-a1893d160e62",
            "last_modified": 1430225196396,
            "title": "No Backend",
            "url": "http://nobackend.org"
        }
    }


If the {{record_name}} is missing (or already deleted), a ``404 Not Found`` error is returned.
The consumer might decide to ignore it.

If the request header ``If-Match`` is provided, and if the {{record_name}} has
changed meanwhile, a ``412 Precondition failed`` error is returned.

.. note::

    ``last_modified`` is updated to the current server timestamp, only if a
    field value was changed.

.. note::

    `JSON-Patch <http://jsonpatch.com>`_ is currently not
    supported. Any help is welcomed though!

{% if with_readonly %}
Read-only fields
----------------

If a read-only field is modified, a ``400 Bad request`` error is returned.
{% endif %}

Conflicts
---------

If changing a {{record_name}} field violates a field unicity constraint, a
``409 Conflict`` error response is returned (see :ref:`error channel <error-responses>`).


Timestamp
---------

When a record is modified, the timestamp of the collection is incremented.

It is possible to force the timestamp if the specified record has a
``last_modified`` attribute.

If the specified timestamp is less or equal than the existing record,
the value is simply ignored and the timestamp is bumped into the future as usual.


HTTP Status Code
----------------

* ``200 OK``: The {{record_name}} was modified
* ``400 Bad Request``: The request body is invalid{% if with_readonly %}, or a read-only field was modified{% endif %}
* ``406 Not Acceptable``: The client doesn't accept supported responses Content-Type.
* ``409 Conflict``: If modifying this {{record_name}} violates a field unicity constraint
* ``412 Precondition Failed``: The {{record_name}} changed since value in ``If-Match`` header
* ``415 Unsupported Media Type``: The client request was not sent with a correct Content-Type.

{% endblock record_patch %}

.. _resource-permissions-attribute:

Notes on permissions attribute
==============================

Shareable resources allow :term:`permissions` management via the ``permissions`` attribute
in the JSON payloads, along the ``data`` attribute. Permissions can be replaced
or modified independently from data.

On a request, ``permissions`` is a JSON dict with the following structure::

    "permissions": {<permission>: [<list_of_principals>]}

Where ``<permission>`` is the permission name (e.g. ``read``, ``write``)
and ``<list_of_principals>`` should be replaced by an actual list of
:term:`principals`.

Example:

::

    {
        "data": {
            "title": "No Backend"
        },
        "permissions": {
            "write": ["twitter:leplatrem", "group:ldap:42"],
            "read": ["system.Authenticated"]
        }
    }


In a response, ``permissions`` contains the current permissions of the {{record_name}}
(i.e. the *modified* version in case of a creation/modification).

.. note::

    When a {{record_name}} is created or modified, the current :term`user id`
    **is always added** among the ``write`` principals.

`Read more about leveraging resource permissions <resource-permissions>`.


.. versionchanged:: 2.6::

    With a ``PATCH`` request, the list of principals for the specified permissions
    is now replaced by the one provided.
