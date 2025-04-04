# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Records-REST configuration."""

from flask import request
from invenio_i18n import lazy_gettext as _
from invenio_indexer.api import RecordIndexer
from invenio_search import RecordsSearch

from .facets import terms_filter
from .utils import allow_all, check_search, deny_all

RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type="recid",
        pid_minter="recid",
        pid_fetcher="recid",
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index=None,
        search_query_parser=None,
        record_serializers={
            "application/json": (
                "invenio_records_rest.serializers" ":json_v1_response"
            ),
        },
        search_serializers={
            "application/json": ("invenio_records_rest.serializers" ":json_v1_search"),
        },
        list_route="/records/",
        item_route="/records/<pid(recid):pid_value>",
        default_media_type="application/json",
        max_result_window=10000,
        error_handlers=dict(),
    ),
)
"""Default REST endpoints loaded.

This option can be overwritten to describe the endpoints of different
record types. Each endpoint is in charge of managing all its CRUD operations
(GET, POST, PUT, DELETE, ...).

The structure of the dictionary is as follows:

.. code-block:: python

    from flask import abort
    from flask_security import current_user
    from invenio_records_rest.query import es_search_factory
    from invenio_records_rest.errors import PIDDeletedRESTError


    def search_factory(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        return es_search_factory(*args, **kwargs)


    def permission_check_factory():
        def check_title(record, *args, **kwargs):
            def can(self):
                if record['title'] == 'Hello World':
                    return True
            return type('Check', (), {'can': can})()

    def deleted_pid_error_handler(error):
        record = error.pid_error.record or {}
        return make_response(jsonify({
            'status': 410,
            'message': error.description,
            'removal_reason': record.get('removal_reason')}), 410)

    def query_parser_with_and(qstr=None):
        if qstr:
            return dsl.Q("query_string", query=qstr, default_operator="AND")
        return dsl.Q()


    RECORDS_REST_ENDPOINTS = {
        'endpoint-prefix': {
            'create_permission_factory_imp': permission_check_factory(),
            'default_endpoint_prefix': True,
            'default_media_type': 'application/json',
            'delete_permission_factory_imp': permission_check_factory(),
            'item_route': ('/records/<pid(record-pid-type, '
                           'record_class="mypackage.api:MyRecord"):pid_value>'),
            'links_factory_imp': ('invenio_records_rest.links:'
                                  'default_links_factory'),
            'list_route': '/records/',
            'max_result_window': 10000,
            'pid_fetcher': '<registered-pid-fetcher>',
            'pid_minter': '<registered-minter-name>',
            'pid_type': '<record-pid-type>',
            'list_permission_factory_imp': permission_check_factory(),
            'read_permission_factory_imp': permission_check_factory(),
            'record_class': 'mypackage.api:MyRecord',
            'record_loaders': {
                'application/json': 'mypackage.loaders:json_loader'
            },
            'record_serializers': {
                'application/json': 'mypackage.utils:my_json_serializer'
            },
            'record_serializers_aliases': {
                'json': 'application/json'
            },
            'search_class': 'mypackage.utils:mysearchclass',
            'search_factory_imp': search_factory(),
            'search_index': 'search-index-name',
            'search_query_parser': query_parser_with_and,
            'search_serializers': {
                'application/json': 'mypackage.utils:my_json_search_serializer'
            },
            'search_serializers_aliases': {
                'json': 'application/json'
            },
            'suggesters': {
                'my_url_param_to_complete': {
                    '_source': ['specified_source_filtered_field'],
                    'completion': {
                        'field': 'suggest_byyear_search_field',
                        'size': 10,
                        'context': 'year'
                    }
                },
            },
            'update_permission_factory_imp': permission_check_factory(),
            'use_options_view': True,
            'error_handlers': {
                PIDDeletedRESTError: deleted_pid_error_handler,
            },
        },
    }

:param create_permission_factory_imp: Import path to factory that create
    permission object for a given record.

:param default_endpoint_prefix: declare the current endpoint as the default
    when building endpoints for the defined ``pid_type``. By default the
    default prefix is defined to be the value of ``pid_type``.

:param default_media_type: Default media type for both records and search.

:param delete_permission_factory_imp: Import path to factory that creates a
    delete permission object for a given record.

:param item_route: URL rule for a single record.

:param links_factory_imp: Factory for record links generation.

:param list_route: Base URL for the records endpoint.

:param max_result_window: Maximum total number of records retrieved from a
    query.

:param pid_type: It specifies the record pid type. Required.
    You can generate an URL to list all records of the given ``pid_type`` by
    calling ``url_for('invenio_records_rest.{0}_list'.format(
    current_records_rest.default_endpoint_prefixes[pid_type]))``.

:param pid_fetcher: It identifies the registered fetcher name. Required.

:param pid_minter: It identifies the registered minter name. Required.

:param list_permission_factory_imp: Import path to factory that creates a
    list permission object for a given index / list.

:param read_permission_factory_imp: Import path to factory that creates a
    read permission object for a given record.

:param record_class: A record API class or importable string.

:param record_loaders: It contains the list of record deserializers for
    supported formats.

:param record_serializers: It contains the list of record serializers for
    supported formats.

:param record_serializers_aliases: A mapping of values of the defined query arg
    (see `config.REST_MIMETYPE_QUERY_ARG_NAME`) to valid mimetypes for record
    item serializers: dict(alias -> mimetype).

:param search_class: Import path or class object for the object in charge of
    execute the search queries. The default search class is
    :class:`invenio_search.api.RecordsSearch`.
    For more information about resource loading, see the `Search
    <http://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html>` of the
    the search engine DSL library.

:param search_factory_imp: Factory to parse queries.

:param search_index: Name of the search index used when searching records.

:param search_query_parser: Name of the function that will be used to parse the
    query. The default parser does an 'OR' of all the terms that have been
    specified. This could be used to do, as an example, and 'AND' of the terms.

:param search_serializers: It contains the list of records serializers for all
    supported format. This configuration differ from the previous because in
    this case it handle a list of records resulted by a search query instead of
    a single record.

:param search_serializers_aliases: A mapping of values of the defined query arg
    (see `config.REST_MIMETYPE_QUERY_ARG_NAME`) to valid mimetypes for records
    search serializers: dict(alias -> mimetype).

:param suggesters: Suggester fields configuration. Any element of the
    dictionary represents a suggestion field. For each suggestion field we can
    optionally specify the source filtering (appropriate for ES5) by using
    ``_source``. The key of the dictionary element is used to identify the url
    query parameter. The ``field`` parameter identifies the suggester field
    name in your search engine schema.
    To have more information about suggestion configuration, you can read
    suggesters section on the search engine documentation.

    .. note:: Only completion suggesters are supported.

:param update_permission_factory_imp: Import path to factory that creates a
    update permission object for a given record.

:param use_options_view: Determines if a special option view should be
    installed.

:param error_handlers: Error handlers configuration for the endpoint. The
    dictionary has an exception type or HTTP status code as a key and a
    function or an import path to a function as a value. The function will be
    passed as an argument to :meth:`flask.Blueprint.register_error_handler`, so
    it should take the handled exception/code as its single argument.

"""

