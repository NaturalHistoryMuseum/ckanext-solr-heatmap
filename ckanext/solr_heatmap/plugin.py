import re
from sqlalchemy.sql import select
from sqlalchemy import Table, Column, MetaData, Numeric
from sqlalchemy.exc import DataError
from sqlalchemy import func, or_, not_, cast
import ckan.plugins as p
from ckan.common import json
import ckan.plugins.toolkit as toolkit
import ckanext.tiledmap.logic.action as map_action
import ckanext.tiledmap.logic.auth as map_auth
from ckanext.tiledmap.config import config as plugin_config
from ckanext.tiledmap.lib.helpers import mustache_wrapper, dwc_field_title
from ckanext.tiledmap.db import _get_engine
from ckanext.datastore.interfaces import IDatastore
from ckan.common import _

import ckan.logic as logic
get_action = logic.get_action

import ckan.lib.navl.dictization_functions as df
ignore_empty = p.toolkit.get_validator('ignore_empty')
Invalid = df.Invalid
Missing = df.Missing


class SolrHeatmapPlugin(p.SingletonPlugin):
    """Windshaft map plugin

    This plugin replaces the recline preview template to use a custom map engine.
    The plugin provides controller routes to server tiles and grid from the winsdhaft
    backend. See MapController for configuration options.
    """
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.IConfigurable)

    ## IConfigurer
    def update_config(self, config):
        """Add our template directories to the list of available templates"""
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-tiledmap')

    ## IRoutes
    def before_map(self, map):
        """Add routes to our tile/grid serving functionality"""
        map.connect('/map-tile/{z}/{x}/{y}.png', controller='ckanext.tiledmap.controllers.map:MapController', action='tile')
        map.connect('/map-grid/{z}/{x}/{y}.grid.json', controller='ckanext.tiledmap.controllers.map:MapController', action='grid')
        map.connect('/map-info', controller='ckanext.tiledmap.controllers.map:MapController', action='map_info')

        return map

    ## IActions
    def get_actions(self):
        """Add actions to override resource create/update/delete actions"""
        return {
            'resource_view_create': map_action.resource_view_create,
            'resource_view_update': map_action.resource_view_update,
            'resource_view_delete': map_action.resource_view_delete
        }

    ## IAuthFunctions
    def get_auth_functions(self):
        """Add auth functions for access to geom column creation actions"""
        return {
            'create_geom_columns': map_auth.create_geom_columns,
            'update_geom_columns': map_auth.update_geom_columns
        }

    ## ITemplateHelpers
    def get_helpers(self):
        """Add a template helper for formating mustache templates server side"""
        return {
            'mustache': mustache_wrapper,
            'dwc_field_title': dwc_field_title
        }

    ## IConfigurable
    def configure(self, config):
        plugin_config.update(config)

    ## IResourceView
    def info(self):
        """Return generic info about the plugin"""
        return {
            'name': 'tiledmap',
            'title': 'Tiled map',
            'schema': {
                'latitude_field': [self._is_datastore_field, self._is_latitude_field],
                'longitude_field': [self._is_datastore_field, self._is_longitude_field],
                'repeat_map': [self._boolean_validator],
                'enable_plot_map': [self._boolean_validator],
                'enable_grid_map': [self._boolean_validator],
                'enable_heat_map': [self._boolean_validator],
                'plot_marker_color': [self._color_validator],
                'plot_marker_line_color': [self._color_validator],
                'grid_base_color': [self._color_validator],
                'heat_intensity': [self._float_01_validator],
                'enable_utf_grid': [self._boolean_validator],
                'utf_grid_title': [self._is_datastore_field],
                'utf_grid_fields': [ignore_empty, self._is_datastore_field],
                'overlapping_records_view': [self._is_view_id],
            },
            'icon': 'compass',
            'iframed': True,
            'filterable': True,
            'preview_enabled': False,
            'full_page_edit': False
        }

    def view_template(self, context, data_dict):
        return 'tiledmap_view.html'

    def form_template(self, context, data_dict):
        return 'tiledmap_form.html'

    def can_view(self, data_dict):
        """Specificy which resources can be viewed by this plugin"""
        # Check that the Windshaft server is configured
        if ((plugin_config.get('tiledmap.windshaft.host', None) is None) or
           (plugin_config.get('tiledmap.windshaft.port', None) is None)):
            return False
        # Check that we have a datastore for this resource
        if data_dict['resource'].get('datastore_active'):
            return True
        return False

    def setup_template_variables(self, context, data_dict):
        """Setup variables available to templates"""
        #TODO: Apply variables to appropriate view.
        datastore_fields = self._get_datastore_fields(data_dict['resource']['id'], context)
        views = p.toolkit.get_action('resource_view_list')(context, {'id': data_dict['resource']['id']})
        if 'id' in data_dict['resource_view']:
            views = [v for v in views if v['id'] != data_dict['resource_view']['id']]
        views = [{'text': _('(None)'), 'value': ''}] + [{'text': v['title'], 'value': v['id']} for v in views]
        return {
            'resource_json': json.dumps(data_dict['resource']),
            'resource_view_json': json.dumps(data_dict['resource_view']),
            'map_fields': [{'text': f, 'value': f} for f in datastore_fields],
            'available_views': views,
            'defaults': plugin_config,
            'is_new': not('id' in data_dict['resource_view'])
        }

    def _is_datastore_field(self, key, data, errors, context):
        """Check that a field is indeed a datastore field"""
        if isinstance(data[key], list):
            if not set(data[key]).issubset(self._get_datastore_fields(context['resource'].id, context)):
                raise p.toolkit.Invalid('"{0}" is not a valid parameter'.format(data[key]))
        elif not data[key] in self._get_datastore_fields(context['resource'].id, context):
            raise p.toolkit.Invalid('"{0}" is not a valid parameter'.format(data[key]))

    def _get_datastore_fields(self, rid, context):
        if not hasattr(self, '_datastore_fields'):
            self._datastore_fields = {}
        if not (rid in self._datastore_fields):
            data = {'resource_id': rid, 'limit': 0}
            fields = toolkit.get_action('datastore_search')(context, data)['fields']
            self._datastore_fields[rid] = [f['id'] for f in fields]

        return self._datastore_fields[rid]

    def _boolean_validator(self, value, context):
        """Validate a field as a boolean. Assuming missing value means false"""
        if isinstance(value, bool):
            return value
        elif (isinstance(value, str) or isinstance(value, unicode)) and value.lower() in ['true', 'yes', 't', 'y', '1']:
            return True
        elif (isinstance(value, str) or isinstance(value, unicode)) and value.lower() in ['false', 'no', 'f', 'n', '0']:
            return False
        elif isinstance(value, Missing):
            return False
        else:
            raise p.toolkit.Invalid(_('Value must a true/false value (ie. true/yes/t/y/1 or false/no/f/n/0)'))

    def _color_validator(self, value, context):
        """Validate a value is a CSS hex color"""
        if re.match('^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', value):
            if value[0] != '#':
                return '#' + value
            else:
                return value
        else:
            raise p.toolkit.Invalid(_('Colors must be formed of three or six RGB hex value, optionally preceded by a # sign (eg. #E55 or #F4A088)'))

    def _float_01_validator(self, value, context):
        """Validate value is a float number between 0 and 1"""
        try:
            value = float(value)
        except:
            raise p.toolkit.Invalid(_('Must be a decimal number, between 0 and 1'))
        if value < 0 or value > 1:
            raise p.toolkit.Invalid(_('Must be a decimal number, between 0 and 1'))

        return value

    def _is_view_id(self, value, context):
        """Ensure this is a view id on the current resource"""
        if value:
            views = p.toolkit.get_action('resource_view_list')(context, {'id': context['resource'].id})
            if value not in [v['id'] for v in views]:
                raise p.toolkit.Invalid(_('Must be a view on the current resource'))

        return value

    def _is_latitude_field(self, value, context):
        """Ensure this field can be used for latitudes"""
        # We can't use datastore_search for this, as we need operators
        db = _get_engine()
        metadata = MetaData()
        table = Table(context['resource'].id, metadata, Column(value, Numeric))

        query = select([func.count(1).label('count')], from_obj=table)
        query = query.where(not_(table.c[value] == None))
        query = query.where(or_(cast(table.c[value], Numeric) < -90, cast(table.c[value], Numeric) > 90))
        with db.begin() as connection:
            try:
                query_result = connection.execute(query)
            except DataError as e:
                raise p.toolkit.Invalid(_('Latitude field must contain numeric data'))

            row = query_result.fetchone()
            query_result.close()
            if row['count'] > 0:
                raise p.toolkit.Invalid(_('Latitude field must be between -90 and 90'))
        return value

    def _is_longitude_field(self, value, context):
        """Ensure this field can be used for longitudes"""
        # We can't use datastore_search for this, as we need operators
        db = _get_engine()
        metadata = MetaData()
        table = Table(context['resource'].id, metadata, Column(value, Numeric))

        query = select([func.count(1).label('count')], from_obj=table)
        query = query.where(not_(table.c[value] == None))
        query = query.where(or_(cast(table.c[value], Numeric) < -180, cast(table.c[value], Numeric) > 180))
        with db.begin() as connection:
            try:
                query_result = connection.execute(query)
            except DataError as e:
                raise p.toolkit.Invalid(_('Longitude field must contain numeric data'))

            row = query_result.fetchone()
            query_result.close()
            if row['count'] > 0:
                raise p.toolkit.Invalid(_('Longitude field must be between -180 and 180'))
        return value
