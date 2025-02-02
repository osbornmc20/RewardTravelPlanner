# Trip Planner Web App

A Flask-based web application for planning trips using points and miles.

## Features
- Trip planning with multiple destinations
- Points program management
- Support for both authenticated and anonymous users
- Airport search with autocomplete
- OpenAI integration for intelligent travel suggestions

## Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_api_key
   OPENAI_ORG_ID=your_org_id
   FLASK_SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///database.db
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Deployment Instructions

### Option 1: Deploy to Render (Recommended)

1. Create a Render account at https://render.com
2. Connect your GitHub repository
3. Create a new Web Service
4. Select your repository
5. Configure the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variables from `.env`

### Option 2: Deploy to Railway

1. Create a Railway account at https://railway.app
2. Connect your GitHub repository
3. Create a new project
4. Add environment variables from `.env`
5. Deploy!

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_ORG_ID`: Your OpenAI organization ID
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URL`: Database connection URL
- `FLASK_DEBUG`: Set to 'True' for development, 'False' for production

## Database
The application uses SQLAlchemy with SQLite by default. For production, consider using PostgreSQL.
