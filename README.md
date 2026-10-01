# Job Search Dashboard

A self-hosted kanban-style dashboard for tracking job applications. Built with:

- **Frontend:** Vue 3 (Vite) + Tailwind CSS
- **Backend:** FastAPI + SQLAlchemy
- **Database:** PostgreSQL
- **Dev environment:** Docker Compose (hot reload on both frontend and backend)


## Getting started

```bash
docker compose up --build -d
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at http://localhost:8000/docs)
- Postgres: localhost:5432 (user/pass/db: `jobsearch`)

Both the frontend and backend containers mount your local source as a volume,
so edits to `.vue`, `.py`, etc. hot-reload without rebuilding the image.

## Testing Environment with Pre-Populated Data

To test or demo the application in an isolated sandbox with realistic pre-populated data across all 6 columns without touching your real database or running backups:

```bash
# Start test environment (Frontend :5174, Backend :8001, DB :5433)
docker compose -f docker-compose.test.yml up --build

# Tear down and reset test database
docker compose -f docker-compose.test.yml down -v
```

## Data model

### Applications
Each application has:
- `company`, `role`, `url`
- `status`: `wishlist` | `applied` | `interviewing` | `offer` | `rejected` | `cancelled`
- `date_applied`, `follow_up_date`
- `contact_name`, `description`, `notes`

The board groups applications by status into columns; drag a card between
columns to update its status, or click a card to edit/delete it.

### Resume
Base master resume used for tailoring:
- `id` (UUID)
- `content` (Text markdown/plain text)
- `updated_at` (DateTime)

### Tailored Resume
Versioned resumes tailored per application:
- `id` (UUID)
- `application_id` (UUID foreign key -> applications.id)
- `content` (Text)
- `source` (String: e.g. "chatgpt", "claude", "gemini", "manual")
- `created_at` (DateTime)

## API endpoints

| Method | Path                                   | Description                     |
|--------|----------------------------------------|---------------------------------|
| GET    | /api/applications/                     | List all (optional `?status=`)  |
| POST   | /api/applications/                     | Create an application            |
| GET    | /api/applications/{id}                 | Get one                          |
| PATCH  | /api/applications/{id}                 | Partial update                   |
| DELETE | /api/applications/{id}                 | Delete                           |
| GET    | /api/applications/{id}/tailor-prompt   | Generate tailoring prompt       |
| GET    | /api/applications/{id}/tailored-resumes| List tailored resume history    |
| POST   | /api/applications/{id}/tailored-resumes| Save a tailored resume version  |
| POST   | /api/applications/{id}/tailored-resumes/generate-local | Generate tailored resume via local LLM |
| GET    | /api/applications/{id}/cover-letter/prompt | Generate cover letter prompt    |
| POST   | /api/applications/{id}/cover-letter/generate-local | Generate cover letter via local LLM |
| GET    | /api/applications/{id}/outreach/prompt | Generate outreach email prompt (optional `?template_type=`) |
| POST   | /api/applications/{id}/outreach/generate-local | Generate outreach email via local LLM |
| GET    | /api/resume                            | Get base master resume          |
| PUT    | /api/resume                            | Update base master resume       |
| POST   | /api/resume/extract-preview            | Extract text preview from resume file (.pdf, .docx, .txt) |
| POST   | /api/resume/upload                     | Upload resume file and save content directly |
| GET    | /api/stats                             | Application pipeline stats & metrics |
| GET    | /api/health                            | Health check                     |

## Database Backups & Restore

PostgreSQL database snapshots are automatically saved to `~/!db_backups` on your local host (configurable via `BACKUP_DIR` in `.env`, see `.env.example`).

### Automated Backups
Backups run **automatically in the background** via the `backup-cron` container:
- Takes a snapshot immediately whenever Docker Compose starts.
- Recurs every 6 hours (`0 */6 * * *`) automatically.
- Automatically retains the 5 most recent snapshots and prunes older files.

To view live automated backup logs:
```bash
docker compose logs -f backup-cron
```

### Manual / On-Demand Backup
You can also trigger an immediate backup snapshot at any time:
```bash
bash scripts/backup_db.sh
```

### Restore from a Backup
To restore the database from any snapshot file in `~/!db_backups`:
```bash
cat ~/!db_backups/jobsearch_backup_<TIMESTAMP>.sql | docker compose exec -T db psql -U jobsearch jobsearch
```