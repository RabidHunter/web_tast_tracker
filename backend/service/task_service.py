import psycopg2
from typing import List, Optional
from domain.task import Task

DB_CONFIG = {
    "dbname": "task_tracker",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432",
}


class TaskService:
    def get_all_tasks(self) -> List[Task]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_completed, owner_id FROM tasks ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            Task(id=row[0], name=row[1], is_completed=row[2], owner_id=row[3])
            for row in rows
        ]

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, is_completed, owner_id FROM tasks WHERE id = %s;",
            (task_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return Task(id=row[0], name=row[1], is_completed=row[2], owner_id=row[3])
        return None

    def create_task(self, name: str) -> Task:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (name, is_completed) VALUES (%s, %s) RETURNING id;",
            (name, False),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return Task(id=new_id, name=name, is_completed=False)

    def update_task(
        self,
        task_id: int,
        new_name: Optional[str] = None,
        is_completed: Optional[bool] = None,
    ) -> Optional[Task]:
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        if new_name is not None:
            task.change_name(new_name)
        if is_completed is not None:
            if is_completed:
                task.mark_as_completed()
            else:
                task.mark_as_uncompleted()

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET name = %s, is_completed = %s WHERE id = %s;",
            (task.name, task.is_completed, task.id),
        )
        conn.commit()
        cur.close()
        conn.close()

        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
