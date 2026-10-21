import os
import psycopg2
from dotenv import load_dotenv
from domain.task import Task
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

class TaskService:
    def get_all_tasks(self) -> list[Task]:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, is_completed, owner_id FROM tasks ORDER BY id;")
                rows = cur.fetchall()
                return [Task(id=row[0], name=row[1], is_completed=row[2], owner_id=row[3]) for row in rows]

    def get_task_by_id(self, task_id: int) -> Task | None:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, is_completed, owner_id FROM tasks WHERE id = %s;", (task_id,))
                row = cur.fetchone()
                
                if row:
                    return Task(id=row[0], name=row[1], is_completed=row[2], owner_id=row[3])
                return None

    def create_task(self, name: str) -> Task:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (name, is_completed) VALUES (%s, %s) RETURNING id;", 
                    (name, False)
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                
        return Task(id=new_id, name=name, is_completed=False)

    def update_task(self, task_id: int, new_name: str | None = None, is_completed: bool | None = None) -> Task | None:
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

        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tasks SET name = %s, is_completed = %s WHERE id = %s;",
                    (task.name, task.is_completed, task.id)
                )
                conn.commit()
                
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            return False
            
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
                conn.commit()
                
        return True