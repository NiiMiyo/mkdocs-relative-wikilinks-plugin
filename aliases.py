from collections.abc import Iterable
from frontmatter import loads as frontmatter

from mkdocs.structure.files import File


def get_aliases( file: File, aliases_key: str ) -> dict[str, str]:
	if not file.is_documentation_page():
		return {}

	post = frontmatter( file.content_string, encoding = 'utf-8-sig' )

	if post.get( aliases_key, None ) is None:
		return {}

	aliases = post[ aliases_key ]
	if isinstance( aliases, Iterable ):
		return {
			alias: file.abs_src_path
			for alias in aliases # type: ignore
			if isinstance( alias, str )
		}

	elif isinstance( aliases, str ):
		return { aliases: file.abs_src_path } # type: ignore

	else:
		return {}
