import logging
import regex
import unicodedata

from dataclasses import dataclass
from os.path import splitext, split, relpath
from typing import TYPE_CHECKING
from urllib.parse import quote, urlparse

from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

if TYPE_CHECKING:
	from .plugin import RelativeWikilinksConfig


_log = logging.getLogger( f"mkdocs.plugins.{__name__}" )
WIKILINK_PATTERN = regex.compile( r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]" )


@dataclass
class WikilinkMatch():
	position: tuple[ int, int ]
	filepath: str
	label: str | None

	@staticmethod
	def from_match( match: regex.Match[str] ):
		label = (
			match.group( 2 ).strip()
			if match.group( 2 )
			else None
		)

		return WikilinkMatch(
			position = (
				match.start( 0 ),
				match.end( 0 ),
			),
			filepath = match.group( 1 ).strip(),
			label = label,
		)

	@property
	def start( self ) -> int: return self.position[ 0 ]

	@property
	def end( self ) -> int: return self.position[ 1 ]

def replace_all_wikilinks( markdown: str, page: Page, files: Files, config: 'RelativeWikilinksConfig' ) -> str:
	global WIKILINK_PATTERN

	while True:
		matches = WIKILINK_PATTERN.finditer( markdown )
		match = next( matches, None )
		if match is None:
			break

		wiki_match = WikilinkMatch.from_match( match )

		replacement = wikilink_replacement( wiki_match, page.file, files, config )
		markdown = markdown[:wiki_match.start] + replacement + markdown[wiki_match.end:]
	return markdown


def wikilink_replacement( match: WikilinkMatch, origin: File, files: Files, config: 'RelativeWikilinksConfig' ) -> str:
	if is_absolute_url( match.filepath ):
		return f"[{ match.label or match.filepath }]({ match.filepath })"

	filepath, fragment = sep_fragment( match.filepath )
	label = match.label or fragment or splitext( split( filepath )[ 1 ] )[ 0 ]

	destination = get_destination_file( filepath, origin, files )

	if destination is None:
		link_class = config.not_found_attrs
		# destination file was not found: generating random link
		resolved_link = f"[{ label }]({ match.filepath })"

	else:
		link_class = config.found_attrs
		href = quote(
			relpath(
				destination.src_uri,
				origin.src_uri + "/..",
			).replace('\\', '/')
		) + parse_fragment( fragment )

		resolved_link = f"[{ label }]({ href })"

	attrs = [ x for x in ( config.attrs, link_class, ) if x is not None and len( x ) > 0 ]
	attr_list = (
		f"{{: { ' '.join( attrs ) } }}"
		if len( attrs ) > 0
		else ""
	)

	return resolved_link + attr_list


def get_destination_file( filepath: str, origin: File, files: Files ) -> File | None:
	filepath, _ = sep_fragment( filepath )
	if filepath == "":
		return origin

	file_name, file_ext = splitext( filepath )
	if file_ext == "":
		file_ext = ".md"

	file_upper = ( file_name + file_ext ).upper()
	for f in files:
		f_upper = f.src_uri.upper()
		if f_upper.endswith(file_upper):
			return f


def sep_fragment( filename: str ) -> tuple[ str, str | None ]:
	fragment_start = filename.find("#")
	if fragment_start == -1:
		return filename, None

	return filename[:fragment_start], filename[fragment_start + 1:]


def parse_fragment(fragment: str | None) -> str:
	if fragment is None or fragment == "":
		return ""

	parsed = unicodedata.normalize('NFD', fragment) \
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
