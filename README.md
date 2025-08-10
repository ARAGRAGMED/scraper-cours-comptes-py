# 🏛️ Moroccan Court of Accounts Scraper

A comprehensive web scraper and API for extracting publications data from the Moroccan Court of Accounts website. Features a modern web interface, real-time scraping capabilities, and a robust FastAPI backend.

## ✨ Features

- **🌐 Live Web Scraping**: Real-time scraping of Court of Accounts publications
- **🚀 FastAPI Backend**: Modern, fast REST API with automatic documentation
- **🎨 Modern Web Interface**: Beautiful, responsive frontend with real-time data updates
- **📊 Dynamic Data Loading**: Publications loaded from JSON files with live updates
- **🔍 Category Filtering**: Filter publications by category with real-time search
- **⚙️ Configurable Scraping**: Customizable max pages and force re-scrape options
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices
- **🔄 Real-time Status**: Live scraping status and progress monitoring
- **📄 Publication Details**: Comprehensive publication information extraction
- **🌍 CORS Enabled**: Ready for cross-origin requests and integration

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ARAGRAGMED/scraper-cours-comptes-py.git
cd scrap-cour-des-comptes-scraper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
# From project root directory
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/api

## 🌐 Live Demo

**Production URL**: https://scrap-cour-des-comptes-scraper.vercel.app

## 🏗️ Architecture

### Backend (FastAPI)
- **API Routes**: `/api/court-accounts/*` endpoints
- **Scraping Service**: `CourtAccountsService` for web scraping operations
- **Data Management**: JSON file-based data storage and retrieval
- **CORS Support**: Cross-origin request handling

### Frontend (HTML/CSS/JavaScript)
- **Modern UI**: Clean, professional interface design
- **Real-time Updates**: Dynamic data loading and status updates
- **Responsive Layout**: Mobile-first design approach
- **Interactive Controls**: Scraping controls and category filtering

### Data Flow
1. **User Interface** → Frontend JavaScript
2. **API Calls** → FastAPI Backend
3. **Scraping Service** → Court of Accounts Website
4. **Data Storage** → JSON File
5. **Data Retrieval** → Frontend Display

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Main application page
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation
- `GET /openapi.json` - OpenAPI specification
- `GET /health` - Health check endpoint
- `GET /test` - Test endpoint
- `GET /api` - API information and available endpoints

### Court Accounts API
- `GET /api/court-accounts/publications` - Get all publications
- `GET /api/court-accounts/publications?category={category}` - Filter by category
- `GET /api/court-accounts/publications?year={year}` - Filter by year
- `GET /api/court-accounts/categories` - Get available categories
- `POST /api/court-accounts/scrape` - Start live scraping
- `GET /api/court-accounts/status` - Get scraping status

### Query Parameters
- `category`: Filter publications by category
- `year`: Filter publications by year
- `max_pages`: Maximum pages to scrape (POST request)
- `force_rescrape`: Force re-scraping even if data exists (POST request)

## 🎯 Usage Examples

### Start Scraping
```javascript
// Frontend JavaScript
const response = await fetch('/api/court-accounts/scrape', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        max_pages: 10,
        force_rescrape: true
    })
});

const result = await response.json();
console.log(result.message); // "Scraping completed! Found X publications."
```

### Get Publications by Category
```javascript
// Get publications in "Rapport" category
const response = await fetch('/api/court-accounts/publications?category=Rapport');
const data = await response.json();
console.log(`Found ${data.count} publications`);
```

### Filter by Year
```javascript
// Get publications from 2025
const response = await fetch('/api/court-accounts/publications?year=2025');
const data = await response.json();
console.log(`Found ${data.count} publications from 2025`);
```

## 📊 Data Structure

### Publication Object
```json
{
  "id": "unique_identifier",
  "title": "Publication Title",
  "category": "Rapport",
  "year": 2025,
  "url": "https://courdescomptes.ma/...",
  "scraped_at": "2025-01-15T10:30:00Z"
}
```

### API Response Format
```json
{
  "success": true,
  "publications": [...],
  "count": 2,
  "message": "Data retrieved successfully"
}
```

### Scraping Response
```json
{
  "success": true,
  "message": "Scraping completed! Found 2 publications.",
  "publications_count": 2,
  "details": {
    "status": "completed"
  }
}
```

## 🛠️ Development

### Project Structure
```
scrap-cour-des-comptes-scraper/
├── 📁 api/
│   ├── main.py                    # FastAPI application entry point
│   └── routes/
│       └── court_accounts.py      # API endpoints
├── 📁 app/
│   ├── api/                       # Original API structure
│   ├── core/                      # Configuration and security
│   ├── models/                    # Pydantic models
│   ├── services/                  # Business logic services
│   └── main.py                    # Original main application
├── 📁 public/                     # Frontend assets
│   ├── css/
│   │   └── styles.css            # Application styles
│   ├── js/
│   │   └── app.js                # Frontend JavaScript
│   └── index.html                # Main HTML page
├── 📁 data/                       # Data storage
│   └── court-accounts-publications-2025.json
├── 📁 src/                        # Core scraper logic
├── requirements.txt               # Python dependencies
├── vercel.json                   # Vercel deployment configuration
└── README.md                     # This file
```

