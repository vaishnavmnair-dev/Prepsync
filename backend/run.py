"""PrepPilot Backend Server Runner."""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"============================================================")
    print(f" Starting PrepPilot Backend Server on http://{host}:{port}")
    print(f" Swagger UI Documentation: http://{host}:{port}/docs")
    print(f"============================================================")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
