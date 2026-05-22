#!/usr/bin/env python3
import os
import sys

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

import uvicorn
uvicorn.run('app.main:app', host='0.0.0.0', port=8000)
