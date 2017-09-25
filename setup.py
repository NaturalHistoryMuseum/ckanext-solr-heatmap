from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-solr-heatmap',
	version=version,
	description="",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'tests']),
	namespace_packages=['ckanext', 'ckanext.solr_heatmap'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
            solr_heatmap = ckanext.solr_heatmap.plugin:SolrHeatmapPlugin
	""",
)