### Local Development
```bash
# 1. Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 4. Access the application
open http://localhost:8000
```

### Testing the API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test publications endpoint
curl http://localhost:8000/api/court-accounts/publications

# Test scraping endpoint
curl -X POST http://localhost:8000/api/court-accounts/scrape \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 5, "force_rescrape": true}'
```

## 🚀 Deployment

### Vercel Deployment
The application is configured for automatic deployment on Vercel:

1. **Automatic Deploy**: Push to `main` branch triggers deployment
2. **Production URL**: https://scrap-cour-des-comptes-scraper.vercel.app
3. **Configuration**: `vercel.json` handles routing and function configuration

### Deployment Configuration
```json
{
  "functions": {
    "api/main.py": {
      "maxDuration": 60,
      "memory": 1024
    }
  },
  "rewrites": [
    { "src": "/api/(.*)", "dest": "/api/main.py" },
    { "src": "/", "dest": "/api/main.py" }
  ]
}
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `env.example`:
```bash
# Database settings (if needed)
DATABASE_URL=sqlite:///./court_accounts.db

# API settings
API_KEY=your_api_key_here
DEBUG=True
```

### Scraper Configuration
The scraper uses configuration from `config/scraper_config.json`:
```json
{
  "scraper_settings": {
    "force_rescrape": false,
    "max_pages": 10,
    "enable_logs": true
  },
  "request_settings": {
    "timeout": 30,
    "retry_attempts": 3,
    "delay_between_requests": 2
  }
}
```

## 📱 Frontend Features

### User Interface
- **Scraping Controls**: Start scraping with configurable parameters
- **Category Filter**: Real-time filtering of publications
- **Status Display**: Live scraping status and progress
- **Data Table**: Responsive table with publication details
- **Modern Design**: Clean, professional appearance

### Interactive Elements
- **Start Scraping Button**: Initiates live web scraping
- **Category Dropdown**: Filter publications by category
- **Status Indicators**: Visual feedback for scraping operations
- **Responsive Layout**: Works on all device sizes

## 🛡️ Security & Best Practices

- **CORS Configuration**: Properly configured for cross-origin requests
- **Input Validation**: Pydantic models ensure data validation
- **Error Handling**: Comprehensive error handling and user feedback
- **Rate Limiting**: Built-in delays between scraping requests
- **User-Agent Headers**: Proper browser identification

## 🔍 Troubleshooting

### Common Issues

#### 1. Frontend Styles Not Loading
```bash
# Ensure you're running from the root directory
cd /path/to/scrap-cour-des-comptes-scraper
uvicorn api.main:app --reload
```

#### 2. API Endpoints Returning 404
- Check that the server is running with `uvicorn api.main:app`
- Verify the API base URL in `public/js/app.js`
- Clear browser cache and hard refresh

#### 3. Scraping Not Working
- Check the server logs for error messages
- Verify the scraper service is properly imported
- Check that the target website is accessible

#### 4. Data Not Loading
- Verify the JSON data file exists in `data/` directory
- Check file permissions and encoding
- Review the API response in browser developer tools

### Debug Mode
Enable debug logging by setting environment variables:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
```

## 📈 Performance

### Optimization Features
- **Static File Serving**: Efficient CSS/JS file delivery
- **JSON Data Loading**: Fast data retrieval from local files
- **Caching**: Browser-level caching for static assets
- **Minimal Dependencies**: Lightweight, fast-loading application

### Monitoring
- **Health Checks**: `/health` endpoint for monitoring
- **Status Endpoints**: Real-time scraping status
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Request timing and response sizes

## 🔮 Future Enhancements

- **Database Integration**: SQL/NoSQL database storage
- **User Authentication**: Secure access control
- **Scheduled Scraping**: Automated periodic updates
- **Email Notifications**: Alerts for new publications
- **Advanced Analytics**: Data analysis and reporting
- **Mobile App**: Native mobile application
- **API Rate Limiting**: Advanced request throttling
- **Webhook Support**: Real-time notifications

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Add comprehensive error handling
- Include docstrings for all functions
- Test your changes locally before submitting
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **Vercel**: Serverless deployment platform
- **Moroccan Court of Accounts**: Data source
- **Open Source Community**: Contributors and maintainers

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the `/docs` endpoint for API documentation
- **Email**: Contact the development team

---

**🎉 Ready for production use with comprehensive web scraping, modern API, and beautiful frontend!**

**Live Demo**: https://scrap-cour-des-comptes-scraper.vercel.app
**API Docs**: https://scrap-cour-des-comptes-scraper.vercel.app/docs
