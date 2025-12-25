# CarPlace API 🚗

CarPlace is a comprehensive marketplace for new and used cars, featuring AI-powered specialized assistants, auctions, messaging, and a robust administrative system.

## 🏗️ System Architecture

The application is built using a modern **FastAPI** backend with a **PostgreSQL** database managed by **SQLAlchemy**.

```mermaid
graph TD
    User((User))
    API[FastAPI Backend]
    DB[(PostgreSQL)]
    Gemini[Gemini 1.5 Flash]
    Embedding[sentence-transformers]
    FAISS[FAISS Vector Index]
    PDF[Technical Catalogs]

    User -- HTTP/REST --> API
    API -- ORM --> DB
    API -- RAG --> Gemini
    API -- Embeddings --> Embedding
    Embedding -- Search --> FAISS
    FAISS -- Context --> PDF
    Gemini -- AI Response --> API
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL database

### 2. Installation
Clone the repository and set up a virtual environment:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (one has been created for you, but make sure to add your API key):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Running the App
```powershell
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
Documentation is interactive via Swagger UI at `http://127.0.0.1:8000/docs`.

---

## 📡 API Endpoints & Testing

### 🔐 Authentication
- **POST `/auth/register`**: Register a new user (`admin`, `seller`, or `dealer`).
- **POST `/auth/login`**: Get a JWT access token. Use the `Authorize` button in Swagger UI to test protected endpoints.

### 🤖 AI Features (The "Wow" Factors)
- **POST `/chat`**: Secure AI Chat Assistant.
    - **Context**: Grounded in car listing data and conversation history.
    - **Prompt Control**: Strict system instructions to prevent off-topic discussions.
- **GET `/compare`**: AI Car Comparison.
    - **RAG**: Uses FAISS to search technical catalogs for factual data.
    - **Hallucination Prevention**: Strictly grounded in PDF context.

### 🚗 Car Listings
- **GET/POST `/used_cars`**: Manage used car listings.
- **GET/POST `/new_cars`**: Manage new car versions (Dealer specific).
- **GET `/public_models`**: Browse available brands and models.

### 🔨 Auctions
- **POST `/auction`**: Create auctions for cars.
- **POST `/auction/{auction_id}/bid`**: Place bids in real-time.

### 💬 Messaging
- **GET/POST `/conversations`**: Human-to-human communication between buyers and sellers.
- **GET `/chat/conversations`**: List AI chat history.

### 🛠️ Admin Management
- **GET `/admin/stats`**: High-level marketplace overview.
- **POST `/admin/brands`**: Manage manufacturers.
- **DELETE `/admin/users/{id}`**: Moderate users.

---

## 🧪 Testing with cURL

**Login Example:**
```bash
curl -X 'POST' 'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=yourpassword'
```

**AI Comparison Example:**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/compare/?car1_id=1&car2_id=2' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

---

## 🛠️ Technologies
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **AI**: Gemini 1.5 Flash (via REST)
- **Vector Search**: FAISS + Sentence Transformers (RAG)
- **Security**: JWT (Jose) + Passlib (Bcrypt)
- **Data parsing**: PDFPlumber
