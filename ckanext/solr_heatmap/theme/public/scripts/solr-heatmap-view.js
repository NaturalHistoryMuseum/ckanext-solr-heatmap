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
                maxZoom: 18,
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery <a href="http://stamen.com">Stamen</a>'
            }).addTo(self.map);
            var layer = new L.SolrHeatmapLayer(self.fetchCallback, {
                field: 'geom'
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

            var query = new recline.Model.Query();
            if (window.parent.ckan.views && window.parent.ckan.views.filters) {
                var defaultFilters = resourceView.filters || {},
                    urlFilters = window.parent.ckan.views.filters.get(),
                    filters = $.extend({}, defaultFilters, urlFilters);
                $.each(filters, function (field, values) {
                    query.addFilter({type: 'term', field: field, term: values});
                });
                if (window.parent.ckan.views.filters.getFullText()) {
                    query.set({q: window.parent.ckan.views.filters.getFullText()});
                }
            }

            // Add any filters to the params
            var q = query.toJSON();
            ['q', 'facets', 'filters'].forEach(function(el) {
                params[el] = q[el]
            });

            params['heatmap_field'] = resourceView.geospatial_field;
            params['heatmap_geom'] = '[' +
                Math.max(-180, bbox.getWest()) + ' ' + Math.max(-90, bbox.getSouth()) +
                ' TO ' +
                Math.min(180, bbox.getEast()) + ' ' + Math.min(90, bbox.getNorth()) +
                ']';

            $.ajax({
                url: ckan.SITE_ROOT + '/api/3/action/datastore_search',
                type: 'GET',
                data: params,
                success: $.proxy(function (data, status, jqXHR) {
                    var hm = data.result.facets.facet_heatmaps[resourceView.geospatial_field];
                    console.log(data.result);
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
        },


    });
})(this.solr_heatmap, jQuery);
