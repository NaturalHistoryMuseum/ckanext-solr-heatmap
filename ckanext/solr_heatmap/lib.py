#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '24/08/2017'.
"""

import ckan.plugins.toolkit as toolkit


def get_datastore_geospatial_fields(resource_id, context):
    """
    Get all fields of type geospatial_rpt
    @param resource_id:
    @param context:
    @return:
    """
    data = {'resource_id': resource_id, 'limit': 0}
    try:
        fields = toolkit.get_action('datastore_search')(context, data)['fields']
    except toolkit.ObjectNotFound:
        # if the resource isn't found in the solr datastore (or indeed the
        # standard datastore which the solr datastore action passes off to)
        # that's fine, but we should catch the error
        return []
    else:
        return sorted([f['id'] for f in fields if f['type'] == 'geospatial_rpt'])
