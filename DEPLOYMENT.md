# Deployment Guide for Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Python 3.9+**: Vercel supports Python 3.9 and above

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has the following structure:
```
scrap-cour-des-comptes-scraper/
├── app/
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── services/
│   └── api/
├── public/
│   ├── index.html
│   ├── css/
│   └── js/
├── src/
├── config/
├── requirements.txt
├── vercel.json
└── README.md
```

### 2. Set Environment Variables

In your Vercel dashboard, go to your project settings and add these environment variables:

```bash
# Required
API_KEY=your_secure_api_key_here
VERCEL_ENV=production

# Optional (for external database)
DATABASE_URL=your_external_db_url
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
```

### 3. Deploy to Vercel

#### Option A: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Option B: GitHub Integration
1. Connect your GitHub repository to Vercel
2. Vercel will automatically deploy on every push to main branch
3. Configure build settings if needed

### 4. Configure Custom Domain (Optional)

1. Go to your Vercel project dashboard
2. Navigate to "Domains"
3. Add your custom domain
4. Configure DNS records as instructed

## API Endpoints

After deployment, your API will be available at:

- **Base URL**: `https://your-project.vercel.app/api/v1`
- **Documentation**: `https://your-project.vercel.app/docs/`
- **Frontend**: `https://your-project.vercel.app`

### Available Endpoints

#### Public Endpoints (No API Key Required)
- `GET /api/court-accounts/status` - Get scraper status
- `GET /api/court-accounts/publications` - Get publications
- `GET /api/court-accounts/categories` - Get available categories
- `GET /api/data/stats` - Get data statistics
- `GET /api/data/years` - Get available years

#### Protected Endpoints (API Key Required)
- `POST /api/court-accounts/scrape` - Start scraping
- `POST /api/court-accounts/stop` - Stop scraping
- `GET /api/config/` - View configuration
- `PUT /api/config/` - Update configuration
- `GET /api/config/validate` - Validate configuration
- `GET /api/config/reset` - Reset configuration

## Usage

### 1. Get Your API Key
Set the `API_KEY` environment variable in Vercel dashboard.

### 2. Use the Frontend
- Visit your deployed URL
- Enter your API key in the "API Key" field
- Use the interface to control scraping and view data

### 3. Use the API Directly
```bash
# Example: Start scraping
curl -X POST "https://your-project.vercel.app/api/court-accounts/scrape" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"category_filter": "Rapport thématique", "max_pages": 5}'

# Example: Get publications
curl "https://your-project.vercel.app/api/court-accounts/publications?year=2023"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Timeout Errors**: Vercel has a 60-second timeout limit
3. **Memory Issues**: Vercel has memory limits for serverless functions
4. **File System**: Vercel has read-only file system, use external storage for data

### Debugging

1. Check Vercel function logs in the dashboard
2. Use `vercel logs` command for detailed logs
3. Test locally with `uvicorn app.main:app --reload`

### Performance Optimization

1. **Database**: Use external database (PostgreSQL, MongoDB) instead of file storage
2. **Caching**: Implement Redis caching for better performance
3. **Async Operations**: Use background tasks for long-running scraping operations
4. **Data Storage**: Store large datasets in external storage (S3, Google Cloud Storage)

## Security Considerations

1. **API Key**: Use a strong, unique API key
2. **Rate Limiting**: Implement rate limiting for public endpoints
3. **Input Validation**: Validate all input parameters
4. **HTTPS**: Vercel automatically provides HTTPS
5. **CORS**: Configure CORS properly for production

## Monitoring

1. **Vercel Analytics**: Monitor function performance and errors
2. **Logs**: Check function logs regularly
3. **Metrics**: Monitor API usage and response times
4. **Alerts**: Set up alerts for errors and performance issues

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Python on Vercel**: [vercel.com/docs/runtimes/python](https://vercel.com/docs/runtimes/python)
