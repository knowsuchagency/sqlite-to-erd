fk:
    uv run sqlite_to_erd.py test_fk.db

fk-png:
    just fk | dot -Tpng -o test_fk.png

complex:
    uv run sqlite_to_erd.py complex_test.db

complex-png:
    just complex | dot -Tpng -o complex_test.png
