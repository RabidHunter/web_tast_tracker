Опис системи та архітектури в Kubernetes

1. Сервіс: Я моделюю веб-застосунок Task Tracker API (FastAPI бекенд). Його призначення — обробка CRUD-запитів для управління списками завдань користувачів.

2. Трафік та маршрутизація: Зовнішній користувач надсилає запит на домен api.tasktracker.com. Запит через DNS потрапляє на Ingress Controller кластера Kubernetes. Ingress аналізує Host і Path (/tasks) та перенаправляє трафік на внутрішній Service з ім'ям task-api-svc (тип ClusterIP). Далі Service балансує навантаження між працюючими Pod-ами.

3. Розгортання в кластері: Сервіс розміщено всередині Namespace під назвою prod. Об'єкт Deployment з ім'ям task-api-deployment керує 2 репліками Pod-ів (task-api-pod-1, task-api-pod-2) для забезпечення базової відмовостійкості та високої доступності (якщо один Pod впаде, інший продовжить обробку).

4. CI/CD та Registry: Код зберігається в git-репозиторії github.com/user/task-tracker. При створенні git push спрацьовує GitHub Actions (CI/CD), який збирає Docker-образ і пушить його у GitHub Container Registry (ghcr.io/user/task-api:1.0.0). Під час старту Deployment в Kubernetes Pod-и автоматично викачують цей образ із Registry.