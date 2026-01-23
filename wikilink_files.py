from os.path import splitext
from typing import TYPE_CHECKING

from mkdocs.structure.files import File, Files

if TYPE_CHECKING:
	from .plugin import RelativeWikilinksConfig


def get_destination( filepath: str, origin: File, files: Files, config: 'RelativeWikilinksConfig' ):
	return get_destination_from_alias( filepath, files, config ) \
		or get_destination_from_filepath( filepath, origin, files )


def get_destination_from_alias( filepath: str, files: Files, config: 'RelativeWikilinksConfig' ) -> File | None:
	if alias_file_path := config.aliases.get( filepath, None ):
		return next( ( f for f in files if f.abs_src_path == alias_file_path ), None )


def get_destination_from_filepath( filepath: str, origin: File, files: Files ) -> File | None:
	if filepath == "":
		return origin

	file_name, file_ext = splitext( filepath )
	if file_ext == "":
		file_ext = ".md"

	file_path_upper = split_reverse_upper_path( ( file_name + file_ext ) )

	for f in files:
		f_path_upper = split_reverse_upper_path( f.src_uri )

		if (
			len( file_path_upper ) <= len( f_path_upper )
			and all( l == t for l, t in zip( file_path_upper, f_path_upper ) )
		): return f


def split_reverse_upper_path( path: str ):
	return [
		p
		for p in path.upper().replace( "\\", "/" ).split( "/" )
		if len( p )
	][::-1]
