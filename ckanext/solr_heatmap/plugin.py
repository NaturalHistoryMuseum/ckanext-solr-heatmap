import ckan.plugins as p
from ckan.common import json

from ckanext.datasolr.interfaces import IDataSolr

from ckanext.solr_heatmap.config import config as plugin_config
from ckanext.solr_heatmap.logic.validators import is_datastore_geospatial_field
from ckanext.solr_heatmap.lib import get_datastore_geospatial_fields


class SolrHeatmapPlugin(p.SingletonPlugin):
    """
    Solr Heatmap plugin
    """
    p.implements(p.IConfigurer)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IConfigurable)
    p.implements(IDataSolr)

    ## IConfigurer
    def update_config(self, config):
        """Add our template directories to the list of available templates"""
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-solr-heatmap')

    ## IConfigurable
    def configure(self, config):
        plugin_config.update(config)

    ## IResourceView
    def info(self):
        """Return generic info about the plugin"""
        return {
            'name': 'solr_heatmap',
            'title': 'Solr Heatmap',
            'schema': {
                'geospatial_field': [is_datastore_geospatial_field],
                # 'repeat_map': [self._boolean_validator],
                # 'heat_intensity': [self._float_01_validator],
            },
            'icon': 'globe',
            'iframed': True,
            'filterable': True,
            'preview_enabled': False,
            'full_page_edit': False
        }

    @staticmethod
    def view_template(context, data_dict):
        return 'solr_heatmap_view.html'

    @staticmethod
    def form_template(context, data_dict):
        return 'solr_heatmap_form.html'

    def can_view(self, data_dict):
        """
        Only Solr datastore resources with geospatial fields (type=geospatial_rpt)
        @param data_dict:
        @return:
        """
        datastore_fields = get_datastore_geospatial_fields(data_dict['resource']['id'], {})
        if not datastore_fields:
            return False
        # Check that we have a datastore for this resource
        if data_dict['resource'].get('datastore_active'):
            return True
        return False

    @staticmethod
    def setup_template_variables(context, data_dict):
        """Setup variables available to templates"""
        datastore_fields = get_datastore_geospatial_fields(data_dict['resource']['id'], context)
        return {
            'resource_json': json.dumps(data_dict['resource']),
            'resource_view_json': json.dumps(data_dict['resource_view']),
            'datastore_fields': [{'text': f, 'value': f} for f in datastore_fields],
            'defaults': plugin_config,
        }

    ## IDataSolr
    def datasolr_validate(self, context, data_dict, fields_types):
        """
        datasolr validation -re move any of the heatmap fields
        @param context:
        @param data_dict:
        @param fields_types:
        @return:
        """
        # Remove any of the facet heatmap fields, so validation passes
        for f in ['heatmap_field', 'heatmap_geom', 'heatmap_format']:
            try:
                data_dict['__extras'].pop(f, None)
            except KeyError:
                continue
        return data_dict

    def datasolr_search(self, context, data_dict, fields_types, query_dict):
        try:
            heatmap_field = data_dict['__extras']['heatmap_field']
        except KeyError:
            pass
        else:
            query_dict['additional_solr_params'] = {
                'facet': 'true',
                'facet_heatmap': heatmap_field,
                'facet_heatmap_format': 'ints2D',
                'rows': 0
            }
            heatmap_geom = data_dict['__extras'].get('heatmap_geom', None)
            if heatmap_geom:
                query_dict['additional_solr_params']['facet_heatmap_geom'] = heatmap_geom

        return query_dict
