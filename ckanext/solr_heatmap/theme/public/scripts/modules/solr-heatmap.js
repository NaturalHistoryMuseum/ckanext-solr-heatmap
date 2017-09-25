this.solr_heatmap = this.solr_heatmap || {};

this.ckan.module('solr-heatmap', function ($, _) {
    function initialize() {
        console.log(this.options);
        this.view = new solr_heatmap.SolrHeatmapView({
            resource: JSON.parse(this.options.resource),
            resourceView: JSON.parse(this.options.resourceView),
            i18n: this.options.i18n
        });
        $(this.el).append(this.view.el);
    }

    return {
        initialize: initialize,
        options: {
            resource: null,
            resourceView: null,
            i18n: {
                errorLoadingPreview: "Could not load view",
                errorDataProxy: "DataProxy returned an error",
                errorDataStore: "DataStore returned an error",
                previewNotAvailableForDataType: "View not available for data type: ",
                noRecords: "No matching records"
            }
        }
    };
});
