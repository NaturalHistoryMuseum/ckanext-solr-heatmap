# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-solr-heatmap
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


def get_datastore_geospatial_fields(resource_id, context):
    '''Get all fields of type geospatial_rpt

    :param resource_id: param context:
    :param context: 

    '''
    data = {
        u'resource_id': resource_id,
        u'limit': 0
        }
    try:
        fields = toolkit.get_action(u'datastore_search')(context, data)[u'fields']
    except toolkit.ObjectNotFound:
        # if the resource isn't found in the solr datastore (or indeed the
        # standard datastore which the solr datastore action passes off to)
        # that's fine, but we should catch the error
        return []
    else:
        return sorted([f[u'id'] for f in fields if f[u'type'] == u'geospatial_rpt'])
