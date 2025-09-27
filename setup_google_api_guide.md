# Google Places API Setup Guide

## Overview
To get better healthcare organization search suggestions in the QuXAT Scoring system, you can configure Google Places API integration. This will provide real-time suggestions from Google Maps when users search for healthcare organizations.

## Step-by-Step Setup

### 1. Get Google Places API Key

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create or Select a Project**
   - Create a new project or select an existing one
   - Note down your project ID

3. **Enable Places API**
   - Go to "APIs & Services" > "Library"
   - Search for "Places API"
   - Click on "Places API" and click "Enable"

4. **Create API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key

5. **Restrict API Key (Recommended)**
   - Click on your API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Choose "Places API" from the list
   - Save the changes

### 2. Configure the Application

1. **Update .env File**
   - Open the `.env` file in the project root directory
   - Replace the empty `GOOGLE_PLACES_API_KEY=` with your actual API key:
   ```
   GOOGLE_PLACES_API_KEY=your_actual_api_key_here
   ```

2. **Restart the Application**
   - Stop the Streamlit application if it's running
   - Start it again to load the new environment variable

### 3. Verify Setup

1. **Test Search Functionality**
   - Go to the organization search page
   - Type a healthcare organization name (e.g., "Apollo Hospital")
   - You should see suggestions from Google Places in addition to database matches

2. **Check for Errors**
   - If you see "External search temporarily unavailable" messages, check:
     - API key is correctly set in .env file
     - Places API is enabled in Google Cloud Console
     - API key has proper permissions

## Features Enabled

With Google Places API configured, you get:

- **Real-time Suggestions**: Live suggestions from Google Maps
- **Enhanced Coverage**: Organizations not in your database
- **Location Information**: Addresses and ratings from Google
- **Better Matching**: More accurate healthcare organization identification

## Cost Information

- Google Places API has a free tier with generous limits
- Text Search requests: $32 per 1,000 requests (after free tier)
- Free tier: $200 credit monthly (covers ~6,250 requests)
- For typical usage, this should be sufficient

## Troubleshooting

### Common Issues

1. **"API key not configured" message**
   - Ensure .env file has the correct API key
   - Restart the application after updating .env

2. **"ZERO_RESULTS" or no suggestions**
   - API key might not have Places API enabled
   - Check API restrictions in Google Cloud Console

3. **"Request denied" errors**
   - API key might be restricted to specific domains/IPs
   - Check API key restrictions in Google Cloud Console

### Testing Without API Key

If you don't want to set up Google Places API, the system will still work with:
- Smart fallback suggestions based on common healthcare naming patterns
- Database-based suggestions from existing organizations
- Generated suggestions with common healthcare suffixes

## Security Notes

- Never commit your API key to version control
- Use API key restrictions to limit usage
- Monitor API usage in Google Cloud Console
- Consider using environment-specific API keys for development/production

## Support

If you encounter issues:
1. Check the console logs for specific error messages
2. Verify API key permissions in Google Cloud Console
3. Test the API key using Google's API Explorer
4. Ensure billing is enabled if you exceed free tier limits