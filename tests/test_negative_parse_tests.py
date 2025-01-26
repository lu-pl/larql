from pathlib import Path

from larql import sparql_parser
import pytest

from discovery import SPARQL11SyntaxTestDiscovery


negative_test_paths = SPARQL11SyntaxTestDiscovery().get_syntax_tests("negative")


@pytest.mark.parametrize("test_query_path", negative_test_paths)
def test_positive_query_parsing(test_query_path):
    query_file_path: Path = Path(test_query_path)
    query: str = query_file_path.read_text()

    with pytest.raises(Exception):
        sparql_parser.parse(query)
