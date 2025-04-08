import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  TextField,
  Button,
  Box,
  Grid,
  Paper,
  CircularProgress,
  Divider
} from '@mui/material';
import axios from 'axios';
import StockCard from '../components/StockCard';

const defaultStocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'];

const HomePage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [featuredStocks, setFeaturedStocks] = useState([]);
  const [popularStocks, setPopularStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchDefaultStocks = async () => {
      setLoading(true);
      try {
        // Fetch data for default stocks
        const stockPromises = defaultStocks.map(ticker => 
          axios.get(`/api/stock-info/${ticker}`)
        );
        
        const results = await Promise.all(stockPromises);
        const stocksData = results
          .filter(res => res.data.success)
          .map(res => res.data.data);
        
        setFeaturedStocks(stocksData);
        
        // Fetch popular stocks from backend
        const popularRes = await axios.get('/api/popular-stocks');
        if (popularRes.data.success) {
          setPopularStocks(popularRes.data.data);
        }
      } catch (error) {
        console.error('Error fetching stocks:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDefaultStocks();
  }, []);
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      window.location.href = `/stock/${searchTerm.trim().toUpperCase()}`;
    }
  };
  
  return (
    <Container className="container">
      <Box className="hero-section">
        <Typography variant="h2" className="hero-title">
          Stock Market Analyzer
        </Typography>
        <Typography variant="h5" className="hero-subtitle" color="textSecondary">
          Analyze stocks with real-time data and AI-powered insights
        </Typography>
        
        <Box 
          component="form" 
          onSubmit={handleSearch}
          sx={{ 
            display: 'flex', 
            justifyContent: 'center',
            gap: 1,
            maxWidth: 600,
            mx: 'auto'
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Enter stock ticker (e.g., AAPL, MSFT)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              sx: { borderRadius: 2 }
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            size="large"
            sx={{ borderRadius: 2 }}
          >
            Analyze
          </Button>
        </Box>
      </Box>
      
      <Paper sx={{ p: 3, mb: 4, mt: 4, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          Featured Stocks
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3} className="stock-grid">
            {featuredStocks.map((stock) => (
              <Grid item xs={12} sm={6} md={4} key={stock.ticker}>
                <StockCard stock={stock} />
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
      
      {popularStocks.length > 0 && (
        <Paper sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h4" gutterBottom>
            Popular Searches
          </Typography>
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3} className="stock-grid">
            {popularStocks.map((item) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={item.ticker}>
                <Paper 
                  sx={{ 
                    p: 2, 
                    textAlign: 'center',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      cursor: 'pointer'
                    }
                  }}
                  onClick={() => window.location.href = `/stock/${item.ticker}`}
                >
                  <Typography variant="h6">{item.ticker}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {item.name}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                    Searched {item.count} times
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Container>
  );
};

export default HomePage;