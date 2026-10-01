-- Seed script for standalone testing environment (docker-compose.test.yml)
-- Mounted into db-test at /docker-entrypoint-initdb.d/init.sql

BEGIN;

CREATE TABLE IF NOT EXISTS applications (
    id              UUID PRIMARY KEY,
    company         VARCHAR(255) NOT NULL,
    role            VARCHAR(255) NOT NULL,
    url             VARCHAR(1024),
    status          VARCHAR(32) NOT NULL DEFAULT 'wishlist',
    date_applied    DATE,
    follow_up_date  DATE,
    contact_name    VARCHAR(255),
    description     TEXT,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resumes (
    id          UUID PRIMARY KEY,
    content     TEXT NOT NULL DEFAULT '',
    updated_at  TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tailored_resumes (
    id             UUID PRIMARY KEY,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    content        TEXT NOT NULL,
    source         VARCHAR(64) NOT NULL,
    created_at     TIMESTAMP DEFAULT now()
);

-- 1. Base / Master Resume
INSERT INTO resumes (id, content, updated_at)
VALUES (
    'a0000000-0000-4000-8000-000000000001',
    $resume$# Alex Morgan
Senior Full-Stack Engineer | Remote / San Francisco, CA
alex.morgan@example.com | (555) 234-5678 | github.com/alexmorgan | linkedin.com/in/alexmorgan

## Summary
Experienced Full-Stack Software Engineer with 7+ years of experience designing and scaling web applications, microservices, and distributed cloud architectures. Proven expertise in Python, FastAPI, Vue.js, PostgreSQL, and Docker. Passionate about clean code, high performance, and intuitive user experiences.

## Technical Skills
- **Languages:** Python, JavaScript (ES6+), TypeScript, SQL, HTML5, CSS3
- **Frameworks & Libraries:** FastAPI, Vue 3, Vite, Tailwind CSS, SQLAlchemy, Pydantic, Node.js
- **Databases & Caching:** PostgreSQL, Redis, SQLite
- **DevOps & Cloud:** Docker, Docker Compose, AWS (S3, ECS, RDS), CI/CD (GitHub Actions), Linux
- **Testing & Tools:** Pytest, Git, Vite, Postman, Celery

## Professional Experience

### Senior Software Engineer | NexaCloud Systems (2021 – Present)
- Architected and deployed microservices handling 25,000+ daily active users using FastAPI and PostgreSQL.
- Reduced database p95 response times by 35% through connection pooling, index optimization, and Redis caching.
- Spearheaded frontend rewrite to Vue 3 and Tailwind CSS, increasing page load speed by 40%.
- Mentored junior engineers, led weekly code reviews, and championed unit test coverage targets (85%+).

### Software Engineer | Streamline Dynamics (2018 – 2021)
- Developed RESTful APIs and asynchronous background tasks using Python, Celery, and PostgreSQL.
- Designed responsive user interfaces with Vue.js, Pinia, and modern CSS tooling.
- Built automated database backup and point-in-time recovery workflows using containerized cron services.
- Collaborated cross-functionally with product managers and UX designers to deliver 12 major releases on schedule.

## Education
**B.S. in Computer Science** | University of California, Berkeley (2014 – 2018)
$resume$,
    now()
)
ON CONFLICT (id) DO NOTHING;

-- 2. Applications (8 realistic applications across all 6 columns)

-- Wishlist (2): with job descriptions, URLs, notes
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000001',
     'Stripe',
     'Staff Infrastructure Engineer',
     'https://stripe.com/jobs/infrastructure-engineer',
     'wishlist',
     NULL,
     NULL,
     'David Chen',
     $desc$Join the Core Platform team to design next-generation multi-tenant cloud infrastructure and developer runtime primitives. Requirements: 6+ years backend experience, deep knowledge of distributed systems, high-availability PostgreSQL, and container orchestration.$desc$,
     $notes$Spoke with David at a distributed systems meetup. Need to tailor resume emphasizing database reliability and connection pooling before applying.$notes$,
     now() - interval '5 days',
     now() - interval '5 days'),

    ('b0000000-0000-4000-8000-000000000002',
     'Linear',
     'Senior Full-Stack Engineer',
     'https://linear.app/careers/full-stack-engineer',
     'wishlist',
     NULL,
     NULL,
     'Karri Saarinen',
     $desc$Help us build sync engines and snappy frontend interfaces. We obsess over milliseconds and keyboard navigation. Stack: TypeScript, Vue/React, Node, PostgreSQL, WebSockets.$desc$,
     $notes$Dream role. Highly collaborative remote team with high bar for UI polish. Polish personal portfolio with fast keyboard navigation demo before submitting.$notes$,
     now() - interval '3 days',
     now() - interval '3 days');

-- Applied (2): 1 overdue yesterday (Overdue badge), 1 due today (Due Today badge)
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000003',
     'Vercel',
     'Senior Platform Engineer',
     'https://vercel.com/careers/senior-platform-engineer',
     'applied',
     CURRENT_DATE - 14,
     CURRENT_DATE - 1,
     'Alex Liu (Recruiter)',
     $desc$Building developer experience infrastructure and global edge compute primitives. Seeking strong engineers proficient in Python/Go, edge runtimes, and distributed state.$desc$,
     $notes$Applied via employee referral from Marcus. Follow-up was due yesterday—send friendly check-in note to Alex today.$notes$,
     now() - interval '14 days',
     now() - interval '1 day'),

    ('b0000000-0000-4000-8000-000000000004',
     'Datadog',
     'Backend Software Engineer - APM',
     'https://datadoghq.com/careers/backend-apm',
     'applied',
     CURRENT_DATE - 7,
     CURRENT_DATE,
     'Rachel Adams',
     $desc$Datadog APM tracing team builds high-throughput ingest collectors and trace aggregation engines processing trillions of events weekly in Python and Go.$desc$,
     $notes$Application submitted last week. Follow-up is due today; send message inquiring about review timeline.$notes$,
     now() - interval '7 days',
     now());

