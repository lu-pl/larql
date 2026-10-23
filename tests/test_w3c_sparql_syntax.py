import itertools
from pathlib import Path

import lark.exceptions
import pytest
from larql import SPARQLParser

from tests.discovery import SyntaxTestDiscovery, SyntaxTestInfo


@pytest.mark.parametrize(
    "test_info",
    itertools.chain(
        SyntaxTestDiscovery(Path("./tests/rdf-tests/sparql/sparql10/manifest.ttl")),
        SyntaxTestDiscovery(Path("./tests/rdf-tests/sparql/sparql11/manifest-all.ttl")),
        SyntaxTestDiscovery(Path("./tests/rdf-tests/sparql/sparql12/manifest.ttl")),
    ),
    ids=lambda val: val.test_id,
)
def test_w3c_sparql_syntax_tests(test_info: SyntaxTestInfo):
    match test_info.valid:
        case True:
            SPARQLParser(sparql=test_info.test_path.read_text())
        case False:
            with pytest.raises(lark.exceptions.LarkError):
                SPARQLParser(sparql=test_info.test_path.read_text())
        case _:
            assert False, "this should never happen"
