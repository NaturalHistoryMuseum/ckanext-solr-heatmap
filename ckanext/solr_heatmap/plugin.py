#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-solr-heatmap
# Created by the Natural History Museum in London, UK

import ckan.plugins as p
from ckan.common import json

from ckanext.datasolr.interfaces import IDataSolr

from ckanext.solr_heatmap.config import config as plugin_config
from ckanext.solr_heatmap.logic.validators import is_datastore_geospatial_field
from ckanext.solr_heatmap.lib import get_datastore_geospatial_fields


class SolrHeatmapPlugin(p.SingletonPlugin):
    '''Solr Heatmap plugin'''
    p.implements(p.IConfigurer)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(IDataSolr)

    ## IConfigurer
    def update_config(self, config):
        '''Add our template directories to the list of available templates

        :param config: 

        '''
        p.toolkit.add_template_directory(config, u'theme/templates')
        p.toolkit.add_public_directory(config, u'theme/public')
        p.toolkit.add_resource(u'theme/public', u'ckanext-solr-heatmap')

    ## IConfigurable
    def configure(self, config):
        '''

        :param config: 

        '''
        plugin_config.update(config)

    ## IResourceView
    def info(self):
        ''' '''
        return {
            u'name': u'solr_heatmap',
            u'title': u'Solr Heatmap',
            u'schema': {
                u'geospatial_field': [is_datastore_geospatial_field],
                # 'repeat_map': [self._boolean_validator],
                # 'heat_intensity': [self._float_01_validator],
            },
            u'icon': u'globe',
            u'iframed': True,
            u'filterable': True,
            u'preview_enabled': False,
            u'full_page_edit': False
        }

    @staticmethod
    def view_template(context, data_dict):
        '''

        :param context: 
        :param data_dict: 

        '''
        return u'solr_heatmap_view.html'

    @staticmethod
    def form_template(context, data_dict):
        '''

        :param context: 
        :param data_dict: 

        '''
        return u'solr_heatmap_form.html'

    def can_view(self, data_dict):
        '''Only Solr datastore resources with geospatial fields (type=geospatial_rpt)

        :param data_dict: return:

        '''
        datastore_fields = get_datastore_geospatial_fields(data_dict[u'resource'][u'id'], {})
        if not datastore_fields:
            return False
        # Check that we have a datastore for this resource
        if data_dict[u'resource'].get(u'datastore_active'):
            return True
        return False

    @staticmethod
    def setup_template_variables(context, data_dict):
        '''Setup variables available to templates

        :param context: 
        :param data_dict: 

        '''
        datastore_fields = get_datastore_geospatial_fields(data_dict[u'resource'][u'id'], context)
        return {
            u'resource_json': json.dumps(data_dict[u'resource']),
            u'resource_view_json': json.dumps(data_dict[u'resource_view']),
            u'datastore_fields': [{u'text': f, u'value': f} for f in datastore_fields],
            u'defaults': plugin_config,
        }

    ## IDataSolr
    def datasolr_validate(self, context, data_dict, fields_types):
        '''datasolr validation -re move any of the heatmap fields

        :param context: param data_dict:
        :param fields_types: return:
        :param data_dict: 

        '''
        # Remove any of the facet heatmap fields, so validation passes
        for f in [u'heatmap_field', u'heatmap_geom', u'heatmap_grid_level']:
            try:
                data_dict[u'__extras'].pop(f, None)
            except KeyError:
                continue
        return data_dict

    def datasolr_search(self, context, data_dict, fields_types, query_dict):
        '''

        :param context: 
        :param data_dict: 
        :param fields_types: 
        :param query_dict: 

        '''
        try:
            heatmap_field = data_dict[u'__extras'][u'heatmap_field']
        except KeyError:
            pass
        else:
            query_dict[u'additional_solr_params'] = {
                u'facet': u'true',
                u'facet_heatmap': heatmap_field,
                u'facet_heatmap_format': u'ints2D',
                u'rows': 0
            }

            heatmap_geom = data_dict[u'__extras'].get(u'heatmap_geom', None)
            if heatmap_geom:
                query_dict[u'additional_solr_params'][u'facet_heatmap_geom'] = heatmap_geom

            # Add grid level if it exists
            grid_level = data_dict[u'__extras'].get(u'heatmap_grid_level', None)
            if grid_level:
                query_dict[u'additional_solr_params'][u'facet_heatmap_gridLevel'] = grid_level

        return query_dict
