this.solr_heatmap = this.solr_heatmap || {};
/**
 * NHMMap
 *
 * Custom backbone view to display the Windshaft based maps.
 */
(function (my, $) {

    var self;

    my.SolrHeatmapView = Backbone.View.extend({
        className: 'solr-heatmap-view',

        /**
         * Initialize
         */
        initialize: function () {
            self = this;
            self.$el = $(self.el);
            self.$el.ready(this._onReady);

        },

        _onReady: function () {
            self.map = L.map(self.el).setView([0.0, -40.0], 2);
            L.tileLayer('http://{s}.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}@2x.png?access_token=pk.eyJ1IjoibmhtIiwiYSI6ImNpcjU5a3VuNDAwMDNpYm5vY251MW5oNTIifQ.JuGQ2xZ66FKOAOhYl2HdWQ', {
                maxZoom: 18
             }).addTo(self.map);
            var layer = new L.SolrHeatmapLayer(self.fetchCallback, {
                field: 'geom',
                blur: 2,
                opacity: 0.8,
                interp: 'log'
            });
            layer.addTo(self.map);
        },

        /**
         * Calls to solr to generate the heatmap for a specified bounding box.
         *
         * @param {object} bbox A L.LatLngBounds instance.
         * @param {function} Callback to be run on completion.
         */
        fetchCallback: function (bbox, then) {

            var resource = self.options.resource,
                resourceView = self.options.resourceView;

            var params = {
                resource_id: resource.id
            };

            // Add query string and filters
            if(window.parent.ckan.views.filters.get()){
                params['filters'] = window.parent.ckan.views.filters.get()
            }
            if (window.parent.ckan.views.filters.getFullText()) {
                params['q'] = window.parent.ckan.views.filters.getFullText();
            }

            // Add heatmap parameters
            params['heatmap_field'] = resourceView.geospatial_field;
            params['heatmap_geom'] = '[' +
                Math.max(-180, bbox.getWest()) + ' ' + Math.max(-90, bbox.getSouth()) +
                ' TO ' +
                Math.min(180, bbox.getEast()) + ' ' + Math.min(90, bbox.getNorth()) +
                ']';

            // Mappings oz zoom to grid level
            // As users zooms into the map, the grid resolution increases
            var zoomGridLevel = {
                10: 6,
                7: 5,
                5: 4
            };
            //Default zoom
            params['heatmap_grid_level'] = 3;
            for (var zoom in zoomGridLevel) {
              if (zoomGridLevel.hasOwnProperty(zoom)) {
                if (self.map.getZoom() >= zoom) {
                    params['heatmap_grid_level'] = zoomGridLevel[zoom]
                }
              }
            }
            $.ajax({
                url: ckan.SITE_ROOT + '/api/3/action/datastore_search',
                type: 'POST',
                data: JSON.stringify(params), // serializes the form's elements.
                success: $.proxy(function (data, status, jqXHR) {
                    var hm = data.result.facets.facet_heatmaps[resourceView.geospatial_field];
                    hm['data'] = hm.counts_ints2D;
                    then.apply(self, [hm]);

                }, this),
                error: function (jqXHR, status, error) {
                    self.showError("Heatmap call failed");
                }
            });
        },

        showError: function (msg) {
            msg = msg || _('error loading view');
            window.parent.ckan.pubsub.publish('data-viewer-error', msg);
        }


    });
})(this.solr_heatmap, jQuery);
