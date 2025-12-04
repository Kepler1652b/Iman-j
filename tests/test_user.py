from datetime import datetime
from database.models import UserBase
from database.db import  UserCRUD





# ============= USER TESTS =============

class TestUserCRUD:
    """Test suite for User CRUD operations"""
    
    def test_create_user(self, session):
        """Test creating a new user"""
        user_data = UserBase(
            username="new_user",
            telegram_id=987654321,
            is_active=True
        )
        user = UserCRUD.create(session, user_data)
        
        assert user.id is not None
        assert user.username == "new_user"
        assert user.telegram_id == 987654321
        assert user.is_active is True
        assert user.is_admin is False
        assert isinstance(user.created_at, datetime)
    
    def test_get_user_by_id(self, session, sample_user):
        """Test retrieving user by ID"""
        user = UserCRUD.get_by_id(session, sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.username == sample_user.username
    
    def test_get_user_by_telegram_id(self, session, sample_user):
        """Test retrieving user by Telegram ID"""
        user = UserCRUD.get_by_telegram_id(session, sample_user.telegram_id)
        
        assert user is not None
        assert user.telegram_id == sample_user.telegram_id
    
    def test_get_nonexistent_user(self, session):
        """Test retrieving non-existent user returns None"""
        user = UserCRUD.get_by_id(session, 99999)
        assert user is None
    
    def test_get_all_users(self, session):
        """Test retrieving all users"""
        # Create multiple users
        for i in range(5):
            user_data = UserBase(
                username=f"user_{i}",
                telegram_id=100000 + i,
                is_active=True
            )
            UserCRUD.create(session, user_data)
        
        users = UserCRUD.get_all(session)
        assert len(users) >= 5
    
    def test_get_all_users_with_pagination(self, session):
        """Test pagination when retrieving users"""
        # Create 10 users
        for i in range(10):
            user_data = UserBase(
                username=f"user_{i}",
                telegram_id=200000 + i,
                is_active=True
            )
            UserCRUD.create(session, user_data)
        
        # Get first page
        page1 = UserCRUD.get_all(session, skip=0, limit=5)
        assert len(page1) == 5
        
        # Get second page
        page2 = UserCRUD.get_all(session, skip=5, limit=5)
        assert len(page2) == 5
        
        # Ensure different users
        assert page1[0].id != page2[0].id
    
    def test_get_active_users(self, session):
        """Test retrieving only active users"""
        # Create active and inactive users
        UserCRUD.create(session, UserBase(username="active1", telegram_id=301, is_active=True))
        UserCRUD.create(session, UserBase(username="active2", telegram_id=302, is_active=True))
        UserCRUD.create(session, UserBase(username="inactive", telegram_id=303, is_active=False))
        
        active_users = UserCRUD.get_active_users(session)
        assert all(user.is_active for user in active_users)
        assert len(active_users) >= 2
    
    def test_get_admins(self, session):
        """Test retrieving admin users"""
        UserCRUD.create(session, UserBase(username="admin", telegram_id=401, is_admin=True))
        UserCRUD.create(session, UserBase(username="user", telegram_id=402, is_admin=False))
        
        admins = UserCRUD.get_admins(session)
        assert all(user.is_admin for user in admins)
    
    def test_update_user(self, session, sample_user):
        """Test updating user information"""
        update_data = {
            "username": "updated_username",
            "is_admin": True
        }
        updated_user = UserCRUD.update(session, sample_user.id, update_data)
        
        assert updated_user is not None
        assert updated_user.username == "updated_username"
        assert updated_user.is_admin is True
        assert updated_user.telegram_id == sample_user.telegram_id  # Unchanged
    
    def test_update_nonexistent_user(self, session):
        """Test updating non-existent user returns None"""
        result = UserCRUD.update(session, 99999, {"username": "test"})
        assert result is None
    
    def test_delete_user(self, session, sample_user):
        """Test deleting a user"""
        user_id = sample_user.id
        result = UserCRUD.delete(session, user_id)
        
        assert result is True
        assert UserCRUD.get_by_id(session, user_id) is None
    
    def test_delete_nonexistent_user(self, session):
        """Test deleting non-existent user returns False"""
        result = UserCRUD.delete(session, 99999)
        assert result is False
