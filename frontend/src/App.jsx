import { useState, useEffect } from "react";
import { fetchWithResilience } from "./lib/http";
import { getOrReuseKey } from "./lib/idempotency";

const API_BASE_URL = "http://localhost:8000";

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [taskName, setTaskName] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [consecutiveFailures, setConsecutiveFailures] = useState(0);
  const [healthStatus, setHealthStatus] = useState("ok");

  const isDegraded = consecutiveFailures >= 3 || healthStatus !== "ok";

  const checkHealth = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1000);

    try {
      const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
      if (res.ok) {
        setHealthStatus("ok");
      } else {
        setHealthStatus("degraded");
      }
    } catch {
      setHealthStatus("degraded");
    } finally {
      clearTimeout(timeoutId);
    }
  };

  useEffect(() => {
    checkHealth();
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    setErrorMsg("");
    try {
      const res = await fetchWithResilience(`${API_BASE_URL}/tasks`, {
        retry: { retries: 2, timeoutMs: 3000 },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTasks(data);
      setConsecutiveFailures(0);
    } catch (err) {
      setConsecutiveFailures((prev) => prev + 1);
      setErrorMsg("Не вдалося завантажити завдання: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!taskName.trim()) return;

    setLoading(true);
    setErrorMsg("");

    try {
      const payload = { name: taskName };
      const idemKey = await getOrReuseKey(payload);

      const res = await fetchWithResilience(`${API_BASE_URL}/tasks`, {
        method: "POST",
        body: JSON.stringify(payload),
        idempotencyKey: idemKey,
        retry: { retries: 2, baseDelayMs: 300, timeoutMs: 3500, jitter: true },
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || `HTTP ${res.status}`);
      }

      setTaskName("");
      setConsecutiveFailures(0);
      await loadTasks();
    } catch (err) {
      setConsecutiveFailures((prev) => prev + 1);
      setErrorMsg("Помилка створення: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "40px auto", fontFamily: "sans-serif", padding: "0 20px" }}>
      <h1>Task Tracker (Practical 5)</h1>

      {isDegraded && (
        <div style={{ padding: "12px", backgroundColor: "#fff3cd", border: "1px solid #ffeeba", borderRadius: "6px", marginBottom: "20px", color: "#856404" }}>
          ⚠️ <strong>Сервіс перевантажено або нестабільний (Degraded Mode).</strong>
          <br />
          Деякі функції тимчасово обмежені для захисту сервера.
        </div>
      )}

      {errorMsg && (
        <div style={{ padding: "10px", backgroundColor: "#f8d7da", color: "#721c24", borderRadius: "6px", marginBottom: "20px" }}>
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleCreateTask} style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          type="text"
          value={taskName}
          onChange={(e) => setTaskName(e.target.value)}
          placeholder="Назва нового завдання..."
          disabled={loading || isDegraded}
          style={{ flex: 1, padding: "8px", fontSize: "16px" }}
        />
        <button
          type="submit"
          disabled={loading || isDegraded || !taskName.trim()}
          style={{ padding: "8px 16px", cursor: isDegraded ? "not-allowed" : "pointer" }}
        >
          {loading ? "Створення..." : "Додати"}
        </button>
      </form>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <h2>Список завдань</h2>
        <button onClick={loadTasks} disabled={loading}>Оновити</button>
      </div>

      {tasks.length === 0 ? (
        <p>Завдань немає</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {tasks.map((task) => (
            <li
              key={task.id}
              style={{
                padding: "10px",
                borderBottom: "1px solid #ccc",
                display: "flex",
                justify: "space-between",
                alignItems: "center",
              }}
            >
              <span>{task.name}</span>
              <small style={{ color: "#888" }}>ID: {task.id}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}