import pytest
from unittest.mock import MagicMock
from lib.repository import StudyPlannerRepository
from lib.models import Task

class TestStudyPlannerRepository:
    @pytest.fixture
    def mock_supabase(self):
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_supabase):
        return StudyPlannerRepository(mock_supabase)

    def test_get_tasks_for_user_success(self, repo, mock_supabase):
        # Mock successful response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": 1, "user_id": "user123", "task": "Study"}]
        )
        tasks = repo.get_tasks_for_user("user123")
        assert len(tasks) == 1
        assert tasks[0].title == "Study"

    def test_get_tasks_for_user_failure(self, repo, mock_supabase):
        # Mock exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        tasks = repo.get_tasks_for_user("user123")
        assert tasks == []  

    def test_add_task_success(self, repo, mock_supabase):
        task = Task(
            id=None, 
            user_id="user123",
            title="Study Math",
            subject="Mathematics",
            hours=2.0,
            deadline=None,
            difficulty=3,
            completed_percent=0,
            description="Chapter 5"
        )
        
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "user_id": "user123", "task": "Study Math"}]  
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result = repo.add_task(task)
        
        assert result is not None
        assert result.id == 1
        assert result.title == "Study Math"
    
    def test_add_task_failure(self, repo, mock_supabase):
        task = Task(
            id=None, 
            user_id="user123",
            title="Study Math",
            subject="Mathematics",
            hours=2.0,
            deadline=None,
            difficulty=3,
            completed_percent=0,
            description="Chapter 5"
        )
        
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        
        result = repo.add_task(task)
        
        assert result is None  

    def test_update_task_success(self, repo, mock_supabase):
        task = Task(
            id=1,
            user_id="user123",
            title="Updated Study",
            subject="Mathematics",
            hours=3.0,
            deadline=None,
            difficulty=4,
            completed_percent=50,
            description="Updated"
        )
        
        mock_response = MagicMock()
        mock_response.data = [{"id": 1, "user_id": "user123", "task": "Updated Study"}]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        result = repo.update_task(task)
        
        assert result is not None
        assert result.id == 1
        assert result.title == "Updated Study"

    def test_update_task_failure(self, repo, mock_supabase):
        task = Task(
            id=1,
            user_id="user123",
            title="Updated Study",
            subject="Mathematics",
            hours=3.0,
            deadline=None,
            difficulty=4,
            completed_percent=50,
            description="Updated"
        )
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        
        result = repo.update_task(task)
        
        assert result is None

    def test_delete_task_success(self, repo, mock_supabase):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        result = repo.delete_task(1)
        
        assert result is True

    def test_delete_task_failure(self, repo, mock_supabase):
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("DB error")
        
        result = repo.delete_task(1)
        
        assert result is False

    def test_get_user_availability_success(self, repo, mock_supabase):
        mock_response = MagicMock()
        mock_response.data = {"availability": {"monday": {"hours": 5}}}
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        
        result = repo.get_user_availability("user123")
        
        assert result == {"monday": {"hours": 5}}

    def test_get_user_availability_failure(self, repo, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("DB error")
        
        result = repo.get_user_availability("user123")
        
        assert result == {}

    def test_update_user_availability_success(self, repo, mock_supabase):
        availability_data = {"monday": {"hours": 6}}
        
        # update_user_availability doesn't return anything, just executes
        repo.update_user_availability("user123", availability_data)
        
        # Verify the call was made
        mock_supabase.table.return_value.update.assert_called_once_with({"availability": availability_data})
        mock_supabase.table.return_value.update.return_value.eq.assert_called_once_with("id", "user123")
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.assert_called_once()
    