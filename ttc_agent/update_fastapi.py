#!/usr/bin/env python3
import re

# Read the original file
with open('chat_app.py', 'r') as f:
    content = f.read()

# Add StaticFiles import
import_pattern = r'from fastapi\.responses import FileResponse, Response, StreamingResponse'
import_replacement = 'from fastapi.responses import FileResponse, Response, StreamingResponse\nfrom fastapi.staticfiles import StaticFiles'
content = re.sub(import_pattern, import_replacement, content)

# Add static files mounting
app_pattern = r'app = fastapi\.FastAPI\(lifespan=lifespan\)\nlogfire\.instrument_fastapi\(app\)'
app_replacement = 'app = fastapi.FastAPI(lifespan=lifespan)\nlogfire.instrument_fastapi(app)\n\n# Mount static files\napp.mount("/static", StaticFiles(directory=THIS_DIR / "static"), name="static")'
content = re.sub(app_pattern, app_replacement, content)

# Update index route
index_pattern = r'@app\.get\(\'/\'\)\nasync def index\(\) -> FileResponse:\n    return FileResponse\(\(THIS_DIR / \'chat_app\.html\'\), media_type=\'text/html\'\)'
index_replacement = '''@app.get('/')
async def index() -> FileResponse:
    static_dir = THIS_DIR / "static"
    if static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')

@app.get('/{path:path}')
async def serve_react(path: str):
    static_dir = THIS_DIR / "static"
    if path and (static_dir / path).exists():
        return FileResponse(static_dir / path)
    elif static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')'''
content = re.sub(index_pattern, index_replacement, content)

# Write the updated content
with open('chat_app.py', 'w') as f:
    f.write(content)

print("FastAPI app updated successfully")
