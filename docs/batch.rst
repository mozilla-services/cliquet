################
Batch operations
################

.. _batch:

POST /batch
===========

**Requires an FxA OAuth authentication**

The POST body is a mapping, with the following attributes:

- ``requests``: the list of requests (*limited to 25 by default*)
- ``defaults``: (*optional*) default requests values in common for all requests

 Each request is a JSON mapping, with the following attribute:

- ``method``: HTTP verb
- ``path``: URI
- ``body``: a mapping
- ``headers``: (*optional*), otherwise take those of batch request

::

    {
      "defaults": {
        "method" : "POST",
        "path" : "/articles",
        "headers" : {
          ...
        }
      },
      "requests": [
        {
          "body" : {
            "title": "MoFo",
            "url" : "http://mozilla.org",
            "added_by": "FxOS",
          }
        },
        {
          "body" : {
            "title": "MoCo",
            "url" : "http://mozilla.com"
            "added_by": "FxOS",
          }
        },
        {
          "method" : "PATCH",
          "path" : "/articles/409",
          "body" : {
            "read_position" : 3477
          }
        }
      ]
    ]


The response body is a list of all responses:

::

    {
      "responses": [
        {
          "path" : "/articles/409",
          "status": 200,
          "body" : {
            "id": 409,
            "url": "...",
            ...
            "read_position" : 3477
          },
          "headers": {
            ...
          }
        },
        {
          "status": 201,
          "path" : "/articles",
          "body" : {
            "id": 411,
            "title": "MoFo",
            "url" : "http://mozilla.org",
            ...
          },
        },
        {
          "status": 201,
          "path" : "/articles",
          "body" : {
            "id": 412,
            "title": "MoCo",
            "url" : "http://mozilla.com",
            ...
          },
        },
      ]
    ]


:warning:

    Since the requests bodies are necessarily mappings, posting arbitrary data
    (*like raw text or binary*)is not supported.

:note:

     Responses are provided in the same order than requests.

:note:

    A form of payload optimization for massive operations is planned.
