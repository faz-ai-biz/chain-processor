"""
Base repository class for the Chain Processing System.

This module defines the base repository class that provides common
CRUD operations for all repositories.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast, get_args
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from ..models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize a new repository.

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        # Extract the model type from the generic parameter
        # This is a bit of a hack but works well for typed repositories
        self.model_class = cast(Type[T], get_args(self.__class__.__orig_bases__[0])[0])

    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        """
        Get an entity by ID.

        Args:
            id: The entity ID

        Returns:
            The entity if found, None otherwise
        """
        return self.db.get(self.model_class, id)

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        Get all entities with pagination.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of entities
        """
        stmt = select(self.model_class).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def create(self, entity: T) -> T:
        """
        Create a new entity.

        Args:
            entity: The entity to create

        Returns:
            The created entity with updated ID and timestamps
        """
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, id: uuid.UUID, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity by ID.

        Args:
            id: The entity ID
            data: The fields to update

        Returns:
            The updated entity if found, None otherwise
        """
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**data)
            .returning(self.model_class)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        
        updated_entity = result.scalar_one_or_none()
        return updated_entity

    def delete(self, id: uuid.UUID) -> bool:
        """
        Delete an entity by ID.

        Args:
            id: The entity ID

        Returns:
            True if the entity was deleted, False if it was not found
        """
        stmt = delete(self.model_class).where(self.model_class.id == id)
        result = self.db.execute(stmt)
        self.db.commit()
        
        # SQLAlchemy returns the number of rows deleted
        return result.rowcount > 0

    def exists(self, id: uuid.UUID) -> bool:
        """
        Check if an entity with the given ID exists.

        Args:
            id: The entity ID

        Returns:
            True if the entity exists, False otherwise
        """
        stmt = select(self.model_class).where(self.model_class.id == id).exists()
        result = self.db.execute(select(stmt))
        return result.scalar_one() 