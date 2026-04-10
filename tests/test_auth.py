import pytest
from unittest.mock import MagicMock, patch
from lib.auth import (
    init_session, get_user, get_profile, sync_session_state,
    handle_oauth_callback, sign_in, sign_up, logout
)


class SessionStateMock(dict):
    """Mock Streamlit's session_state that supports both dict and attribute access."""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __contains__(self, key):
        return super().__contains__(key)


@pytest.fixture
def mock_st():
    """Mock Streamlit's st module."""
    with patch('lib.auth.st') as mock:
        mock.session_state = SessionStateMock()
        mock.query_params = {}
        yield mock


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('lib.auth.supabase') as mock:
        yield mock


@pytest.fixture
def mock_logger():
    """Mock the logger."""
    with patch('lib.auth.logger') as mock:
        yield mock


class TestInitSession:
    def test_init_session_creates_required_keys(self, mock_st):
        """Test that init_session initializes all necessary session state keys."""
        init_session()
        
        assert "user" in mock_st.session_state
        assert "profile" in mock_st.session_state
        assert "repository" in mock_st.session_state
        assert mock_st.session_state["user"] is None
        assert mock_st.session_state["profile"] is None
        assert mock_st.session_state["repository"] is not None

    def test_init_session_does_not_overwrite_existing_keys(self, mock_st):
        """Test that init_session preserves existing session state values."""
        mock_st.session_state["user"] = "existing_user"
        mock_st.session_state["profile"] = {"name": "John"}
        
        init_session()
        
        assert mock_st.session_state["user"] == "existing_user"
        assert mock_st.session_state["profile"] == {"name": "John"}


class TestGetUser:
    def test_get_user_returns_current_user(self, mock_st):
        """Test that get_user returns the user from session state."""
        mock_user = MagicMock(id="user123", email="user@example.com")
        mock_st.session_state = {"user": mock_user}
        
        result = get_user()
        
        assert result == mock_user
        assert result.id == "user123"

    def test_get_user_returns_none_when_not_logged_in(self, mock_st):
        """Test that get_user returns None when no user is logged in."""
        mock_st.session_state = {"user": None}
        
        result = get_user()
        
        assert result is None


class TestGetProfile:
    def test_get_profile_returns_cached_profile(self, mock_st):
        """Test that get_profile returns cached profile without DB call."""
        cached_profile = {"id": "user123", "display_name": "John Doe"}
        mock_st.session_state["profile"] = cached_profile
        mock_st.session_state["user"] = MagicMock(id="user123")
        
        result = get_profile()
        
        assert result == cached_profile

    def test_get_profile_fetches_from_db_when_not_cached(self, mock_st, mock_supabase):
        """Test that get_profile fetches from database when profile is not cached."""
        mock_user = MagicMock(id="user123")
        mock_st.session_state["profile"] = None
        mock_st.session_state["user"] = mock_user
        
        profile_data = {"id": "user123", "display_name": "Jane Doe"}
        mock_response = MagicMock(data=profile_data)
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        result = get_profile()
        
        assert result == profile_data

    def test_get_profile_returns_none_when_no_user_logged_in(self, mock_st):
        """Test that get_profile returns None when no user is logged in."""
        mock_st.session_state["profile"] = None
        mock_st.session_state["user"] = None
        
        result = get_profile()
        
        assert result is None

    def test_get_profile_handles_db_error(self, mock_st, mock_supabase, mock_logger):
        """Test that get_profile handles database errors gracefully."""
        mock_user = MagicMock(id="user123")
        mock_st.session_state["profile"] = None
        mock_st.session_state["user"] = mock_user
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("DB error")
        
        result = get_profile()
        
        assert result is None
        mock_logger.error.assert_called_once()


class TestSyncSessionState:
    def test_sync_session_state_with_valid_session(self, mock_st, mock_supabase):
        """Test that sync_session_state properly syncs a valid Supabase session."""
        mock_session = MagicMock()
        mock_session.user = MagicMock(id="user123", email="user@example.com")
        mock_session.access_token = "token123"
        mock_st.session_state["profile"] = None
        
        sync_session_state(mock_session)
        
        assert mock_st.session_state["supabase_session"] == mock_session
        assert mock_st.session_state["user"] == mock_session.user
        mock_supabase.postgrest.auth.assert_called_once_with("token123")

    def test_sync_session_state_with_none_clears_state(self, mock_st):
        """Test that sync_session_state clears session when passed None."""
        mock_st.session_state["user"] = MagicMock(id="user123")
        mock_st.session_state["profile"] = {"name": "John"}
        mock_st.session_state["supabase_session"] = MagicMock()
        
        sync_session_state(None)
        
        assert mock_st.session_state["user"] is None
        assert mock_st.session_state["profile"] is None
        assert mock_st.session_state["supabase_session"] is None


class TestSignIn:
    def test_sign_in_success(self, mock_supabase, mock_st):
        """Test successful sign-in with email and password."""
        mock_user = MagicMock(id="user123", email="user@example.com")
        mock_session = MagicMock()
        mock_response = MagicMock(user=mock_user, session=mock_session)
        mock_supabase.auth.sign_in_with_password.return_value = mock_response
        mock_st.session_state["profile"] = None
        
        success, error = sign_in("user@example.com", "password123")
        
        assert success is True
        assert error is None
        mock_supabase.auth.sign_in_with_password.assert_called_once_with({
            "email": "user@example.com",
            "password": "password123"
        })

    def test_sign_in_failure_returns_error_message(self, mock_supabase, mock_logger):
        """Test that sign-in returns error message on auth failure."""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")
        
        success, error = sign_in("user@example.com", "wrongpassword")
        
        assert success is False
        assert "Invalid credentials" in error
        mock_logger.error.assert_called_once()


class TestSignUp:
    def test_sign_up_success(self, mock_supabase, mock_st):
        """Test successful user registration."""
        mock_user = MagicMock(id="newuser123", email="newuser@example.com")
        mock_session = MagicMock(access_token="token123")
        mock_response = MagicMock(user=mock_user, session=mock_session)
        mock_supabase.auth.sign_up.return_value = mock_response
        
        success, error = sign_up("newuser@example.com", "password123", "New User")
        
        assert success is True
        assert error is None
        mock_supabase.auth.sign_up.assert_called_once()
        mock_supabase.postgrest.auth.assert_called_once_with("token123")

    def test_sign_up_failure_returns_error(self, mock_supabase, mock_logger):
        """Test that sign-up returns error on failure."""
        mock_supabase.auth.sign_up.side_effect = Exception("Email already exists")
        
        success, error = sign_up("existing@example.com", "password123", "User")
        
        assert success is False
        assert "Email already exists" in error
        mock_logger.error.assert_called_once()


class TestLogout:
    def test_logout_clears_session_and_calls_signout(self, mock_st, mock_supabase):
        """Test that logout clears session state and calls Supabase sign_out."""
        mock_st.session_state["user"] = MagicMock(id="user123")
        mock_st.session_state["profile"] = {"name": "John"}
        
        logout()
        
        mock_supabase.auth.sign_out.assert_called_once()
        assert mock_st.session_state["user"] is None
        assert mock_st.session_state["profile"] is None
        mock_st.rerun.assert_called_once()
