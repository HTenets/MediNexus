"""Pytest root conftest — force no-database demo mode for the test suite.

Environment variables are set before any app module import so that
`app.config.settings` and the database engine pick up test-safe values.
Real environment variables (if explicitly exported) still win.
"""

import os

os.environ.setdefault("MEDINEXUS_DATABASE_URL", "")
os.environ.setdefault("MEDINEXUS_REDIS_URL", "")
os.environ.setdefault("MEDINEXUS_QDRANT_URL", "")
os.environ.setdefault("MEDINEXUS_DEMO_MODE", "true")
os.environ.setdefault("MEDINEXUS_JWT_SECRET", "test-secret-for-ci")
