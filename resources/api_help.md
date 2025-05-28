# API Registration Guide for Auralis

## Overview
Auralis enhances your music collection by fetching metadata from online services. This guide explains how to register for API keys and the limitations of each service.

## AcoustID / MusicBrainz

### About the Service
AcoustID is an audio fingerprinting service that can identify songs based on their audio content. It works with MusicBrainz, an open music encyclopedia that collects music metadata.

### Registration Process
1. **Create an AcoustID account**:
   - Visit [AcoustID Login](https://acoustid.org/login)
   - Click "Register" and complete the registration form
   - Verify your email address

2. **Generate an API key**:
   - Log in to your AcoustID account
   - Go to [API Key Management](https://acoustid.org/api-key)
   - Click "New application"
   - Fill in:
     * Application name: "Auralis" (or your preferred name)
     * Version: "1.0"
     * Website: (optional)
     * Description: "Personal music management application"
   - Submit the form to receive your API key

3. **Enter the API key in Auralis**:
   - Open Auralis and go to the Settings tab
   - Find the "AcoustID API Key" field
   - Paste your key and save settings

### Usage Limits
- Free tier: 1 request per second, 3 lookups per request
- Total daily limit: Up to 1,000 lookups per day
- Commercial use requires a paid plan

### Troubleshooting
- **401 Unauthorized**: Check if your API key is correct
- **429 Too Many Requests**: You've exceeded rate limits; wait and try again
- **503 Service Unavailable**: The service is temporarily down; try again later

## Discogs

### About the Service
Discogs is a comprehensive music database and marketplace with extensive information about recordings, artists, and releases.

### Registration Process
1. **Create a Discogs account**:
   - Visit [Discogs Sign Up](https://www.discogs.com/users/create)
   - Complete the registration form
   - Verify your email address

2. **Generate a Personal Access Token**:
   - Log in to your Discogs account
   - Go to [Developer Settings](https://www.discogs.com/settings/developers)
   - Scroll to "Personal Access Tokens"
   - Click "Generate new token"
   - Label it "Auralis" (or your preferred name)
   - Copy the generated token

3. **Enter the token in Auralis**:
   - Open Auralis and go to the Settings tab
   - Find the "Discogs Token" field
   - Paste your token and save settings

### Usage Limits
- Authenticated requests: 60 requests per minute
- User-Agent required: Provided automatically by Auralis
- Images have a separate rate limit of 1,000 per day

### Troubleshooting
- **401 Unauthorized**: Your token is invalid or expired
- **403 Forbidden**: Application has been blocked
- **429 Too Many Requests**: Rate limit exceeded
- Service will be automatically disabled if authentication fails

## Optimizing API Usage

Auralis employs several strategies to minimize API calls:

1. **Metadata Caching**:
   - Previously fetched metadata is cached locally
   - Files with the same audio fingerprint reuse metadata

2. **Adaptive Source Selection**:
   - Auralis learns which source works best for your collection
   - Most successful sources are prioritized automatically

3. **Batch Processing**:
   - Use the "Dry Run" feature to test with a small batch before processing your entire collection
   - This helps identify any API issues early

4. **Rate Limiting Protection**:
   - Built-in throttling prevents exceeding API rate limits
   - Failed requests are handled gracefully

## Privacy Considerations

When using external APIs, be aware that:
- Small audio fingerprints (not the actual audio) are sent to AcoustID
- Search queries based on your file metadata are sent to Discogs
- No personal information is shared with these services
- All processing occurs on your local machine

## Support

If you encounter issues with API integration:
1. Check the error message in the application log
2. Verify your API keys in the Settings tab
3. Ensure your internet connection is stable
4. Try processing a smaller batch of files
5. Consult the service status pages for AcoustID or Discogs 