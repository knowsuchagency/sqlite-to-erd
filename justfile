set dotenv-load

fk:
    uv run sqlite_to_erd.py test_fk.db

fk-png:
    uv run sqlite_to_erd.py test_fk.db --png test_fk.png

complex:
    uv run sqlite_to_erd.py complex_test.db

complex-png:
    uv run sqlite_to_erd.py complex_test.db --png complex_test.png

build:
    uv build

publish: build
    uv publish
