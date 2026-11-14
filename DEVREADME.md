To publish a new version of this package, follow this protocol

0. If anything in `libmogra/raagdb/` (names.json, tanarang.json, extras.json) changed, rebuild the raag DB with `python -m libmogra.raagdb` (a test fails if raags.pkl is stale).

1. Check the new code to main and push it.

2. Run
```
poetry install
poetry build
poetry publish
```
