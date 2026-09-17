# Training Tracker

A web app for a part-time personal training business. Clients log their daily food intake and bodyweight over time; the trainer logs in with a separate admin role, reviews each client's data, and assigns workout splits.

**Live app:** https://trainer-app-hekm.onrender.com

Built from scratch as a learning project — my first time writing Flask, using Postgres, and deploying a full web app. I wrote the application logic, the templates, and the database design myself. (The CSS is the one part I chose not to focus on.)

## What it does

**For clients:**
- Register and log in
- Log meals (type, quantity, food) and bodyweight
- View their own history and assigned workout split

**For the trainer (admin):**
- Separate role with its own access
- View any client's food log, weight log, and profile
- Assign workout splits to individual clients

## Tech stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL (started on SQLite, migrated to Postgres for persistence)
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Auth:** session-based login with role-based access control
- **Hosting:** Render (app + managed Postgres)

## Running it locally

**1. Clone the repo**
```bash
git clone https://github.com/sullvs/trainer-app.git
cd trainer-app
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv trainer
source trainer/bin/activate      # macOS/Linux
# trainer\Scripts\activate       # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your environment**

Create a `.env` file in the project root with your database connection and secret key string:
```
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
```
The app reads this via `python-dotenv`. You'll need a running Postgres database (local or a cloud provider like Render).

**5. Initialise the database**

The schema is defined in schema.sql. It runs automatically on startup via init_db(), which creates the tables if they don't already exist — so no manual step is needed. Just make sure your DATABASE_URL points at a reachable Postgres database before you start the app.

**6. Start the app**
```bash
python app.py
```
The app runs at `http://127.0.0.1:5000`.

## Project structure

```
trainer-app/
├── app.py               # All routes, DB helpers, and app logic
├── schema.sql           # Database schema (tables)
├── templates/           # Jinja2 HTML templates
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── client_dash.html
│   ├── trainer_dash.html
│   ├── one_client.html
│   └── assign.html
├── static/
│   └── style.css        # Dark theme styling
├── requirements.txt
├── create_trainer.py    # Script to create a trainer/admin account
├── reset_trainer.py     # Script to reset a trainer's password
├── README.md            # Project's summary
└── .env                 # Not committed — holds DATABASE_URL and SECRET_KEY
```

## Notes

- Trainer accounts are created via the create_trainer.py script rather than the public register form (which only creates client accounts).
- `.env` and any local database files are git-ignored.

## Feedback welcome

The repo is public — clone it, open an issue, or suggest a feature. If you're into building things, I'd love to connect.
