import pytest
from unittest.mock import patch, MagicMock
from service.task_service import TaskService


@patch("service.task_service.psycopg2.connect")
def test_create_task_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = [99]

    service = TaskService()
    task = service.create_task("Купити молоко")

    assert task.id == 99
    assert task.name == "Купити молоко"
    assert task.is_completed is False

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("service.task_service.psycopg2.connect")
def test_create_task_validation_error(mock_connect):
    service = TaskService()

    with pytest.raises(ValueError, match="Task name cannot be empty"):
        service.create_task("   ")
