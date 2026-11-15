"""
Starhealers Module 4 - OpenAPI Specification Generator.
Exports OpenAPI 3.1 JSON schema representing all backend contracts, endpoints,
schemas, and query parameters for frontend client code generation and contract tests.
"""

import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.config import settings

def export_openapi():
    openapi_schema = app.openapi()
    
    output_dir = settings.CONTRACTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = output_dir / "openapi.json"
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"Successfully generated OpenAPI schema at: {target_file}")
    print(f"Total paths documented: {len(openapi_schema.get('paths', {}))}")
    print(f"Total component schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")

if __name__ == "__main__":
    export_openapi()