-- Interviewing (1): contact_name 'Sarah Jenkins', upcoming follow_up_date next week, notes
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000005',
     'GitLab',
     'Senior Backend Engineer, CI/CD Platform',
     'https://gitlab.com/jobs/sr-backend-engineer',
     'interviewing',
     CURRENT_DATE - 20,
     CURRENT_DATE + 7,
     'Sarah Jenkins',
     $desc$GitLab is 100% remote. Seeking a Senior Backend Engineer to build scalable job runner queues, artifact caching systems, and high-performance workflow execution APIs.$desc$,
     $notes$Completed technical screen and system design round with Sarah Jenkins. Round 3 (Executive & Team Culture) scheduled for next week. Review GitLab CI runner architecture and async task patterns beforehand.$notes$,
     now() - interval '20 days',
     now() - interval '2 days');

-- Offer (1): with salary and exciting notes
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000006',
     'Supabase',
     'Staff Software Engineer - Database Cloud',
     'https://supabase.com/careers/staff-software-engineer',
     'offer',
     CURRENT_DATE - 30,
     NULL,
     'Paul Copplestone',
     $desc$Lead developer-facing database primitives and cloud management services for PostgreSQL. Work on real-time CDC, backup orchestration, and multi-region replication.$desc$,
     $notes$🎉 Received written offer!
- Base Salary: $185,000 USD
- Equity: $65,000/year (4-year vesting, 1-year cliff)
- Benefits: Full health/dental, $3,000 home office stipend, flexible PTO
- Reviewing terms; deadline to sign is Friday afternoon.$notes$,
     now() - interval '30 days',
     now() - interval '1 day');

