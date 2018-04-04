#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-solr-heatmap
# Created by the Natural History Museum in London, UK

config = {
    # Information about the base layer used for the maps.
    # We don't want to let users define this per dataset, as we need to ensure we have the right to use the tiles.
    u'solr_heatmap.tile_layer.url': u'http://{s}.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}@2x.png?access_token=pk.eyJ1IjoibmhtIiwiYSI6ImNpcjU5a3VuNDAwMDNpYm5vY251MW5oNTIifQ.JuGQ2xZ66FKOAOhYl2HdWQ',
    u'solr_heatmap.tile_layer.opacity': u'0.8',

    # Max/min zoom constraints
    u'solr_heatmap.zoom_bounds.min': u'3',
    u'solr_heatmap.zoom_bounds.max': u'18',

    # Default style parameters for the heatmap.
    u'solr_heatmap.blur': u'5',
    u'solr_heatmap.opacity': u'0.5',
    u'solr_heatmap.interp': u'lin',
    u'solr_heatmap.colors': u'#0000FF, #00FFFF, #00FF00, #FFFF00, #FFA500, #FF0000',

}