RECORDS_REST_DEFAULT_LOADERS = {
    "application/json": lambda: request.get_json(),
    "application/json-patch+json": lambda: request.get_json(force=True),
}
"""Default data loaders per request mime type.

This option can be overritten in each REST endpoint as follows:

.. code-block:: python

    RECORDS_REST_ENDPOINTS = {
        'recid': {
            ...
            'record_loaders': {
                'application/json': 'mypackage.utils:myloader',
            },
            ...
        }
    }

"""

RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_("Best match"),
            fields=["_score"],
            default_order="desc",
            order=1,
        ),
        mostrecent=dict(
            title=_("Most recent"),
            fields=["-_created"],
            default_order="asc",
            order=2,
        ),
    )
)
"""Sort options for default sorter factory.

The structure of the dictionary is as follows:

.. code-block:: python

    RECORDS_REST_SORT_OPTIONS = {
        '<index or index alias>': {
            '<sort-field-name>': {
                'fields': ['<search_field>', '<search_field>', ...],
                'title': '<title displayed to end user in search-ui>',
                'default_order': '<default sort order in search-ui>',
            }
        }
    }

Each search field can be either:

- A string of the form ``'<field name>'`` (ascending) or ``'-<field name>'``
  (descending).
- A dictionary with search engine sorting syntax (e.g.
  ``{'price' : {'order' : 'asc', 'mode' : 'avg'}}``).
- A callable taking one boolean parameter (``True`` for ascending and ``False``
  for descending) and returning a dictionary like above. This is useful if you
  need to extract extra sorting parameters (e.g. for geo location searches).
"""

RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query="bestmatch",
        noquery="mostrecent",
    )
)
"""Default sort option per index with/without query string.

The structure of the dictionary is as follows:

.. code-block:: python

    RECORDS_REST_DEFAULT_SORT = {
        '<index or index alias>': {
            'query': '<default-sort-if-a-query-is-passed-from-url>',
            'noquery': '<default-sort-if-no-query-in-passed-from-url>',
        }
    }
"""

RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(type=dict(terms=dict(field="type"))),
        post_filters=dict(
            type=terms_filter("type"),
        ),
    )
)
"""Facets per index for the default facets factory.

The structure of the dictionary is as follows:

.. code-block:: python

    RECORDS_REST_FACETS = {
        '<index or index alias>': {
            'aggs': {
                '<key>': <aggregation definition>,
                ...
            }
            'filters': {
                '<key>': <filter func>,
                ...
            }
            'post_filters': {
                '<key>': <filter func>,
                ...
            }
        }
    }
"""

RECORDS_REST_FACETS_POST_FILTERS_PROPAGATE = False
"""Define if the post_filters facets in one category should be applied as filters to all the other categories"""

RECORDS_REST_DEFAULT_CREATE_PERMISSION_FACTORY = deny_all
"""Default create permission factory: reject any request."""

RECORDS_REST_DEFAULT_LIST_PERMISSION_FACTORY = allow_all
"""Default list permission factory: allow all requests"""

RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY = check_search
"""Default read permission factory: check if the record exists."""

RECORDS_REST_DEFAULT_UPDATE_PERMISSION_FACTORY = deny_all
"""Default update permission factory: reject any request."""

RECORDS_REST_DEFAULT_DELETE_PERMISSION_FACTORY = deny_all
"""Default delete permission factory: reject any request."""

RECORDS_REST_SEARCH_ERROR_HANDLERS = {
    "query_parsing_exception": (
        "invenio_records_rest.views" ":search_query_parsing_exception_handler"
    ),
    "query_shard_exception": (
        "invenio_records_rest.views" ":search_query_parsing_exception_handler"
    ),
}

RECORDS_REST_DEFAULT_RESULTS_SIZE = 10
"""Default search results size."""
