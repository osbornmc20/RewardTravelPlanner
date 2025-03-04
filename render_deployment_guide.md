# Render Deployment Guide for Blog Reviews

## Step 1: Log in to Render Dashboard
1. Go to [render.com](https://render.com/) and log in to your account
2. Find your Travel Rewards App Web Service in the dashboard

## Step 2: Update Environment Variables
1. Click on your Web Service
2. Navigate to the "Environment" tab
3. Click "Add Environment Variable"
4. Add the following:
   - **Key**: `DEPLOY_REVIEWS`
   - **Value**: `true`
5. Click "Save Changes"

![Environment Variables Example](https://i.imgur.com/1uXJ3g0.png)

## Step 3: Update Build Command
1. Still in your Web Service settings, go to the "Settings" tab
2. Scroll down to find "Build Command"
3. Update it to:
   ```
   pip install -r requirements.txt && chmod +x deploy_to_render.sh && ./deploy_to_render.sh
   ```
4. Click "Save Changes"

![Build Command Example](https://i.imgur.com/ZUoEGlN.png)

## Step 4: Deploy Manually
1. Click on the "Manual Deploy" button at the top right
2. Select "Deploy latest commit"
3. Wait for the deployment to complete

![Manual Deploy Example](https://i.imgur.com/VDC9Eiy.png)

## Step 5: Monitor Deployment
1. Click on the "Logs" tab
2. Watch for the following messages in the logs:
   - "Starting deployment process..."
   - "Creating database tables..."
   - "Adding sample reviews to the database"
   - "Deployment complete!"

## Step 6: Verify Success
1. After deployment completes, visit your website:
   - Main site: [https://goaskmarshall.com/travel-guides](https://goaskmarshall.com/travel-guides)
   - API endpoint: [https://goaskmarshall.com/api/reviews](https://goaskmarshall.com/api/reviews)
2. You should now see the "Our Reviews" section populated with your blog reviews

## Troubleshooting
If you encounter any issues:

1. **Reviews not appearing**:
   - Check the Render logs for any error messages
   - Try hitting the API endpoint directly to see what's returned
   - Verify your database connection is correct

2. **Build errors**:
   - Make sure the `deploy_to_render.sh` script is executable (we set this with chmod +x)
   - Check that `requirements.txt` includes all necessary dependencies
   - Verify the Python version on Render matches your development environment

3. **Database issues**:
   - You may need to manually connect to the database and check if the reviews table exists
   - Verify the table schema matches what's expected by the application

4. **Additional help**:
   - If you encounter persistent issues, consider using Option 2 or 3 from the deployment instructions
