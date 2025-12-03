# Module 0: Pre-Course Setup & FastAPI Smoke Test

This is your first FastAPI application! It's a simple smoke test to confirm your environment is set up correctly.

## What This Code Does

- Creates a minimal FastAPI application
- Sets up a SQLite database connection (file-based, no server needed)
- Provides a `/health` endpoint that checks if the database works
- Provides a `/` root endpoint with a welcome message
- Auto-generates interactive API documentation at `/docs`

## How to Run

### Step 1: Activate Virtual Environment

If you haven't already activated your virtual environment:

**Mac/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` appear at the start of your command prompt.

### Step 2: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - The web framework
- `uvicorn` - The server that runs FastAPI
- `sqlalchemy` - Database toolkit

### Step 3: Run the FastAPI Server

Start the development server with auto-reload:

```bash
uvicorn main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Test the API

Open your web browser and visit these URLs:

1. **Health Check:** http://localhost:8000/health
   - Should show: `{"status":"healthy","message":"OpenCafe API is ready!","database":"connected"}`

2. **Welcome Page:** http://localhost:8000/
   - Should show welcome message with links to documentation

3. **Interactive Docs:** http://localhost:8000/docs
   - Shows auto-generated API documentation
   - You can test endpoints directly from this page!

## Stopping the Server

Press `Ctrl+C` in the terminal where uvicorn is running.

## What You'll See

### Terminal Output
When you run the server, uvicorn shows:
- Server address (usually http://127.0.0.1:8000)
- Auto-reload status (watches for code changes)
- Startup confirmation

### Browser Output
- `/health` returns JSON showing API status and database connection
- `/` returns a welcome message
- `/docs` shows interactive Swagger UI documentation

### File System
- A new file `test.db` appears in the `code/` directory
- This is your SQLite database file (automatically created)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Activate virtual environment and run `pip install -r requirements.txt` |
| `Address already in use` or `Port 8000 is in use` | Another server is using port 8000. Try `uvicorn main:app --reload --port 8001` |
| `Permission denied` when creating test.db | Check folder permissions. Try running from a different directory. |
| Server won't start | Check Python version with `python --version` (need 3.9+) |

## What's Next?

After confirming everything works:
1. Try modifying the `/health` endpoint to return additional information
2. Add a new endpoint (practice exercise in the lesson)
3. Explore the auto-generated documentation at `/docs`
4. Move on to Module 1 to learn Clean Architecture patterns

## Files in This Directory

- `main.py` - The FastAPI application code
- `requirements.txt` - Python package dependencies
- `README.md` - This file (run instructions)
- `.gitignore` - Files to exclude from version control
- `test.db` - SQLite database (auto-created when you run the app)
