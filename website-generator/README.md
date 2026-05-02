# ⚡ WebGen — AI Website Builder SaaS

> Generate complete, production-ready websites from a single sentence. No coding required.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![License MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Deploy on Render](https://img.shields.io/badge/deploy-render-purple.svg)](https://render.com)

---

## What is WebGen?

WebGen is a multi-user SaaS platform that converts natural language prompts into complete, downloadable website projects. Users describe what they want, and the AI engine generates every file — HTML, CSS, JavaScript, Python/Flask backend, SQLite database, and deployment instructions.

**Example prompts:**
- `"Create a dark portfolio website with animations"`
- `"Build an e-commerce site like Meesho with seller dashboard"`
- `"Make a startup landing page with pricing and waitlist"`
- `"Create a blog CMS with admin panel using Python"`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        WebGen SaaS                          │
├──────────────┬──────────────────────┬───────────────────────┤
│   Frontend   │      Backend         │      AI Engine        │
│              │                      │                       │
│  Dashboard   │  Flask + Blueprints  │  NLP Intent Parser    │
│  Wizard UI   │  Auth (session)      │  Prompt Optimizer     │
│  Live Editor │  Billing (Stripe)    │  Code Generator       │
│  Code Viewer │  Rate Limiting       │  Response Validator   │
│  Preview     │  API Key Auth        │  (OpenAI optional)    │
├──────────────┴──────────────────────┴───────────────────────┤
│                      Data Layer                             │
│  SQLite (dev) │ PostgreSQL (prod) │ Local/S3 file storage   │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Free | Pro | Business |
|---------|------|-----|----------|
| AI Generations / hour | 5 | 100 | 500 |
| Max Projects | 3 | 50 | 200 |
| Project Types | Static, Flask | All 6 | All 6 |
| Live Editor | ✓ | ✓ | ✓ |
| Version History | — | ✓ | ✓ |
| API Access | — | — | ✓ |
| Price | Free | $9.99/mo | $29.99/mo |

**6 Project Types:**
- 🌐 **Static** — HTML/CSS/JS, no server needed
- 🐍 **Flask** — Python backend with SQLite, optional auth
- 🛍️ **E-commerce** — Seller dashboard, product CRUD, orders
- 🚀 **Startup** — Landing page with waitlist, pricing, FAQ
- ✍️ **Blog CMS** — Post editor, categories, comments, admin
- 🎨 **Portfolio** — Animated dark theme with typewriter effect

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/webgen-saas.git
cd webgen-saas/website-generator
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY
```

### 3. Run

```bash
python app.py
# Open http://localhost:5000
```

---

## Project Structure

```
website-generator/
├── app.py                  # Main Flask application
├── config.py               # Environment-aware configuration
├── db.py                   # SQLite database layer
├── generator.py            # Code generation engine (6 project types)
├── nlp.py                  # Natural language intent parser
├── planner.py              # Architecture planning engine
├── codegen.py              # Structured output generator
├── billing.py              # Stripe subscription system
├── rate_limiter.py         # Per-user rate limiting + API keys
├── cache.py                # Prompt caching + minor-edit detection
│
├── ai_engine/              # AI enhancement layer
│   ├── optimizer.py        # Prompt optimizer (+ OpenAI mode)
│   ├── validator.py        # Response validator
│   └── openai_gen.py       # OpenAI integration
│
├── utils/                  # Production utilities
│   ├── logger.py           # Structured logging (JSON in prod)
│   ├── security.py         # CSRF, security headers, sanitization
│   └── health.py           # Health check endpoints
│
├── app/                    # Modular Flask package
│   ├── routes/             # Blueprints: auth, dashboard, generate...
│   ├── models/             # UserModel, ProjectModel
│   └── services/           # AIEngine, FileService
│
├── templates/              # Jinja2 HTML templates
├── static/css/style.css    # Platform stylesheet
├── generated/              # Generated project output
│
├── Procfile                # Render/Heroku deployment
├── runtime.txt             # Python version
├── Dockerfile              # Container deployment
├── docker-compose.yml      # Local Docker setup
├── .env.example            # Environment template
└── .github/workflows/      # CI/CD pipeline
```

---

## Deployment

### Render (Recommended — Free Tier)

1. Push to GitHub
2. Create new **Web Service** on [render.com](https://render.com)
3. Connect your repository
4. Set environment variables:
   ```
   SECRET_KEY=<random-64-char-string>
   FLASK_ENV=production
   ```
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
7. Deploy

### Railway

```bash
railway login
railway init
railway up
```

Set environment variables in the Railway dashboard.

### Docker

```bash
# Build
docker build -t webgen-saas .

# Run
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  -e FLASK_ENV=production \
  -v $(pwd)/generated:/app/generated \
  webgen-saas
```

### Docker Compose

```bash
docker-compose up --build
```

### AWS EC2

```bash
# On EC2 instance (Ubuntu 22.04)
sudo apt update && sudo apt install -y python3.11 python3-pip nginx
git clone <your-repo> && cd website-generator
pip install -r requirements.txt
gunicorn app:app --bind 127.0.0.1:5000 --daemon
# Configure nginx as reverse proxy (see nginx.conf)
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Flask session secret (64+ random chars) |
| `FLASK_ENV` | ✅ | `development` or `production` |
| `PORT` | — | Server port (default: 5000) |
| `STRIPE_SECRET_KEY` | — | Stripe secret key (billing) |
| `STRIPE_PUBLISHABLE_KEY` | — | Stripe public key |
| `STRIPE_WEBHOOK_SECRET` | — | Stripe webhook signing secret |
| `STRIPE_PRO_PRICE_ID` | — | Stripe price ID for Pro plan |
| `STRIPE_BIZ_PRICE_ID` | — | Stripe price ID for Business plan |
| `OPENAI_API_KEY` | — | OpenAI API key (enhances generation) |
| `OPENAI_MODEL` | — | OpenAI model (default: gpt-4o-mini) |
| `DATABASE_URL` | — | PostgreSQL URL (SQLite used if not set) |
| `LOG_LEVEL` | — | Logging level (default: INFO) |

---

## API Reference

### Authentication
All API endpoints require either:
- Session cookie (browser users)
- `Authorization: Bearer wg_<key>` header (API users — Business plan)

### Endpoints

```
POST /api/v1/generate
  Body: { "prompt": "Create a portfolio website" }
  Returns: { project_id, files, type, folder_tree, run_instructions }

GET  /health          → Basic health check
GET  /health/ready    → Readiness check (DB connectivity)
GET  /health/live     → Liveness check (uptime)

GET  /api/themes      → List all available themes
GET  /api/theme/:name → Get theme config
```

### Example API Call

```bash
curl -X POST https://your-app.onrender.com/api/v1/generate \
  -H "Authorization: Bearer wg_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a dark portfolio website with animations"}'
```

---

## Stripe Setup

1. Create account at [stripe.com](https://stripe.com)
2. Create two products: **Pro** ($9.99/mo) and **Business** ($29.99/mo)
3. Copy the Price IDs to your `.env`
4. Set up webhook endpoint: `https://your-domain.com/stripe/webhook`
5. Add webhook events: `checkout.session.completed`, `customer.subscription.deleted`

> **Dev mode:** Without Stripe keys, clicking "Upgrade" instantly upgrades the account (mock mode). Perfect for testing.

---

## Admin Access

Create an admin user:

```bash
python -c "
import sys; sys.path.insert(0, '.')
import db
from werkzeug.security import generate_password_hash
db.init_db()
conn = db.get_db()
conn.execute(
    'INSERT INTO users (username, email, password, is_admin) VALUES (?,?,?,1)',
    ('admin', 'admin@example.com', generate_password_hash('admin123'))
)
conn.commit()
print('Admin created: admin / admin123')
"
```

Then visit `/admin` and `/admin/analytics`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Database | SQLite (dev), PostgreSQL (prod) |
| Auth | Session-based + API keys |
| Payments | Stripe |
| AI | Keyword NLP + optional OpenAI |
| Server | Gunicorn |
| Container | Docker |
| CI/CD | GitHub Actions |
| Hosting | Render / Railway / AWS |

---

## License

MIT — free to use, modify, and deploy commercially.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

*Built with ⚡ by the WebGen team*
