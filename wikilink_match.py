from dataclasses import dataclass
import regex

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

	@staticmethod
	def get_match( markdown: str ):
		matches = WIKILINK_PATTERN.finditer( markdown )
		match = next( matches, None )

		if match is None:
			return None
		else:
			return WikilinkMatch.from_match( match )

	@property
	def start( self ) -> int: return self.position[ 0 ]

	@property
	def end( self ) -> int: return self.position[ 1 ]
