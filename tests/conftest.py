"""
Test database setup for repositories and API tests.
Ensures both main and audit tables are created in the in-memory SQLite DB.
"""

import os
from datetime import date

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Give the test suite a deterministic JWT configuration.
# These values are only for tests and are not production credentials.
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"

from constants.employee_roles import EmployeeRole
from database import AuditBase, Base, get_audit_db, get_db
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_schema import EmployeeSchema
from main import app
