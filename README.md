# Stock Market Analyzer

A full-stack web application that provides real-time stock market data analysis with AI-powered insights using yfinance, Flask, React, and MongoDB.

![Stock Market Analyzer](https://via.placeholder.com/800x400?text=Stock+Market+Analyzer)

## Features

- **Real-time Stock Data**: Fetch up-to-date stock information using Yahoo Finance API
- **Interactive Charts**: Visualize historical stock prices with customizable time ranges
- **AI-Powered Analysis**: Get intelligent stock analysis using Google's Gemini AI
- **Responsive UI**: Modern Material UI design that works on all devices
- **MongoDB Integration**: Store search history and track popular stocks
- **Graceful Degradation**: Fallback mechanisms when external APIs are rate-limited

## Technology Stack

### Backend
- **Flask**: Python web framework for the backend API
- **yfinance**: Yahoo Finance API wrapper for stock data
- **Google Gemini AI**: AI model for stock analysis
- **MongoDB**: NoSQL database for storing search history and analyses
- **Python libraries**: pymongo, flask-cors, python-dotenv, etc.

### Frontend
- **React**: JavaScript library for building the user interface
- **Material UI**: Component library for modern design
- **Chart.js**: JavaScript charting library for visualizations
- **Axios**: Promise-based HTTP client for API requests
- **React Router**: For navigation between pages

## Project Structure

```
stock-analyzer/
├── backend/                  # Flask backend
│   ├── app.py                # Main Flask application
│   ├── .env                  # Environment variables
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── public/               # Static files
│   ├── src/                  # React source code
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   └── App.js            # Main React component
│   └── package.json          # npm dependencies
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Node.js and npm
- Python 3.8 or higher
- MongoDB (local or Atlas)
- Google Gemini API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/stock-analyzer.git
   cd stock-analyzer
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a `.env` file in the backend directory
   - Add your Gemini API key and MongoDB connection URI:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     MONGO_URI=mongodb://localhost:27017/
     ```

5. **Start MongoDB service**
   - **Windows**:
     - Open Services app (services.msc)
     - Find "MongoDB Server" and ensure it's running
   - **macOS/Linux**:
     ```bash
     sudo systemctl start mongod
     ```
   - **Alternative**: Create a free MongoDB Atlas cluster and use its connection string

6. **Run the Flask backend**
   ```bash
   python app.py
   ```
   The backend will be available at http://localhost:5000

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install npm dependencies**
   ```bash
   npm install
   ```

3. **Start the React development server**
   ```bash
   npm start
   ```
   The frontend will be available at http://localhost:3000

## How It Works

### Data Flow

1. **User Searches for a Stock**:
   - User enters a ticker symbol (e.g., AAPL, MSFT)
   - Request is sent to the Flask backend

2. **Backend Processing**:
   - Flask receives the request and tries to fetch data from Yahoo Finance
   - If successful, data is returned and also stored in MongoDB
   - If rate-limited, the app uses cached data or fallback mechanisms
   - Search count is incremented in the database

3. **Display and Visualization**:
   - Frontend displays stock information, charts, and metrics
   - Historical data is shown as an interactive chart
   - User can view different time periods (1M, 3M, 6M, 1Y, 5Y)

4. **AI Analysis**:
   - User can request an AI-powered analysis
   - Backend sends stock data to Google's Gemini API
   - AI generates a technical and fundamental analysis
   - Analysis is displayed to the user and stored in MongoDB

### Fallback Mechanisms

The application includes sophisticated fallback mechanisms to handle API rate limiting:

1. **Caching**: Frequently accessed data is cached to reduce API calls
2. **Rate Limiting**: Requests are spaced out to avoid hitting API limits
3. **Mock Data**: When APIs fail, synthetic data is generated for demonstration
4. **Local Storage**: Pre-defined data for common stocks is stored locally

### MongoDB Usage

MongoDB stores three types of data:

1. **Stock Information**: Basic data about each stock that's been searched
2. **Search Popularity**: Counts of how many times each stock has been searched
3. **AI Analyses**: Saved analyses from the Gemini API

## Troubleshooting

### Common Issues

1. **429 Too Many Requests Error**:
   - The Yahoo Finance API is rate-limiting your requests
   - The app will automatically use fallback data
   - Wait a few minutes before making more requests
   - or upgrade the yfinance's version

2. **MongoDB Connection Issues**:
   - Ensure MongoDB is running on your system
   - Check your MongoDB connection string in the `.env` file
   - Use MongoDB Compass to verify the connection

3. **Missing API Keys**:
   - Ensure you've added your Gemini API key to the `.env` file
   - Get a key from [Google AI Studio](https://ai.google.dev/)

## Future Enhancements

- Portfolio tracking functionality
- User authentication and saved preferences
- More detailed financial reports
- Comparison of multiple stocks
- News sentiment analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Yahoo Finance API](https://pypi.org/project/yfinance/) for stock data
- [Google Gemini AI](https://ai.google.dev/) for AI-powered analysis
- [Material UI](https://mui.com/) for the frontend components
- [Chart.js](https://www.chartjs.org/) for visualization
