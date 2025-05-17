"""
Tests for the UserRepository class.
"""

import pytest
import uuid

from chain_processor_db.models.user import User
from chain_processor_db.repositories.user_repo import UserRepository


def test_get_by_id(db_session, sample_user):
    """Test the get_by_id method."""
    repo = UserRepository(db_session)
    user = repo.get_by_id(sample_user.id)
    assert user is not None
    assert user.id == sample_user.id
    assert user.email == sample_user.email


def test_get_by_email(db_session, sample_user):
    """Test the get_by_email method."""
    repo = UserRepository(db_session)
    user = repo.get_by_email(sample_user.email)
    assert user is not None
    assert user.id == sample_user.id
    assert user.email == sample_user.email


def test_get_by_email_not_found(db_session):
    """Test the get_by_email method with a non-existent email."""
    repo = UserRepository(db_session)
    user = repo.get_by_email("nonexistent@example.com")
    assert user is None


def test_get_by_role(db_session, sample_user):
    """Test the get_by_role method."""
    repo = UserRepository(db_session)
    users = repo.get_by_role("user")
    assert len(users) == 1
    assert users[0].id == sample_user.id
    assert users[0].email == sample_user.email


def test_get_by_role_not_found(db_session, sample_user):
    """Test the get_by_role method with a non-existent role."""
    repo = UserRepository(db_session)
    users = repo.get_by_role("admin")
    assert len(users) == 0


def test_create(db_session):
    """Test the create method."""
    repo = UserRepository(db_session)
    user = User(
        email="new@example.com",
        password_hash="hashed_password",
        full_name="New User",
        is_active=True,
        is_superuser=False,
        roles=["user"],
    )
    created_user = repo.create(user)
    assert created_user.id is not None
    assert created_user.email == "new@example.com"
    assert created_user.full_name == "New User"
    
    # Check that the user was added to the database
    fetched_user = repo.get_by_email("new@example.com")
    assert fetched_user is not None
    assert fetched_user.id == created_user.id


def test_update(db_session, sample_user):
    """Test the update method."""
    repo = UserRepository(db_session)
    updated = repo.update(sample_user.id, {"full_name": "Updated Name"})
    assert updated is not None
    assert updated.full_name == "Updated Name"
    
    # Check that the user was updated in the database
    fetched_user = repo.get_by_id(sample_user.id)
    assert fetched_user.full_name == "Updated Name"


def test_update_not_found(db_session):
    """Test the update method with a non-existent user."""
    repo = UserRepository(db_session)
    updated = repo.update(uuid.uuid4(), {"full_name": "Updated Name"})
    assert updated is None


def test_delete(db_session, sample_user):
    """Test the delete method."""
    repo = UserRepository(db_session)
    result = repo.delete(sample_user.id)
    assert result is True
    
    # Check that the user was deleted from the database
    fetched_user = repo.get_by_id(sample_user.id)
    assert fetched_user is None


def test_delete_not_found(db_session):
    """Test the delete method with a non-existent user."""
    repo = UserRepository(db_session)
    result = repo.delete(uuid.uuid4())
    assert result is False


def test_count_active_users(db_session, sample_user):
    """Test the count_active_users method."""
    repo = UserRepository(db_session)
    count = repo.count_active_users()
    assert count == 1
    
    # Create an inactive user
    inactive_user = User(
        email="inactive@example.com",
        password_hash="hashed_password",
        full_name="Inactive User",
        is_active=False,
        is_superuser=False,
        roles=["user"],
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    # Count should still be 1
    count = repo.count_active_users()
    assert count == 1 