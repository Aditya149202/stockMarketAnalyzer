from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pymongo
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import logging
import traceback
import time
import random
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["stock_analyzer"]
stocks_collection = db["stocks"]
analyses_collection = db["analyses"]

# Fallback stock data for demonstration when API fails
fallback_stocks = {
    "AAPL": {"name": "Apple Inc.", "price": 173.31, "change": 0.65},
    "MSFT": {"name": "Microsoft Corporation", "price": 417.12, "change": 1.23},
    "GOOGL": {"name": "Alphabet Inc.", "price": 157.73, "change": -0.42},
    "AMZN": {"name": "Amazon.com, Inc.", "price": 183.32, "change": 0.87},
    "META": {"name": "Meta Platforms, Inc.", "price": 487.58, "change": 1.05}
}

# Cache for popular stocks to avoid frequent MongoDB queries
popular_stocks_cache = None
popular_stocks_timestamp = 0
CACHE_TIMEOUT = 300  # 5 minutes

# Add a cache decorator to reduce API calls
@lru_cache(maxsize=100)
def get_cached_stock_info(ticker):
    # Add a random delay between 1-3 seconds to avoid rate limiting
    time.sleep(random.uniform(1,3))
    stock = yf.Ticker(ticker)
    return stock.info

# Add a cache for stock history data
@lru_cache(maxsize=50)
def get_cached_stock_history(ticker, period, interval):
    # Add a random delay between 1-3 seconds to avoid rate limiting
    time.sleep(random.uniform(1, 3))
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)

