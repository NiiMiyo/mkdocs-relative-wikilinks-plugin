from setuptools import setup

setup(
	name='mkdocs-relative-wikilinks-plugin',

	py_modules=[
		"plugin",
		"wikilinks",
	],

	entry_points = {
		"mkdocs.plugins": [
			"relative-wikilinks = plugin:RelativeWikilinks"
		]
	}
)

