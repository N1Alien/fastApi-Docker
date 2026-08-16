# FastAPI + PostgreSQL (pgvector) w chmurze Render

Projekt demonstracyjny przedstawiający implementację bazy wektorowej oraz wyszukiwania semantycznego przy użyciu **FastAPI**, **PostgreSQL** z rozszerzeniem **pgvector** oraz **Dockera**, wdrożony w chmurze produkcyjnej **Render**.

## 🚀 Publiczny Link do Aplikacji (Swagger UI)

Aplikacja jest w pełni wdrożona i dostępna publicznie pod poniższym adresem:
👉 **[https://fastapi-docker-i29z.onrender.com/docs](https://fastapi-docker-i29z.onrender.com/docs)**

---

## 🧭 Co dokładnie dzieje się pod maską?

Gdy otwierasz powyższy link i wywołujesz endpoint `POST /szukaj-wektorem/`, w architekturze chmurowej zachodzi zaawansowany proces podzielony na kilka etapów:

1. **Publiczny Request HTTP**: Twoja przeglądarka wysyła żądanie przez internet. Trafia ono do serwerów platformy Render (w centrum danych we Frankfurcie), gdzie w odizolowanym środowisku działa kontener Docker z aplikacją FastAPI.
2. **Generowanie Wektora (Embeddingu)**: Kod w Pythonie (korzystając z biblioteki `NumPy`) generuje wielowymiarowy wektor składający się z 1536 liczb zmiennoprzecinkowych. W docelowych systemach RAG (Retrieval-Augmented Generation) w tym miejscu model językowy (np. OpenAI text-embedding-3) zamienia wpisany przez użytkownika tekst na matematyczny zapis jego znaczenia semantycznego.
3. **Wyszukiwanie Semantyczne w Bazie (pgvector)**: Aplikacja przekazuje ten wektor do bazy danych PostgreSQL. Dzięki wtyczce `pgvector` oraz operatorowi odległości cosinusowej (`<=>`), baza danych porównuje ten wektor w wielwymiarowej przestrzeni z rekordami zapisanymi podczas startu systemu (np. artykułem o AI oraz przepisem na obiad).
4. **Kalkulacja Podobieństwa**: PostgreSQL nie szuka identycznych słów kluczowych – zamiast tego mierzy kąt i odległość matematyczną między wektorami. Im mniejsza odległość, tym większe podobieństwo znaczeniowe (semantyczne) między tekstami.
5. **Odpowiedź JSON**: Najlepiej dopasowane rekordy wraz z wyliczonym współczynnikiem podobieństwa (`similarity`) są zwracane przez FastAPI bezpośrednio do Twojej przeglądarki z kodem statusu **200 OK**.

---

## 🛠️ Struktura Projektu

Projekt składa się z następujących komponentów pracujących w jednym ekosystemie:
*   `main.py` – Aplikacja FastAPI zarządzająca endpointami, automatyczną inicjalizacją rozszerzenia wektorowego w bazie oraz logiką wyszukiwania.
*   `Dockerfile` – Wieloetapowy (multi-stage) plik konfiguracyjny budujący zoptymalizowany, lekki obraz kontenera z aplikacją.
*   `docker-compose.yml` – Konfiguracja lokalnego środowiska deweloperskiego (aplikacja + baza danych).
*   `requirements.txt` – Spis wszystkich niezbędnych zależności Pythona (`sqlalchemy`, `pgvector`, `numpy`, `fastapi`, `uvicorn`, `psycopg2-binary`).

---

## 🐳 Jak uruchomić projekt lokalnie?

Jeśli chcesz uruchomić to środowisko na własnym komputerze, upewnij się, że masz zainstalowanego Dockera, a następnie wykonaj w folderze projektu:

```bash
docker compose up --build
```

Aplikacja lokalna będzie dostępna pod adresem: `http://localhost:8000/docs`
