import logging

from os.path import splitext, split, relpath
from typing import TYPE_CHECKING
from unicodedata import normalize
from urllib.parse import quote, urlparse

from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from wikilink_match import WikilinkMatch
from wikilink_files import get_destination

if TYPE_CHECKING:
	from .plugin import RelativeWikilinksConfig


_log = logging.getLogger( f"mkdocs.plugins.{__name__}" )


def replace_all_wikilinks( markdown: str, page: Page, files: Files, config: 'RelativeWikilinksConfig' ) -> str:
	while wiki_match := WikilinkMatch.get_match( markdown ):
		replacement = wikilink_replacement( wiki_match, page.file, files, config )
		markdown = markdown[:wiki_match.start] + replacement + markdown[wiki_match.end:]
	return markdown


def wikilink_replacement( match: WikilinkMatch, origin: File, files: Files, config: 'RelativeWikilinksConfig' ) -> str:
	if is_absolute_url( match.filepath ):
		return make_md_link( match.filepath, match.label or match.filepath, config.absolute_attrs )

	filepath, fragment = sep_fragment( match.filepath )
	label = match.label or fragment or splitext( split( filepath )[ 1 ] )[ 0 ]

	destination = get_destination( filepath, origin, files, config )

	if destination is None:
		_log.warning( f"Doc file '{ origin.src_uri }' contains a link '[[{ filepath }]]' that could not be found." )
		link_attrs = config.not_found_attrs
		href = match.filepath

	else:
		link_attrs = config.found_attrs
		href = quote(
			relpath(
				destination.src_uri,
				origin.src_uri + "/..",
			).replace('\\', '/')
		) + parse_fragment( fragment )

	return make_md_link( href, label, config.relative_attrs, link_attrs )


def sep_fragment( filename: str ) -> tuple[ str, str | None ]:
	fragment_start = filename.find("#")
	if fragment_start == -1:
		return filename, None

	return filename[:fragment_start], filename[fragment_start + 1:]


def parse_fragment(fragment: str | None) -> str:
	if fragment is None or fragment == "":
		return ""

	parsed = normalize('NFD', fragment) \
		.encode('ascii', 'ignore') \
		.decode('utf-8') \
		.lower() \
		.replace('(', '') \
		.replace(')', '') \
		.replace('+', '') \
		.replace(' - ', '-') \
		.replace(' ', '-') \
		.replace('--', '-') \
		.strip( "-" )

	if not parsed.startswith("#"):
		parsed = "#" + parsed

	return parsed


def is_absolute_url( url: str ) -> bool:
	return bool( urlparse( url ).netloc )


def make_md_link( url: str, label: str, *attrs: str | None ) -> str:
	parsed_attrs = [ x for x in attrs if x is not None and len( x ) > 0 ]
	attr_list = (
		f"{{: { ' '.join( parsed_attrs ) } }}"
		if len( parsed_attrs ) > 0
		else ""
	)

	return f"[{ label }]({ url }){ attr_list }";
