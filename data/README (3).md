# EduCast - MVP v0

A mobile-first real-time academic support marketplace where students post doubts as bounties, mentors bid competitively, and sessions are conducted in real-time.

## 🎯 Overview

EduCast flips the traditional e-learning model from **supply-driven** to **demand-driven**:
- Students post academic problems as bounties with budgets
- Mentors see bounties in real-time and place competitive bids
- Students accept the best bid and start a session
- After completion, students rate mentors

## 🏗️ Architecture

### Backend
- **Language:** Go (Golang)
- **Framework:** Gin
- **Database:** MySQL
- **Real-time:** WebSocket (Gorilla)
- **Authentication:** JWT

### Frontend
- **Framework:** React Native (Expo)
- **Navigation:** React Navigation
- **State:** Context API
- **HTTP Client:** Axios
- **Storage:** AsyncStorage

## 📋 Prerequisites

### Backend
- Go 1.21 or higher
- MySQL 8.0 or higher

### Frontend
- Node.js 18+ or 20+
- npm or yarn
- Expo CLI (installed automatically)

## 🚀 Setup Instructions

### 1. Database Setup

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE educast;

# Run migration
mysql -u root -p educast < backend/migrations/001_initial_schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
go mod download

# Copy environment file
cp .env.example .env

# Edit .env with your MySQL credentials
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=educast

# Run the server
go run main.go
```

The backend server will start on `http://localhost:8080`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Expo
npm start
```

This will open Expo Dev Tools. You can:
- Press `w` to open in web browser
- Scan QR code with Expo Go app (iOS/Android)
- Press `a` for Android emulator
- Press `i` for iOS simulator (macOS only)

## 📱 Usage Guide

### Student Flow

1. **Sign Up** as Student
2. **Post a Bounty**
   - Enter title, description, subject tag, and budget
   - Bounty appears instantly in mentor feeds via WebSocket
3. **View Bids**
   - Mentors place bids on your bounty
   - Bids appear in real-time
4. **Accept a Bid**
   - Review bids and accept the best one
   - System creates escrow transaction
   - Session room is generated
5. **Complete Bounty**
   - Mark bounty as complete
   - Rate the mentor (1-5 stars)
   - System releases payment transaction

### Mentor Flow

1. **Sign Up** as Mentor
2. **Browse Live Feed**
   - See all open bounties in real-time
   - New bounties appear instantly via WebSocket
3. **Place a Bid**
   - View bounty details
   - Submit your bid with price and note
4. **Get Notified**
   - Receive real-time notification when bid is accepted
   - Join session room automatically
5. **Complete Session**
   - Help student solve their problem
   - Receive payment and rating

## 🔌 API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login

### Bounties
- `POST /api/bounties` - Create bounty (Student only)
- `GET /api/bounties` - List bounties (filtered by role)
- `GET /api/bounties/:id` - Get bounty details
- `POST /api/bounties/:id/complete` - Complete bounty (Student only)

### Bids
- `POST /api/bounties/:id/bids` - Place bid (Mentor only)
- `GET /api/bounties/:id/bids` - Get bids for bounty (Student only)
- `POST /api/bids/:id/accept` - Accept bid (Student only)

### WebSocket
- `GET /ws?token=JWT` - WebSocket connection

## 🔄 WebSocket Events

### Server → Client

**bounty_created**
```json
{
  "type": "bounty_created",
  "payload": { "bounty": {...} }
}
```

**bid_created**
```json
{
  "type": "bid_created",
  "payload": { "bid": {...} }
}
```

**bid_accepted**
```json
{
  "type": "bid_accepted",
  "payload": {
    "bid_id": 12,
    "bounty_id": 55,
    "room_id": "uuid"
  }
}
```

## 🗄️ Database Schema

### users
- id, name, email, password_hash, role (Student/Mentor), rating_avg

### bounties
- id, student_id, title, description, subject_tag, budget, status (OPEN/IN_PROGRESS/CLOSED), room_id

### bids
- id, bounty_id, mentor_id, price_offer, note, is_accepted

### transactions
- id, bounty_id, amount, type (ESCROW/RELEASE/REFUND)

## 🎨 Features Implemented

✅ JWT Authentication
✅ Role-based access control
✅ Real-time bounty feed (WebSocket)
✅ Real-time bid notifications
✅ Atomic bid acceptance (with database locking)
✅ Escrow transaction simulation
✅ Session room generation
✅ Mentor rating system
✅ Auto-reconnect WebSocket logic

## 🚧 Prototype Limitations

- **No real payments:** Transactions are simulated in database
- **No video streaming:** Session room is a placeholder (WebRTC integration pending)
- **No push notifications:** Only in-app WebSocket notifications
- **Basic UI:** Functional but not polished

## 🧪 Testing

### Manual Testing

1. **Test Authentication**
```bash
# Signup as student
curl -X POST http://localhost:8080/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"1234","role":"Student"}'

# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"1234"}'
```

2. **Test Bounty Creation**
```bash
curl -X POST http://localhost:8080/api/bounties \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Help with Calculus","description":"Need help solving derivatives","subject_tag":"Math","budget":25.00}'
```

3. **Test WebSocket**
- Open browser console
- Connect to `ws://localhost:8080/ws?token=YOUR_JWT_TOKEN`
- Create a bounty and watch for real-time events

## 📂 Project Structure

```
Bits-Study-Project/
├── backend/
│   ├── config/          # Configuration and database
│   ├── controllers/     # Request handlers
│   ├── middleware/      # Auth and role middleware
│   ├── models/          # Data models
│   ├── websocket/       # WebSocket hub and client
│   ├── migrations/      # Database schema
│   ├── main.go          # Entry point
│   └── .env             # Environment variables
│
└── frontend/
    ├── src/
    │   ├── context/     # Auth and WebSocket contexts
    │   ├── navigation/  # App navigation
    │   ├── screens/     # All screens (auth, student, mentor)
    │   ├── services/    # API clients
    │   └── components/  # Reusable components
    └── App.js           # Root component
```

## 🐛 Troubleshooting

### Backend won't start
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Check `.env` file has correct credentials

### Frontend can't connect to backend
- Ensure backend is running on port 8080
- Update `API_BASE_URL` in `frontend/src/services/config.js` if needed
- For physical device testing, use your computer's IP instead of `localhost`

### WebSocket not connecting
- Check JWT token is valid
- Verify WebSocket URL in `frontend/src/services/config.js`
- Check browser/app console for connection errors

## 🔐 Security Notes

⚠️ **This is a prototype. Do NOT use in production without:**
- Changing JWT secret
- Adding password strength requirements
- Implementing rate limiting
- Adding input sanitization
- Using HTTPS/WSS
- Implementing proper error handling
- Adding request validation

.
