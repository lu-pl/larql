"""Postive SPARQL 1.1 syntax parsing tests."""

from pathlib import Path

from larql import sparql_parser
import pytest

from discovery import SPARQL11SyntaxTestDiscovery


positive_test_paths = SPARQL11SyntaxTestDiscovery().get_syntax_tests("positive")


@pytest.mark.parametrize("test_query_path", positive_test_paths)
def test_positive_query_parsing(test_query_path):
    query_file_path: Path = Path(test_query_path)
    query: str = query_file_path.read_text()

    assert sparql_parser.parse(query)
