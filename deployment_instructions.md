# Deployment Instructions for Travel Rewards App

## Issue: Missing Blog Reviews on Production

The blog review system is fully implemented in the codebase, but the reviews are not appearing on the production site because the database on Render doesn't contain the review data that exists in your local development environment.

## Deployment Options

### Option 1: Update Render Deployment Settings (Recommended)

1. Log in to your Render dashboard
2. Go to your Web Service for the Travel Rewards App
3. Go to the "Environment" tab
4. Add the following environment variable:
   - Key: `DEPLOY_REVIEWS`
   - Value: `true`
5. Go to the "Settings" tab 
6. Under "Build Command", update it to include running the deployment script:
   ```
   pip install -r requirements.txt && chmod +x deploy_to_render.sh && ./deploy_to_render.sh
   ```
7. Click "Save Changes"
8. Trigger a manual deploy by clicking "Manual Deploy" > "Deploy latest commit"

### Option 2: Connect to Render Database Directly (Alternative)

If Option 1 doesn't work, you can connect directly to the Render database:

1. Log in to your Render dashboard
2. Go to your PostgreSQL database
3. Click on "Connect" to view connection details
4. Use a PostgreSQL client (like pgAdmin or DBeaver) to connect to your database
5. Create a new SQL query and paste the contents of `reviews_for_production.sql`
6. Execute the query

### Option 3: Use the Render Shell (Simplest)

1. Log in to your Render dashboard
2. Go to your PostgreSQL database
3. Click on "Shell" tab
4. Copy and paste the contents of `reviews_for_production.sql` into the shell
5. Press Enter to execute the SQL commands

## Verifying the Deployment

After deploying, verify that the reviews are visible:

1. Visit https://goaskmarshall.com/travel-guides
2. Scroll down to see if the "Our Reviews" section shows the reviews
3. Check the API endpoint directly: https://goaskmarshall.com/api/reviews

## Troubleshooting

If reviews are still not showing up:

1. Check the Render logs for any errors during deployment
2. Verify the database connection is correctly configured
3. Check if the `reviews` table was created in the database
4. Verify that the reviews are marked as published (`is_published = true`)

## Maintenance

The scripts provided in this repository will help you manage reviews:

- `manage_reviews.py` - Interactive tool to add, edit, delete reviews
- `upload_reviews_to_render.py` - Export reviews from your local database to SQL
- `migrations/deploy_reviews.py` - Deploy reviews programmatically during deployment
- `deploy_to_render.sh` - Deployment script for Render

When adding new reviews in the future, develop them locally first, then use these scripts to deploy them to production.
