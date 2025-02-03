from pathlib import Path

from lark import LarkError
from larql import SPARQLParser, sparql_parser
import pytest

from tests.discovery import SPARQL11SyntaxTestDiscovery


negative_test_paths = SPARQL11SyntaxTestDiscovery().get_syntax_tests("negative")


@pytest.mark.parametrize("test_query_path", negative_test_paths)
def test_positive_query_parsing(test_query_path):
    _query_file_path: Path = Path(test_query_path)
    query: str = _query_file_path.read_text()

    with pytest.raises(LarkError):
        sparql_parser.parse(query)

    with pytest.raises(LarkError):
        SPARQLParser(query)
