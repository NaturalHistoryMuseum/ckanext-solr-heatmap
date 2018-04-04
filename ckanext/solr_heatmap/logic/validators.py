# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-solr-heatmap
# Created by the Natural History Museum in London, UK

from ckanext.solr_heatmap.lib import get_datastore_geospatial_fields

from ckan.plugins import toolkit


def is_datastore_geospatial_field(value, context):
    '''Validation function
    Ensure field name exists in the resource datastore

    :param value: field name
    :param context: return:

    '''
    fields = get_datastore_geospatial_fields(context[u'resource'].id, context)
    #  Convert substring to a list, so we can use same process
    # For multiple select
    if value:
        value_list = [value] if isinstance(value, basestring) else value
        # Loop through values, making sure they're in the datastore
        for v in value_list:
            if v not in fields:
                raise toolkit.Invalid(
                    toolkit._(u'Field not found in datastore')
                    )
    return value
