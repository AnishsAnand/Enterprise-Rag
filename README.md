Enterprise RAG Bot

A comprehensive RAG (Retrieval-Augmented Generation) system with web scraping capabilities, built with FastAPI backend and Angular frontend.

Features

- Web Scraping: Advanced scraping with anti-blocking mechanisms
- Multiple Data Formats: Support for CSV, JSON, PDF, text, images, videos
- Dynamic URL Discovery: Automatically discover URLs from base domains
- RAG System: ChromaDB-powered document retrieval and AI responses
- Multiple AI Providers: OpenRouter.ai, Voyage, and local Ollama support

Architecture

Backend (FastAPI)
- Web Scraper Service: Multi-method scraping (requests, Selenium, Trafilatura)
- ChromaDB Integration: Vector storage and similarity search
- *AI Service: Multiple provider support with fallback mechanisms

Frontend (Angular)
-
- 1) Web Scraper**: Single URL and bulk scraping interfaces
- 2) RAG System**: Query interface and document management

Prerequisites
- Python 3.11.0
- Node.js 18+
- Chrome/Chromium (for Selenium)

API Keys Required:

1) OpenRouter.ai
- Sign up at https://openrouter.ai
- Get API key from dashboard
- Add to `.env` as `OPENROUTER_API_KEY`

2) Voyage AI
- Sign up at https://www.voyageai.com
- Get API key from dashboard  
- Add to `.env` as `VOYAGE_API_KEY`

3) Local Ollama (Backup)
- Install Ollama: https://ollama.ai
- Pull DeepSeek model: `ollama pull deepseek-v2:latest`
- Ensure running on `http://localhost:11434`

Usage:
-Web Scraping
1. Single URL**: Enter URL and configure extraction options
2. Bulk Scraping: Provide base URL for automatic discovery
3. Anti-Blocking: Automatic user-agent rotation and delays
4. Multiple Formats: Export as JSON, CSV, text, or PDF

- RAG System
1. Query: Ask questions about scraped content
2. Search: Find relevant documents without AI generation
3. Management: View statistics and clear system



ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

MAX_CONCURRENT_REQUESTS=10
REQUEST_DELAY=1.0
\`\`\`

Scraping Parameters
- extract_text: Extract plain text content
- extract_links: Extract all hyperlinks
- extract_images: Extract image URLs
- extract_tables: Extract table data
- scroll_page: Handle dynamic content loading
- wait_for_element: Wait for specific CSS selector

Anti-Blocking Features

1. User-Agent Rotation: Automatic rotation of browser user agents
2. Request Delays: Configurable delays between requests
3. Multiple Methods: Fallback between requests, Selenium, and Trafilatura
4. Undetected Chrome: Uses undetected-chromedriver for Selenium
5. Session Management: Maintains persistent sessions with cookies

API Endpoints

 Scraper
- `POST /api/scraper/scrape` - Scrape single URL
- `POST /api/scraper/bulk-scrape` - Start bulk scraping
- `GET /api/scraper/discover-urls` - Discover URLs from base
- `GET /api/scraper/scraping-status` - Get scraping status
RAG
- `POST /api/rag/query` - Query RAG system
- `POST /api/rag/add-document` - Add document manually
- `POST /api/rag/upload-file` - Upload file
- `GET /api/rag/search` - Search documents
- `GET /api/rag/stats` - Get RAG statistics
- `DELETE /api/rag/clear` - Clear all documents

Docker Deployment

\`\`\`dockerfile
Use provided Dockerfile
docker build -t enterprise-rag-bot .
docker run -p 8000:8000 -v ./chroma_db:/app/chroma_db enterprise-rag-bot
\`\`\`

Troubleshooting

Common Issues

1. ChromaDB Permission Error**
   \`\`\`bash
   sudo chown -R $USER:$USER ./chroma_db
   \`\`\`

2. Selenium Chrome Issues**
   \`\`\`bash
   Install Chrome dependencies
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   \`\`\`

3. API Key Issues**
   - Verify API keys in `.env` file
   - Check API key permissions and quotas
   - Ensure Ollama is running for local fallback

4. Angular Build Issues**
   \`\`\`bash
   cd angular-frontend
   npm install --force
   ng build --configuration production
   \`\`\`

Performance Optimization

1. Concurrent Scraping: Adjust `MAX_CONCURRENT_REQUESTS`
2. Request Delays: Tune `REQUEST_DELAY` for target sites
3. ChromaDB: Use persistent storage for better performance
4. Caching: Implement Redis for session caching

Security Considerations

1. API Keys: Store securely and rotate regularly
2. Rate Limiting: Implement rate limiting for public APIs
3. Input Validation: Validate all URLs and inputs
4. CORS: Configure CORS for production deployment

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review API documentation at `/docs`

## Roadmap

- [ ] Add support for more file formats (DOCX, XLSX)
- [ ] Implement real-time scraping monitoring
- [ ] Add webhook notifications
- [ ] Enhance AI model selection
- [ ] Add data export/import features
- [ ] Implement user authentication
- [ ] Add scheduled scraping tasks
