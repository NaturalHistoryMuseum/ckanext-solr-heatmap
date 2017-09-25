# Default configuration
config = {
    # Information about the base layer used for the maps.
    # We don't want to let users define this per dataset, as we need to ensure we have the right to use the tiles.
    'solr_heatmap.tile_layer.url': 'http://{s}.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}@2x.png?access_token=pk.eyJ1IjoibmhtIiwiYSI6ImNpcjU5a3VuNDAwMDNpYm5vY251MW5oNTIifQ.JuGQ2xZ66FKOAOhYl2HdWQ',
    'solr_heatmap.tile_layer.opacity': '0.8',

    # Max/min zoom constraints
    'solr_heatmap.zoom_bounds.min': '3',
    'solr_heatmap.zoom_bounds.max': '18',

    # The style parameters for the heatmap. The intensity can be defined per dataset (with the default provided in
    # the main config if present, or here otherwise), but the marker url and marker size can only be set in the main
    # config (if present, or here otherwise) as they have a notable performance impact on larger datasets.
    'solr_heatmap.intensity': '0.1',
    'solr_heatmap.gradient': '#0000FF, #00FFFF, #00FF00, #FFFF00, #FFA500, #FF0000',

}