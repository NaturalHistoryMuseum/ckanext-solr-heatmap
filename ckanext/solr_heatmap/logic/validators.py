#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '24/08/2017'.
"""

from ckanext.solr_heatmap.lib import get_datastore_geospatial_fields
import ckan.plugins as p
from ckan.common import _


Invalid = p.toolkit.Invalid


def is_datastore_geospatial_field(value, context):
    """
    Validation function
    Ensure field name exists in the resource datastore
    @param value:  field name
    @param context:
    @return:
    """
    fields = get_datastore_geospatial_fields(context['resource'].id, context)
    #  Convert substring to a list, so we can use same process
    # For multiple select
    if value:
        value_list = [value] if isinstance(value, basestring) else value
        # Loop through values, making sure they're in the datastore
        for v in value_list:
            if v not in fields:
                raise Invalid(
                    _('Field not found in datastore')
                )
    return value