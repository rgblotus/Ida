# Main application package
# This file can be used to expose key components for easier imports

# Domain layer
from .domain import schemas, models

# Infrastructure layer
from .infra import database, redis

# Services layer
from .services import service_manager

# API layer
from .api.v1 import auth, chats, documents, collections, user_settings