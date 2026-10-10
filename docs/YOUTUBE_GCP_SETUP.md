# YouTube для Єви — підключення через Google Cloud

**Статус:** погоджено Андрієм 2026-10-10 (YouTube Data API v3, офіційний). Права (`grants`) порожні.
Секрети в репозиторії не зберігаються. Підключення виконує Андрій у своєму Google Cloud-проєкті, потім секрети лягають у Vault.

## Межі

- Тільки офіційний **YouTube Data API v3**. Завантаження відео чи аудіо з YouTube заборонено (`config/agents/eva.profile.json`, `not_allowed`).
- YouTube Music — окремо, рішення ще не прийнято (неофіційний доступ ризикує акаунтом).
- Scope: лише читання (`https://www.googleapis.com/auth/youtube.readonly`). Публікація відео — окремий шлях (`content_factory/publisher.py`), тут не використовується.
- Дані з YouTube — джерело рівня C (`src/agents/doc_knowledge.py`), не факт без перевірки.

## Кроки в Google Cloud (виконує Андрій)

1. Створити проєкт у Google Cloud Console (наприклад, `syndicate-youtube`).
2. **APIs & Services → Library** → увімкнути **YouTube Data API v3**.
3. **OAuth consent screen**: тип External, додати Андрія як тестового користувача. Scope — лише `youtube.readonly`.
4. **Credentials → Create credentials → OAuth client ID** (тип Desktop або Web). Отримані `client_id` і `client_secret` нікуди не копіювати в git.
5. Пройти OAuth-згоду один раз, щоб отримати refresh token (лише для приватних плейлистів, які Андрій явно вкаже). Публічні дані можна читати звичайним API-ключем.
6. **Квота:** стандартна квота Data API — 10 000 одиниць на добу. Перевірити в **Quotas** перед запуском.
7. Записати секрети у Vault за шляхом сервісу `youtube` з `src/vault_paths.py` (`secret/data/eva-syndicate/youtube`). Політика `eva-agent` уже дозволяє читання цього шляху. Імена полів визначить коннектор при реалізації.

## Що далі (не зроблено)

- Коннектор `src/integrations/youtube.py`: читання через Vault, помилка `unavailable` без ключів, лише читання, rate limit.
- Тести коннектора на живому API — після того, як Андрій передасть облікові дані на деплої.
- Перевірити, що відповіді YouTube в агентів позначаються як джерело з рівнем C.
