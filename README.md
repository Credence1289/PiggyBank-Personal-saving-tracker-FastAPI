# 🐷 PiggyBank API

A personal savings goal tracker API built with FastAPI and PostgreSQL. Supports JWT authentication, multiple piggybank vaults with password protection, and full deposit/withdrawal transaction history.

---

## 🚀 Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — Database
- **SQLAlchemy** — ORM
- **Pydantic** — Data validation
- **Jose (JWT)** — Authentication
- **Bcrypt** — Password hashing
- **Python-dotenv** — Environment config

---

## 📁 Project Structure

```
FastAPI_PB#2/
├── .gitignore
├── requirements.txt
└── PiggyBank/
    ├── __init__.py
    └── backend/
        ├── __init__.py
        ├── main.py
        ├── .env
        ├── auth/
        │   ├── __init__.py
        │   ├── gate.py        # JWT middleware / current_user dependency
        │   ├── security.py    # bcrypt hash & verify
        │   └── token.py       # JWT encode & decode
        └── db/
            ├── __init__.py
            ├── db_models.py   # SQLAlchemy models
            ├── dbengine.py    # DB engine setup
            ├── models.py      # Pydantic schemas
            ├── session.py     # DB session
            └── create_table.py
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YourUsername/piggybank-api.git
cd piggybank-api
```

### 2. Create and activate virtual environment

```bash
python -m venv myenv

# Windows
myenv\Scripts\activate

# Mac/Linux
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Inside `PiggyBank/backend/` create a `.env` file:

```env
SECRET_KEY=your_secret_key_here
DB_URL=postgresql://username:password@localhost:5432/piggybank
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

### 5. Create the database tables

```bash
cd PiggyBank/backend
python -m db.create_table
```

### 6. Run the server

```bash
# Always run from the project root
cd FastAPI_PB#2

uvicorn PiggyBank.backend.main:app --reload
```

Server runs at `http://127.0.0.1:8000`

---

## 📖 API Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users` | Register new user | ❌ |
| POST | `/user/login` | Login and get JWT token | ❌ |
| DELETE | `/users` | Delete account | ✅ |

### PiggyBanks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/piggybank` | Create new savings goal | ✅ |
| GET | `/users/piggybank` | List all your piggybanks | ✅ |
| GET | `/users/piggybank/{id}` | Get a single piggybank | ✅ |
| DELETE | `/users/piggybank/{id}` | Delete a piggybank | ✅ |

### Transactions

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/piggybank/{id}/deposit` | Deposit into a piggybank | ✅ |
| POST | `/users/piggybank/{id}/withdraw` | Withdraw from a piggybank | ✅ |
| GET | `/users/piggybank/{id}/transaction` | View transaction history | ✅ |

---

## 🔐 Authentication

This API uses **JWT Bearer tokens**.

1. Register at `POST /users`
2. Login at `POST /user/login` — returns an `access_token`
3. Pass the token in the `Authorization` header for all protected routes:

```
Authorization: Bearer <your_token>
```

Tokens expire after **30 minutes**.

---

## 📦 Request Examples

### Register
```json
POST /users
{
  "name": "Vinayak",
  "mobile_no": "9876543210",
  "email": "vinayak@gmail.com",
  "password": "securepassword"
}
```

### Login
```
POST /user/login
Content-Type: application/x-www-form-urlencoded

username=vinayak@gmail.com&password=securepassword
```

### Create PiggyBank
```json
POST /users/piggybank
Authorization: Bearer <token>
{
  "name": "New Laptop",
  "target_amount": 80000,
  "passwordpb": "vaultpassword"
}
```

### Deposit
```
POST /users/piggybank/1/deposit?amount=5000
Authorization: Bearer <token>
```

---

## 🗃️ Database Models

### User
| Column | Type | Notes |
|--------|------|-------|
| user_id | Integer | Primary key |
| name | String | |
| mobile_no | String | Unique |
| email | String | Unique |
| hashed_password | String | bcrypt |

### PiggyBank
| Column | Type | Notes |
|--------|------|-------|
| piggybank_id | Integer | Primary key |
| user_id | Integer | FK → users |
| name | String | Goal name |
| target_amount | Float | Savings target |
| balance | Float | Current balance |
| hashed_passwordpb | String | Vault password (bcrypt) |
| is_target_active | Boolean | Default true |

### Transaction
| Column | Type | Notes |
|--------|------|-------|
| transaction_id | Integer | Primary key |
| piggybank_id | Integer | FK → piggybank |
| type | String | "Deposit" or "Withdraw" |
| amount | Float | |
| time_stamp | DateTime | Auto set |

---

## 📋 Requirements

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic[email]
python-jose[cryptography]
bcrypt
python-dotenv
python-multipart
```

---

## 🌐 Interactive Docs

FastAPI auto-generates interactive documentation:

- **Swagger UI** → `http://127.0.0.1:8000/docs`
- **ReDoc** → `http://127.0.0.1:8000/redoc`

---

## 👤 Author

**Vinayak** — [github.com/YourUsername](https://github.com/Credence1289)
