from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

app = FastAPI()

# Налаштування CORS, щоб React міг робити запити до бекенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Параметри підключення до БД (замініть user та password на свої)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432",
}


@app.get("/items")
def get_items():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT id, name, is_completed FROM items ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Форматуємо результат у список JSON-об'єктів
    return [{"id": row[0], "name": row[1], "is_completed": row[2]} for row in rows]
