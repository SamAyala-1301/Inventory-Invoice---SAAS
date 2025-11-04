
# Inventory & Invoice Management SaaS

A multi-tenant SaaS platform for inventory and invoice management built with Django REST Framework and React.

---

## 🚀 Sprint 1 Features

**Backend (Django + DRF)**
- ✅ Multi-tenant architecture with row-level isolation
- ✅ JWT authentication with refresh token rotation
- ✅ User registration, login, email verification
- ✅ Organization management (CRUD)
- ✅ Role-based access control (RBAC) with 6 default roles
- ✅ Permission caching with Redis
- ✅ Organization member management
- ✅ Email invitations for team members
- ✅ Rate limiting for security
- ✅ API documentation with Swagger/ReDoc

**Frontend (React + Vite)**
- ✅ User registration and login
- ✅ Protected routes with authentication
- ✅ Organization listing and creation
- ✅ Organization switching
- ✅ Dashboard with role display
- ✅ JWT token management with auto-refresh
- ✅ Zustand state management
- ✅ Tailwind CSS styling

---

## 📋 Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

---

## 🛠️ Setup Instructions

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
```bash
git clone &lt;repository-url&gt;
cd inventory-saas
```

2. **Create environment file**
```bash
cp .env.example .env
```
Edit `.env` and update the following:
```env
DJANGO_SECRET_KEY=&lt;generate-with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'&gt;
JWT_SECRET_KEY=&lt;generate-random-string&gt;
POSTGRES_PASSWORD=&lt;strong-password&gt;
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec api python manage.py migrate
```

5. **Seed roles and permissions**
```bash
docker-compose exec api python manage.py seed_roles
```

6. **Create superuser (optional)**
```bash
docker-compose exec api python manage.py createsuperuser
```

7. **Install frontend dependencies**
```bash
cd frontend
npm install
```

8. **Start frontend development server**
```bash
npm run dev
```

9. **Access the application**
   - **Frontend:** http://localhost:3000
   - **Backend API:** http://localhost:8000/api
   - **API Docs:** http://localhost:8000/api/docs
   - **Admin Panel:** http://localhost:8000/admin

---

### Option 2: Local Setup (Without Docker)

#### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements/development.txt

# Setup environment
cp ../.env.example ../.env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Seed roles and permissions
python manage.py seed_roles

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Start Redis
```bash
redis-server
```

#### Start Celery Worker (optional for emails)
```bash
cd backend
celery -A config worker -l info
```

---

## 🧪 Running Tests

**Backend Tests**
```bash
cd backend
pytest
pytest --cov=apps  # With coverage
```

**Frontend Tests**
```bash
cd frontend
npm test
npm run test:ui  # With UI
```

---

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

---

## 🏗️ Project Structure
```text
inventory-saas/
├── backend/
│   ├── apps/
│   │   ├── authentication/     # User auth & JWT
│   │   ├── organizations/      # Organizations & RBAC
│   │   └── core/              # Base models & utilities
│   ├── config/                # Django settings
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── stores/           # Zustand stores
│   │   └── lib/              # API client
│   └── package.json
├── docker/                    # Docker configs
├── docker-compose.yml
└── README.md
```

---

## 🔐 Default Roles
- **Owner** - Full access including org deletion
- **Admin** - Manage users, settings, all resources
- **Manager** - Approve invoices, manage inventory
- **Accountant** - Manage invoices, payments, reports
- **Staff** - Create invoices, update inventory
- **Viewer** - Read-only access

---

## 🎯 Usage Guide

1. **Register & Login**
    - Visit http://localhost:3000/register
    - Create an account
    - Check email for verification link (check console in dev mode)
    - Login at http://localhost:3000/login

2. **Create Organization**
    - After login, you'll see the organizations page
    - Click "Create New Organization"
    - Enter organization name and description
    - You'll be automatically assigned as the Owner

3. **Invite Team Members**
    - Go to organization settings
    - Click "Invite Member"
    - Enter email and select role
    - They'll receive an invitation email

4. **Switch Organizations**
    - Click "Switch Org" button in the header
    - Select from your organizations
    - Context automatically switches

---

## 🔧 Environment Variables

| Variable           | Description            | Default                |
|--------------------|-----------------------|------------------------|
| DJANGO_SECRET_KEY  | Django secret key     | -                      |
| JWT_SECRET_KEY     | JWT signing key       | -                      |
| POSTGRES_DB        | Database name         | inventory_saas         |
| POSTGRES_USER      | Database user         | postgres               |
| POSTGRES_PASSWORD  | Database password     | -                      |
| POSTGRES_HOST      | Database host         | postgres               |
| REDIS_HOST         | Redis host            | redis                  |
| FRONTEND_URL       | Frontend URL          | http://localhost:3000  |

---

## 📝 Next Steps (Sprint 2)
- Products management
- Inventory tracking
- Invoice creation & management
- Payment tracking
- Reports & analytics

---

## 🐛 Troubleshooting

**Database connection error**
- Ensure PostgreSQL is running
- Check credentials in `.env` file
- Run migrations: `python manage.py migrate`

**Redis connection error**
- Ensure Redis is running
- Check `REDIS_HOST` in `.env`

**JWT token errors**
- Clear `localStorage` in browser
- Login again

**CORS errors**
- Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Restart backend server

---

## 📄 License
MIT License - see LICENSE file for details

---

## 👥 Contributors
- Sai Sampath Ayalasomayajula - Initial work

---

## 🙏 Acknowledgments
- Django REST Framework
- React & Vite
- Tailwind CSS
- Zustand

---

## 🧩 Notes

Celery-related functionality and authentication route integrations have been skipped for now and will be added in future sprints.