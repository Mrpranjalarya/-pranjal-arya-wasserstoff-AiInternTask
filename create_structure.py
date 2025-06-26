import os

folders = [
    "backend/app/api",
    "backend/app/core",
    "backend/app/models",
    "backend/app/services",
    "backend/data",
    "frontend/public",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/services",
    "docs",
    "tests",
    "demo/screenshots"
]

files = [
    # Backend API
    "backend/app/api/__init__.py",
    "backend/app/api/routes.py",
    # Backend Core
    "backend/app/core/embedding.py",
    "backend/app/core/ocr.py",
    "backend/app/core/preprocessing.py",
    "backend/app/core/query_engine.py",
    "backend/app/core/theme_extractor.py",
    "backend/app/core/vector_store.py",
    # Backend Models
    "backend/app/models/document_model.py",
    "backend/app/models/schemas.py",
    # Backend Services
    "backend/app/services/document_service.py",
    "backend/app/services/query_service.py",
    "backend/app/services/theme_service.py",
    # Backend Config & Main
    "backend/app/config.py",
    "backend/app/main.py",
    # Backend Docker and requirements
    "backend/Dockerfile",
    "backend/requirements.txt",
    # Frontend main files
    "frontend/src/App.jsx",
    "frontend/package.json",
    "frontend/vite.config.js",
    # Frontend components
    "frontend/src/components/ChatInterface.jsx",
    "frontend/src/components/DocumentList.jsx",
    "frontend/src/components/ThemeSummary.jsx",
    "frontend/src/components/UploadDocuments.jsx",
    # Frontend pages and services
    "frontend/src/pages/Home.jsx",
    "frontend/src/services/api.js",
    # Docs
    "docs/api_reference.md",
    "docs/architecture_diagram.png",
    # Tests
    "tests/test_api.py",
    "tests/test_ocr.py",
    "tests/test_query_engine.py",
    "tests/test_theme_extractor.py",
    # Demo
    "demo/demo_script.md",
    "demo/demo_video.mp4"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file_path in files:
    # Only create file if it doesn't exist to avoid overwriting
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            # Optional: put a comment header inside Python or JS files
            if file_path.endswith(".py"):
                f.write(f"# {os.path.basename(file_path)}\n")
            elif file_path.endswith((".jsx", ".js")):
                f.write(f"// {os.path.basename(file_path)}\n")
            elif file_path.endswith(".md"):
                f.write(f"# {os.path.basename(file_path)}\n")
            else:
                # Leave other files empty (png, json etc)
                pass

print("Project folder structure created successfully!")
