from setuptools import setup

setup(
	name='mkdocs-relative-wikilinks-plugin',

	py_modules=[
		"plugin",
		"wikilinks",
		"aliases",
		"wikilink_match",
		"wikilink_files",
	],

	install_requires=[
		"mkdocs >= 1.6.1",
		"regex >= 2025.11.3",
		"setuptools >= 80.9.0",
		"python-frontmatter >= 1.1.0",
	],

	entry_points = {
		"mkdocs.plugins": [
			"relative-wikilinks = plugin:RelativeWikilinks"
		]
	}
)
