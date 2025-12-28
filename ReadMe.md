# CarPlace API 🚗

CarPlace is a comprehensive automotive marketplace. It handles new and used car listings, auctions, real-time messaging, and features a state-of-the-art AI assistant grounded in technical catalogs.

## 🏗️ Project Architecture

```text
CarPlace/
├── main.py                 # App entry point & router registration
├── models.py               # Database models (SQLAlchemy)
├── schemas.py              # Data validation (Pydantic)
├── database.py             # DB connection & session management
├── .env                    # Secrets & Configuration (ignored by git)
├── routers/                # API Modules
│   ├── admin.py            # Global stats, Brand/Model/User moderation
│   ├── auction.py          # Real-time bidding system (WebSockets)
│   ├── auth.py             # JWT Authentication & Registration
│   ├── brands.py           # Catalog: Brand listing & metadata
│   ├── chat.py             # Secure AI Assistant (Gemini 1.5 Flash)
│   ├── compare.py          # AI-powered Car Comparison (RAG)
│   ├── conversations.py    # P2P Messaging (Buyer <-> Seller)
│   ├── dealers.py          # Dealer profiles & showroom listings
│   ├── new_cars.py         # Manufacturer technical versions
│   ├── public_models.py    # Public model specifications
│   ├── used_cars.py        # Marketplace used car listings
│   └── vin_decoder.py      # VIN Analysis & OCR Scanner
├── services/               # Core business logic
│   └── AIComparision.py    # RAG pipeline (FAISS + PDF processing)
└── requirements.txt        # Project dependencies
```

---

## 🚀 Getting Started

### 1. Installation
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
Update your `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Execution
```powershell
uvicorn main:app --reload
```
Interactive docs: `http://127.0.0.1:8000/docs`

---

## 📡 Exhaustive Endpoint List

### 🔐 Authentication (`/auth`)
- `POST /auth/register` - Create new user account.
- `POST /auth/login` - Authenticate and receive JWT.

### 🤖 AI Services
- `POST /chat` - Grounded AI Chat (Listing context + User history).
- `GET /chat/conversations` - Retrieve your AI chat history.
- `GET /compare/` - Fact-based comparison of two cars via technical PDF RAG.

### 🔨 Auction System (`/auction`)
- `POST /auction/create` - (Dealer Only) List a version for auction.
- `POST /auction/start/{id}` - (Dealer Only) Open an auction for bidding.
- `WS /auction/bid/{id}` - (Seller Only) Real-time bidding via WebSockets.
- `GET /auction/status/{id}` - Monitor highest bid and time remaining.
- `POST /auction/end/{id}` - (Dealer Only) Close auction and declare winner.

### 💬 Messaging (`/conversations`)
- `GET /conversations` - List active P2P chats.
- `POST /conversations` - Start chat about a listing.
- `GET /conversations/{id}` - Get chat details and messages.
- `POST /conversations/messages` - Send a new message.
- `POST /conversations/messages/{id}/read` - Mark message as read.
- `WS /conversations/ws/{id}` - Real-time chat WebSocket tunnel.

### 🚗 used cars (`/cars/used`)
- `GET /cars/used` - Search & filter marketplace listings.
- `POST /cars/used` - (Seller Only) Create a new listing.
- `GET /cars/used/{id}` - Detailed car specs and seller info.
- `PUT /cars/used/{id}` - Update your listing.
- `DELETE /cars/used/{id}` - Remove your listing.
- `GET /cars/used/mine` - View your own active listings.
- `GET /cars/used/stats/mine` - Personal sales performance.

### 🏢 New Cars & Versions (`/cars/new`)
- `GET /cars/new` - Browse professional technical versions.
- `POST /cars/new` - (Dealer Only) Add new car technical specs.
- `GET /cars/new/{id}` - Detailed technical version info.
- `PUT /cars/new/{id}` - Update version data.
- `DELETE /cars/new/{id}` - Reclaim version.
- `GET /cars/new/mine` - Dealer showroom inventory.
- `GET /cars/new/stats/mine` - Dealer inventory analytics.

### � Discovery & Reference
- `GET /brands` - List all automotive brands.
- `GET /brands/{id}` - Get brand details and stats.
- `GET /brands/{id}/models` - List models by brand.
- `GET /models` - List all models across all brands.
- `GET /models/search/` - Search models by name.
- `GET /vin/{vin}` - Decode VIN to identify year and model.
- `POST /vin/scan` - OCR Scanner: Extract and decode VIN from image.

### 🏙️ Dealers (`/dealers`)
- `GET /dealers` - Directory of active dealers. (Optional: `?include_meta=true`).
- `GET /dealers/{id}` - Dealer profile summary.
- `GET /dealers/{id}/cars` - Official dealer inventory.
- `GET /dealers/search/` - Search dealers by name or contact.
- `GET /dealers/{id}/meta` - Additional dealer metadata (Location, Contact).
- `PUT /dealers/me/meta` - (Dealer Only) Manage your own showroom metadata.

### 🛠️ Administration (`/admin`)
*(Required Admin Role)*
- `GET /admin/stats` - Global marketplace metrics.
- `GET /admin/dealers/{id}/stats` - Monitor specific dealer performance.
- `GET /admin/sellers/{id}/stats` - Monitor specific seller activity.
- `POST /admin/brands` - Add new global brand.
- `DELETE /admin/brands/{id}` - Remove brand and relations.
- `POST /admin/categories` - Manage car categories.
- `DELETE /admin/users/{id}` - Moderate/Ban user accounts.

---

## 🛠️ Tech Stack
- **FastAPI**: Modern, high-performance web framework.
- **Gemini 1.5 Flash**: Multi-modal generative AI.
- **FAISS**: High-speed vector search for RAG.
- **SQLAlchemy**: Powerful ORM for PostgreSQL.
- **WebSockets**: Real-time bidding and chat synchronization.
- **Pytesseract**: OCR for VIN scanning.
