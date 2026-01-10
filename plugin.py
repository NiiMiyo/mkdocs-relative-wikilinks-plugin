from mkdocs.config.base import Config
from mkdocs.config import config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from wikilinks import replace_all_wikilinks
from aliases import get_aliases


class RelativeWikilinksConfig( Config ):
	relative_attrs = c.Optional( c.Type( str ) )
	absolute_attrs = c.Optional( c.Type( str ) )
	found_attrs = c.Optional( c.Type( str ) )
	not_found_attrs = c.Optional( c.Type( str ) )

	aliases_enabled = c.Type( bool, default = False )
	aliases_property = c.Type( str, default = "aliases" )
	aliases = c.DictOfItems( c.File( True ), default = {} )

class RelativeWikilinks( BasePlugin[RelativeWikilinksConfig] ):
	def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files | None:
		if self.config.aliases_enabled:
			for f in files:
				self.config.aliases.update( get_aliases( f, self.config.aliases_property ) )

	def on_page_markdown(self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Files) -> str | None:
		return replace_all_wikilinks( markdown, page, files, self.config )
