"""
CineBook Entry Point Runner
Usage: python run.py
"""
import uvicorn

if __name__ == "__main__":
    import sys
    import io
    # Force UTF-8 output so emoji characters don't crash on Windows terminals
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("\U0001f3ac Starting CineBook Web Application...")
    print("\U0001f4cd URL: http://127.0.0.1:8000")
    print("\U0001f4da API Documentation: http://127.0.0.1:8000/docs")
    print("\u26a1 DSA Lab: http://127.0.0.1:8000/dsa-explorer")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