-- Rejected (1): with polite rejection notes
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000007',
     'Airbnb',
     'Senior Backend Engineer - Payments',
     'https://careers.airbnb.com/positions/sr-backend-engineer-payments',
     'rejected',
     CURRENT_DATE - 45,
     NULL,
     'Megan Taylor',
     $desc$Responsible for global checkout flows, ledger immutability, foreign currency conversion, and fraud mitigation microservices at international scale.$desc$,
     $notes$Received courteous email rejection after final stage: team decided to proceed with an internal candidate who already had deep familiarity with their internal transaction ledger. Recruiter Megan invited reconnecting in 6 months for upcoming new team expansions.$notes$,
     now() - interval '45 days',
     now() - interval '10 days');

-- Cancelled (1): with role cancelled / candidate withdrew notes
INSERT INTO applications (id, company, role, url, status, date_applied, follow_up_date, contact_name, description, notes, created_at, updated_at)
VALUES
    ('b0000000-0000-4000-8000-000000000008',
     'Cloudscale Technologies',
     'Principal Systems Architect',
     'https://cloudscale.example.com/careers/principal-architect',
     'cancelled',
     CURRENT_DATE - 25,
     NULL,
     'Marcus Vance',
     $desc$Drive architectural direction for cloud infrastructure modernization, Kubernetes migrations, and site reliability engineering across distributed data centers.$desc$,
     $notes$Role cancelled: Hiring manager Marcus informed me that the company initiated an organizational restructuring and froze hiring for this requisition indefinitely. Candidate withdrew from any further pipeline updates.$notes$,
     now() - interval '25 days',
     now() - interval '5 days');

-- 3. Sample Tailored Resumes (2 linked to applications)

-- Tailored Resume 1: Linked to GitLab (Interviewing)
INSERT INTO tailored_resumes (id, application_id, content, source, created_at)
VALUES (
    'c0000000-0000-4000-8000-000000000001',
    'b0000000-0000-4000-8000-000000000005',
    $tailored$# Alex Morgan
Senior Full-Stack Engineer — Tailored for GitLab CI/CD Platform
alex.morgan@example.com | (555) 234-5678 | Remote

## Targeted Summary
Senior Engineer with extensive background in distributed workflow execution, queue workers, and high-performance asynchronous API services. Deep technical experience with PostgreSQL schema optimization, Celery/Redis task orchestration, and containerized CI runners.

## Relevant Technical Highlights
- Architected asynchronous event queues and worker pools capable of handling 25k+ daily tasks with sub-second scheduling overhead.
- Engineered automated container lifecycle pipelines with Docker and Kubernetes, reducing build queue wait times by 45%.
- Authored robust transactional data models in PostgreSQL ensuring zero data loss during high-concurrency job state transitions.
$tailored$,
    'claude',
    now() - interval '3 days'
)
ON CONFLICT (id) DO NOTHING;

-- Tailored Resume 2: Linked to Supabase (Offer)
INSERT INTO tailored_resumes (id, application_id, content, source, created_at)
VALUES (
    'c0000000-0000-4000-8000-000000000002',
    'b0000000-0000-4000-8000-000000000006',
    $tailored$# Alex Morgan
Staff Software Engineer — Tailored for Supabase Database Cloud
alex.morgan@example.com | (555) 234-5678 | Remote

## Targeted Summary
Systems and database-focused Software Engineer with 7+ years optimizing relational databases, architecting real-time APIs, and designing developer-first cloud infrastructure. Passionate advocate for open source PostgreSQL tooling.

## Key Accomplishments
- Implemented automated database backup and point-in-time snapshot orchestration with background retention policies.
- Cut database p95 response times by 35% through connection pooling, query indexing, and advisory locking strategies.
- Designed real-time event streaming and change data capture interfaces for mission-critical client services.
$tailored$,
    'chatgpt',
    now() - interval '8 days'
)
ON CONFLICT (id) DO NOTHING;

-- Ensure permissions for jobsearch user
ALTER TABLE applications OWNER TO jobsearch;
ALTER TABLE resumes OWNER TO jobsearch;
ALTER TABLE tailored_resumes OWNER TO jobsearch;
GRANT ALL ON SCHEMA public TO jobsearch;
GRANT ALL ON ALL TABLES IN SCHEMA public TO jobsearch;

COMMIT;
