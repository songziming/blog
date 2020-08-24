call activate
call python -m mkdocs build
cd output
call python -m http.server --bind 0.0.0.0 8848
