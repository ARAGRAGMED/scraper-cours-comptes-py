# Local Development Guide

## Prerequisites

1. **Python 3.9+**: Make sure you have Python 3.9 or higher installed
2. **pip**: Python package installer
3. **Git**: Version control system

## Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd scrap-cour-des-comptes-scraper
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the root directory:
```bash
# Copy from env.example
cp env.example .env

# Edit .env file with your values
API_KEY=your_local_api_key_here
VERCEL_ENV=development
```

## Running the Application

### 1. Start the FastAPI Server
```bash
# From the root directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access the Application
- **API Documentation**: http://localhost:8000/docs/
- **Frontend**: http://localhost:8000
- **API Base**: http://localhost:8000/api/v1

## Development Workflow

### 1. Code Changes
- Make changes to your code
- The server will automatically reload (thanks to `--reload` flag)
- Test your changes immediately

### 2. Testing API Endpoints
You can test the API using:

#### cURL
```bash
# Test public endpoint
curl http://localhost:8000/api/court-accounts/status

# Test protected endpoint
curl -X POST http://localhost:8000/api/court-accounts/scrape \
  -H "Authorization: Bearer your_local_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"category_filter": "Rapport thématique", "max_pages": 2}'
```

#### FastAPI Interactive Docs
- Visit http://localhost:8000/docs/
- Use the interactive interface to test endpoints
- Set your API key in the Authorize button

#### Python Requests
```python
import requests

# Test public endpoint
response = requests.get('http://localhost:8000/api/court-accounts/status')
print(response.json())

# Test protected endpoint
headers = {'Authorization': 'Bearer your_local_api_key_here'}
data = {'category_filter': 'Rapport thématique', 'max_pages': 2}
response = requests.post('http://localhost:8000/api/court-accounts/scrape', 
                        json=data, headers=headers)
print(response.json())
```

### 3. Frontend Development
- Edit files in the `public/` directory
- Changes will be reflected immediately
- Use browser developer tools for debugging

## Project Structure

```
scrap-cour-des-comptes-scraper/
├── app/                          # FastAPI application
│   ├── main.py                  # Application entry point
│   ├── core/                    # Core configuration and utilities
│   │   ├── config.py           # Settings and environment variables
│   │   ├── security.py         # Authentication and security
│   │   └── database.py         # Data storage utilities
│   ├── models/                  # Pydantic data models
│   │   ├── court_accounts.py   # Court of Accounts models
│   │   └── responses.py        # Common response models
│   ├── services/                # Business logic layer
│   │   └── court_accounts_service.py  # Scraping service
│   └── api/                     # API endpoints
│       ├── v1/                  # API version 1
│       │   ├── endpoints/       # Individual endpoint modules
│       │   └── api.py          # Main API router
│       └── dependencies.py     # Shared API dependencies
├── public/                      # Static files (served at root)
│   ├── index.html              # Main HTML page
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript files
├── src/                         # Original scraper code
├── config/                      # Configuration files
├── requirements.txt             # Python dependencies
├── vercel.json                 # Vercel deployment config
└── .env                        # Local environment variables
```

## Configuration

### Environment Variables
- `API_KEY`: Your API key for authentication
- `VERCEL_ENV`: Environment (development/production)
- `DATABASE_URL`: External database URL (optional)
- `UPSTASH_REDIS_REST_URL`: Redis URL (optional)
- `UPSTASH_REDIS_REST_TOKEN`: Redis token (optional)

### Scraper Configuration
The scraper configuration is in `config/scraper_config.json`. You can modify:
- Scraper settings (force rescrape, max pages, etc.)
- Proxy settings
- Request settings (timeout, retries, user agent)
- Logging settings

## Debugging

### 1. Logs
FastAPI provides detailed logging. Check the console output for:
- Request/response logs
- Error messages
- Performance metrics

### 2. Debug Mode
The `--reload` flag enables debug mode with:
- Automatic server restart on code changes
- Detailed error messages
- Stack traces

### 3. Browser Developer Tools
- Check Network tab for API calls
- Check Console for JavaScript errors
- Use Sources tab for debugging JavaScript

### 4. Python Debugger
Add breakpoints in your code:
```python
import pdb; pdb.set_trace()
```

## Testing

### 1. Manual Testing
- Use the frontend interface
- Test all API endpoints
- Verify data flow from scraping to display

### 2. API Testing
- Test with different parameters
- Test error conditions
- Test authentication

### 3. Frontend Testing
- Test all user interactions
- Test responsive design
- Test different browsers

## Performance

### 1. Local vs Production
- Local development may be slower
- File I/O operations are faster locally
- Network requests may be slower locally

### 2. Optimization
- Use async/await for I/O operations
- Implement caching where appropriate
- Monitor memory usage

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure virtual environment is activated
   - Check Python path
   - Verify all dependencies are installed

2. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

3. **Permission Errors**
   - Check file permissions
   - Make sure you have write access to the directory

4. **Module Not Found**
   - Check if virtual environment is activated
   - Verify requirements.txt is up to date
   - Check import paths in your code

### Getting Help

1. Check FastAPI documentation: https://fastapi.tiangolo.com/
2. Check Python documentation: https://docs.python.org/
3. Use Stack Overflow for specific issues
4. Check the project's issue tracker

## Next Steps

1. **Add Tests**: Implement unit tests and integration tests
2. **Add Logging**: Implement proper logging throughout the application
3. **Add Monitoring**: Add health checks and metrics
4. **Optimize Performance**: Implement caching and database optimization
5. **Add CI/CD**: Set up automated testing and deployment