@app.route('/api/stock-info/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    try:
        logger.info(f"Fetching stock info for {ticker}")
        
        # First check if we have fallback data for this ticker to avoid API call if needed
        if ticker in fallback_stocks:
            # 20% chance to use fallback data directly (reduces API load)
            if random.random() < 0.2:
                logger.info(f"Using fallback data for {ticker} to reduce API load")
                fallback = fallback_stocks[ticker]
                fallback_data = {
                    "ticker": ticker,
                    "name": fallback["name"],
                    "price": fallback["price"],
                    "change": fallback["change"],
                    "marketCap": 'N/A',
                    "volume": 'N/A',
                    "averageVolume": 'N/A',
                    "pe": 'N/A',
                    "eps": 'N/A',
                    "dividend": 'N/A',
                    "targetHigh": 'N/A',
                    "targetLow": 'N/A',
                    "targetMean": 'N/A',
                    "recommendation": 'N/A',
                }
                
                # Store the search in MongoDB with fallback data
                try:
                    stocks_collection.update_one(
                        {"ticker": ticker},
                        {"$set": {"info": {"longName": fallback["name"]}}, 
                         "$inc": {"search_count": 1}},
                        upsert=True
                    )
                except Exception as mongo_err:
                    logger.error(f"MongoDB error: {str(mongo_err)}")
                
                return jsonify({
                    "success": True,
                    "data": fallback_data,
                    "message": "Using fallback data to reduce API load"
                })
        
        # Try to get info with caching and rate limiting
        try:
            info = get_cached_stock_info(ticker)
        except Exception as api_error:
            logger.warning(f"API error when fetching {ticker}: {str(api_error)}")
            # Wait longer and try one more time
            time.sleep(5)
            try:
                info = get_cached_stock_info(ticker)
            except Exception as retry_error:
                logger.error(f"Retry failed for {ticker}: {str(retry_error)}")
                # Use fallback data if available
                if ticker in fallback_stocks:
                    fallback = fallback_stocks[ticker]
                    fallback_data = {
                        "ticker": ticker,
                        "name": fallback["name"],
                        "price": fallback["price"],
                        "change": fallback["change"],
                        "marketCap": 'N/A',
                        "volume": 'N/A',
                        "averageVolume": 'N/A',
                        "pe": 'N/A',
                        "eps": 'N/A',
                        "dividend": 'N/A',
                        "targetHigh": 'N/A',
                        "targetLow": 'N/A',
                        "targetMean": 'N/A',
                        "recommendation": 'N/A',
                    }
                    
                    # Store the search in MongoDB with fallback data
                    try:
                        stocks_collection.update_one(
                            {"ticker": ticker},
                            {"$set": {"info": {"longName": fallback["name"]}}, 
                             "$inc": {"search_count": 1}},
                            upsert=True
                        )
                    except Exception as mongo_err:
                        logger.error(f"MongoDB error: {str(mongo_err)}")
                    
                    return jsonify({
                        "success": True,
                        "data": fallback_data,
                        "message": "Using fallback data due to API limitations"
                    })
                return jsonify({"success": False, "error": str(retry_error)}), 500
        
        # Check if we got valid info
        if not info or 'longName' not in info:
            logger.warning(f"No valid data returned for {ticker}, using fallback data")
            # Use fallback data if available
            if ticker in fallback_stocks:
                fallback = fallback_stocks[ticker]
                fallback_data = {
                    "ticker": ticker,
                    "name": fallback["name"],
                    "price": fallback["price"],
                    "change": fallback["change"],
                    "marketCap": 'N/A',
                    "volume": 'N/A',
                    "averageVolume": 'N/A',
                    "pe": 'N/A',
                    "eps": 'N/A',
                    "dividend": 'N/A',
                    "targetHigh": 'N/A',
                    "targetLow": 'N/A',
                    "targetMean": 'N/A',
                    "recommendation": 'N/A',
                }
                
                # Store the search in MongoDB with fallback data
                stocks_collection.update_one(
                    {"ticker": ticker},
                    {"$set": {"info": {"longName": fallback["name"]}}, 
                     "$inc": {"search_count": 1}},
                    upsert=True
                )
                
                return jsonify({
                    "success": True,
                    "data": fallback_data,
                    "message": "Using fallback data due to API limitations"
                })
            else:
                return jsonify({
                    "success": False, 
                    "error": f"Could not fetch data for {ticker}"
                }), 404
                
        # Store the search in MongoDB
        stocks_collection.update_one(
            {"ticker": ticker},
            {"$set": {"info": info}, "$inc": {"search_count": 1}},
            upsert=True
        )
        
        return jsonify({
            "success": True,
            "data": {
                "ticker": ticker,
                "name": info.get('longName', 'N/A'),
                "price": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                "change": info.get('regularMarketChangePercent', 'N/A'),
                "marketCap": info.get('marketCap', 'N/A'),
                "volume": info.get('volume', 'N/A'),
                "averageVolume": info.get('averageVolume', 'N/A'),
                "pe": info.get('trailingPE', 'N/A'),
                "eps": info.get('trailingEps', 'N/A'),
                "dividend": info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A',
                "targetHigh": info.get('targetHighPrice', 'N/A'),
                "targetLow": info.get('targetLowPrice', 'N/A'),
                "targetMean": info.get('targetMeanPrice', 'N/A'),
                "recommendation": info.get('recommendationKey', 'N/A'),
            }
        })
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Use fallback data if available
        if ticker in fallback_stocks:
            fallback = fallback_stocks[ticker]
            fallback_data = {
                "ticker": ticker,
                "name": fallback["name"],
                "price": fallback["price"],
                "change": fallback["change"],
                "marketCap": 'N/A',
                "volume": 'N/A',
                "averageVolume": 'N/A',
                "pe": 'N/A',
                "eps": 'N/A',
                "dividend": 'N/A',
                "targetHigh": 'N/A',
                "targetLow": 'N/A',
                "targetMean": 'N/A',
                "recommendation": 'N/A',
            }
            
            # Store the search in MongoDB with fallback data
            try:
                stocks_collection.update_one(
                    {"ticker": ticker},
                    {"$set": {"info": {"longName": fallback["name"]}}, 
                     "$inc": {"search_count": 1}},
                    upsert=True
                )
            except Exception as mongo_err:
                logger.error(f"MongoDB error: {str(mongo_err)}")
            
            return jsonify({
                "success": True,
                "data": fallback_data,
                "message": "Using fallback data due to API limitations"
            })
        
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stock-history/<ticker>', methods=['GET'])
def get_stock_history(ticker):
    try:
        logger.info(f"Fetching stock history for {ticker}")
        period = request.args.get('period', '1y')
        interval = request.args.get('interval', '1d')
        
        # Try to get cached history data
        try:
            history = get_cached_stock_history(ticker, period, interval)
        except Exception as api_error:
            logger.warning(f"API error when fetching history for {ticker}: {str(api_error)}")
            # Wait longer and try one more time
            time.sleep(5)
            try:
                history = get_cached_stock_history(ticker, period, interval)
            except Exception as retry_error:
                logger.error(f"Retry failed for {ticker} history: {str(retry_error)}")
                # Force use of mock data by raising the exception
                raise
        
        # Check if history is empty
        if history.empty:
            logger.warning(f"No history data returned for {ticker}, generating mock data")
            # Generate mock data for demonstration
            import numpy as np
            from datetime import timedelta
            
            # Create mock data
            base_price = 100
            if ticker in fallback_stocks:
                base_price = fallback_stocks[ticker]["price"]
            
            # Number of data points based on period
            periods_map = {
                '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '5y': 365*5
            }
            num_points = periods_map.get(period, 365)
            
            # Generate random walk prices
            np.random.seed(hash(ticker) % 100000)  # Make it deterministic but different for each ticker
            changes = np.random.normal(0, 1, num_points) / 100
            price_changes = np.cumprod(1 + changes)
            prices = base_price * price_changes
            
            # Generate dates
            end_date = datetime.now()
            dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_points)]
            dates.reverse()  # Earliest date first
            
            data = []
            for i, date in enumerate(dates):
                price = prices[i]
                data.append({
                    "date": date,
                    "open": round(price * 0.99, 2),
                    "high": round(price * 1.02, 2),
                    "low": round(price * 0.98, 2),
                    "close": round(price, 2),
                    "volume": int(np.random.normal(1000000, 500000))
                })
            
            return jsonify({
                "success": True, 
                "data": data,
                "message": "Using generated mock data due to API limitations"
            })
        
        data = []
        for index, row in history.iterrows():
            data.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": row['Volume']
            })
        
        return jsonify({"success": True, "data": data})
    except Exception as e:
        logger.error(f"Error fetching stock history for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Generate mock data for demonstration
        try:
            import numpy as np
            from datetime import timedelta
            
            # Create mock data
            base_price = 100
            if ticker in fallback_stocks:
                base_price = fallback_stocks[ticker]["price"]
            
            # Number of data points based on period
            periods_map = {
                '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '5y': 365*5
            }
            period = request.args.get('period', '1y')
            num_points = periods_map.get(period, 365)
            
            # Generate random walk prices
            np.random.seed(hash(ticker) % 100000)  # Make it deterministic but different for each ticker
            changes = np.random.normal(0, 1, num_points) / 100
            price_changes = np.cumprod(1 + changes)
            prices = base_price * price_changes
            
            # Generate dates
            end_date = datetime.now()
            dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_points)]
            dates.reverse()  # Earliest date first
            
            data = []
            for i, date in enumerate(dates):
                price = prices[i]
                data.append({
                    "date": date,
                    "open": round(price * 0.99, 2),
                    "high": round(price * 1.02, 2),
                    "low": round(price * 0.98, 2),
                    "close": round(price, 2),
                    "volume": int(np.random.normal(1000000, 500000))
                })
            
            return jsonify({
                "success": True, 
                "data": data,
                "message": "Using generated mock data due to API limitations"
            })
        except Exception as fallback_error:
            logger.error(f"Error generating fallback data: {str(fallback_error)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    try:
        logger.info("Analyzing stock")
        data = request.json
        ticker = data.get('ticker')
        
        if not ticker:
            return jsonify({"success": False, "error": "Ticker symbol is required"}), 400
        
        # Try to get stock info
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period='1y')
            
            # Check if we got valid info
            if not info or 'longName' not in info:
                raise ValueError(f"No valid data returned for {ticker}")
                
            # Calculate some basic metrics
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            avg_price_50d = info.get('fiftyDayAverage', 0)
            avg_price_200d = info.get('twoHundredDayAverage', 0)
            stock_name = info.get('longName', ticker)
            
        except Exception as stock_error:
            logger.warning(f"Error fetching stock data for analysis: {str(stock_error)}")
            # Use fallback data
            if ticker in fallback_stocks:
                fallback = fallback_stocks[ticker]
                current_price = fallback["price"]
                stock_name = fallback["name"]
                avg_price_50d = current_price * 0.95  # Mock value
                avg_price_200d = current_price * 0.9  # Mock value
            else:
                current_price = 100
                stock_name = ticker
                avg_price_50d = 95
                avg_price_200d = 90
        
        # Prepare prompt for Gemini
        prompt = f"""
        Analyze the stock {ticker} ({stock_name}) with the following information:
        - Current Price: ${current_price}
        - 50-Day Moving Average: ${avg_price_50d}
        - 200-Day Moving Average: ${avg_price_200d}
        
        Provide a concise analysis including:
        1. Technical analysis based on moving averages
        2. Investment recommendation (Buy, Hold, Sell) with a brief justification
        3. Key risks and opportunities
        Limit your response to 250 words or less.
        """
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            analysis_result = response.text
        except Exception as ai_error:
            logger.error(f"Error with Gemini API: {str(ai_error)}")
            # Provide a generic analysis if Gemini API fails
            if current_price > avg_price_50d > avg_price_200d:
                analysis_result = f"""
                Technical Analysis: {ticker} is showing a bullish trend with the current price (${current_price}) above both the 50-day moving average (${avg_price_50d}) and 200-day moving average (${avg_price_200d}). This indicates strong upward momentum.
                
                Recommendation: Buy - The stock shows strong technical signals with price above key moving averages.
                
                Risks: Market volatility could impact short-term performance. The stock may be overbought at current levels.
                
                Opportunities: Continued market strength could lead to further price appreciation. Consider dollar-cost averaging for entry points.
                
                Note: This is a generic analysis because the AI analysis service is currently unavailable. Please try again later for a more detailed assessment.
                """
            elif avg_price_50d > current_price > avg_price_200d:
                analysis_result = f"""
                Technical Analysis: {ticker} is in a neutral trend. The price (${current_price}) is below the 50-day moving average (${avg_price_50d}) but above the 200-day moving average (${avg_price_200d}), suggesting a possible consolidation phase.
                
                Recommendation: Hold - The stock is showing mixed signals. Wait for clearer direction before adding to position.
                
                Risks: Potential for further decline if support at the 200-day moving average doesn't hold.
                
                Opportunities: A bounce back above the 50-day moving average could signal renewed strength.
                
                Note: This is a generic analysis because the AI analysis service is currently unavailable. Please try again later for a more detailed assessment.
                """
            else:
                analysis_result = f"""
                Technical Analysis: {ticker} shows bearish signals with the current price (${current_price}) below both the 50-day moving average (${avg_price_50d}) and 200-day moving average (${avg_price_200d}).
                
                Recommendation: Sell/Avoid - The stock is displaying weakness from a technical perspective.
                
                Risks: Continued downward pressure could lead to further price declines.
                
                Opportunities: Watch for a potential reversal if price moves back above the 50-day moving average.
                
                Note: This is a generic analysis because the AI analysis service is currently unavailable. Please try again later for a more detailed assessment.
                """
        
        # Store the analysis in MongoDB
        try:
            analysis_doc = {
                "ticker": ticker,
                "timestamp": datetime.now(),
                "analysis": analysis_result,
                "current_price": current_price
            }
            analyses_collection.insert_one(analysis_doc)
        except Exception as mongo_err:
            logger.error(f"MongoDB error while storing analysis: {str(mongo_err)}")
        
        return jsonify({
            "success": True,
            "data": {
                "ticker": ticker,
                "analysis": analysis_result
            }
        })
    except Exception as e:
        logger.error(f"Error analyzing stock: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/popular-stocks', methods=['GET'])
def get_popular_stocks():
    global popular_stocks_cache, popular_stocks_timestamp
    
    try:
        # Check if we have a valid cache
        current_time = time.time()
        if popular_stocks_cache and current_time - popular_stocks_timestamp < CACHE_TIMEOUT:
            logger.info("Using cached popular stocks data")
            return jsonify({"success": True, "data": popular_stocks_cache})
        
        # Get the most searched stocks
        popular_stocks = list(stocks_collection.find({}, {"ticker": 1, "info.longName": 1, "search_count": 1})
                           .sort("search_count", -1)
                           .limit(5))
        
        result = []
        for stock in popular_stocks:
            result.append({
                "ticker": stock.get("ticker"),
                "name": stock.get("info", {}).get("longName", "Unknown"),
                "count": stock.get("search_count", 0)
            })
        
        # Update cache
        popular_stocks_cache = result
        popular_stocks_timestamp = current_time
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        logger.error(f"Error fetching popular stocks: {str(e)}")
        
        # If we have a cache, use it even if expired
        if popular_stocks_cache:
            logger.info("Using expired cache for popular stocks due to error")
            return jsonify({"success": True, "data": popular_stocks_cache, "cached": True})
            
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Create an initial pool of popular stocks
    try:
        logger.info("Pre-fetching data for common stocks...")
        # Pre-fetch data for common stocks to build cache
        for ticker in fallback_stocks.keys():
            try:
                # Don't wait for results - just trigger the cache build
                get_cached_stock_info(ticker)
                logger.info(f"Pre-fetched data for {ticker}")
                # Ensure we don't hit rate limits during startup
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not pre-fetch {ticker}: {str(e)}")
    except Exception as e:
        logger.error(f"Error during pre-fetching: {str(e)}")
        
    # Run the Flask app with increased request handling
    app.run(debug=True, threaded=True)