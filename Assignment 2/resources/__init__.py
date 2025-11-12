# resources/__init__.py
"""
This init file makes 'resources' a package.
Importing the modules here triggers their self-registration
with the ResourceFactory.

This is the key to the Open/Closed Principle. To add a new
resource, just create a 'database.py' file and add
'from . import database' here.
"""
from . import app_service
from . import storage_account
from . import cache_db

# To add a new resource, e.g. 'database.py':
# 1. Create the 'database.py' file.
# 2. Add 'from . import database' here.
# The system will pick it up automatically.