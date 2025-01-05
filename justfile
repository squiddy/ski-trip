default: dev

format:
    uv run ruff format

dev:
    uv run pyxel-reload main

build:
    rm -rf pyxel_utils/
    cp -R $(uv run python -c "import pyxel_utils; print(pyxel_utils.__path__[0])") .
    uv run pyxel package . main.py
    uv run pyxel app2html ski-trip.pyxapp
    rm -rf pyxel_utils/ ski-trip.pyxapp
    echo {{GREEN}}"Final build is in ski-trip.html"
