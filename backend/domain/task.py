from typing import Optional


class Task:
    def __init__(
        self,
        id: Optional[int],
        name: str,
        is_completed: bool = False,
        owner_id: Optional[int] = None,
    ):
        if not name.strip():
            raise ValueError("Task name cannot be empty")

        self.id = id
        self.name = name
        self.is_completed = is_completed
        self.owner_id = owner_id

    def mark_as_completed(self):
        self.is_completed = True

    def mark_as_uncompleted(self):
        self.is_completed = False

    def change_name(self, new_name: str):
        if not new_name.strip():
            raise ValueError("New task name cannot be empty")
        self.name = new_name
