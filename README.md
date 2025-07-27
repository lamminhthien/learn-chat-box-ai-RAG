# Chatbox AI - Project Setup Guide

## Requirements
- Python 3.x
- PostgreSQL (if using this database)
- (Optional) Node.js if using React

## Using Free Online Databases if don't want to use Docker
- **Database Postgres**: https://neon.com/
- **VectorDB**: https://qdrant.tech/


## 1. Install Backend
```sh
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Initialize PostgreSQL Database
- Create database and user using pgAdmin or psql:
```sql
CREATE DATABASE chatbox_ai;
CREATE USER chatbox_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE chatbox_ai TO chatbox_user;
```
- Update connection details in `backend/database.py` if needed.

## 3. Run Backend
```sh
cd backend
docker-compose up -d vectordb
docker-compose up -d postgres

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 4. Run Frontend
### Option 1: Open Directly
- Open `frontend/index.html` in a browser.

### Option 2: Use Live Server (VS Code)
- Install the Live Server extension.
- Right-click `index.html` → Open with Live Server.

### Option 3: Use Python HTTP Server
```sh
cd frontend
python -m http.server 8080
```
- Access: http://localhost:8080
- Currently API upload file have issue CORS temporary, we must use extension `Allow CORS: Access-Control-Allow-Origin` to test and work in local