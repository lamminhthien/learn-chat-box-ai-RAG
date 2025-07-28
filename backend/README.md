# Chatbox AI Backend

## Using Free Online Databases if don't want to use Docker
- **Database Postgres**: https://neon.com/
- **VectorDB**: https://qdrant.tech/

## Setup

# Prepare Google Gemini API Key
https://ai.google.dev/gemini-api/docs/api-key


# Install vectordb (qdrant) and database (postgres)
```bash
docker-compose up -d vectordb
docker-compose up -d postgres
```

# Install library psycopg2
## Installation Instructions for psycopg2

### Windows
1. **Install PostgreSQL** (if not installed):
   - Download and install from [postgresql.org](https://www.postgresql.org/download/windows/).
   - Note the installation path for later use.

2. **Install psycopg2**:
   - Open Command Prompt and run:
     ```bash
     pip install psycopg2-binary
     ```
   - If issues arise, install Microsoft Visual C++ Build Tools from [visualstudio.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and retry with:
     ```bash
     pip install psycopg2
     ```

3. **Verify Installation**:
   - Open Python shell and test:
     ```python
     import psycopg2
     print(psycopg2.__version__)
     ```

---

### Mac
1. **Install Homebrew** (if not installed):
   - Open Terminal and run:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

2. **Install PostgreSQL** (if not installed):
   - Run:
     ```bash
     brew install postgresql
     ```

3. **Install psycopg2**:
   - Use pip to install:
     ```bash
     pip install psycopg2-binary
     ```
   - Or, with PostgreSQL development headers:
     ```bash
     brew install postgresql
     pip install psycopg2
     ```

4. **Verify Installation**:
   - Run a Python shell and test:
     ```python
     import psycopg2
     print(psycopg2.__version__)
     ```

---

### Linux
1. **Install PostgreSQL and Development Libraries**:
   - For Debian/Ubuntu:
     ```bash
     sudo apt install postgresql postgresql-contrib libpq-dev
     ```
   - For CentOS/RHEL:
     ```bash
     sudo yum install postgresql-server postgresql-contrib libpq-devel
     ```

2. **Install psycopg2**:
   - Run:
     ```bash
     pip install psycopg2-binary
     ```
   - Or, with system libraries:
     ```bash
     pip install psycopg2
     ```

3. **Verify Installation**:
   - Open Python shell and test:
     ```python
     import psycopg2
     print(psycopg2.__version__)
     ```

# Install and run backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Start Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Main Endpoints

- `GET /notes` - Retrieve list of notes
- `POST /notes` - Add a note
- `PUT /notes/{id}` - Update a note
- `DELETE /notes/{id}` - Delete a note

- `GET /events` - Retrieve list of appointments
- `POST /events` - Add an appointment
- `PUT /events/{id}` - Update an appointment
- `DELETE /events/{id}` - Delete an appointment

- `POST /ask` - Chatbot responds based on NLP
- `GET /reminders` - Retrieve upcoming events for reminders (for frontend polling)

## Notes
- **Scheduler**: APScheduler (logs to console when reminder time is reached)
- **NLP**: Regex + dateparser (can be upgraded later)