# ⅃arqL 🐦✨

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

`larql` is a simple [Lark](https://github.com/lark-parser/lark) parser for [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).

Apart from parsing SPARQL strings into Lark parse trees, the only additional feature `larql` will provide is a `lark.Transformer` for (pretty) serializing parsed queries back to strings. That's it.

> WARNING: This project is in an early stage of development and should be used with caution.

#### Usage

```python
from larql import SPARQLParser

parsed = SPARQLParser("select * where {?s ?p ?o .}")
parsed.tree  # lark.Tree

# not yet available
parsed.serialize(indent=2)
```
