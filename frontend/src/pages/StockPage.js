import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper,
  Tabs,
  Tab,
  Chip,
  Divider,
  CircularProgress,
  Button,
  Alert
} from '@mui/material';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const formatNumber = (num) => {
  if (num === 'N/A') return 'N/A';
  
  if (num >= 1000000000) {
    return `$${(num / 1000000000).toFixed(2)}B`;
  } else if (num >= 1000000) {
    return `$${(num / 1000000).toFixed(2)}M`;
  } else if (num >= 1000) {
    return `$${(num / 1000).toFixed(2)}K`;
  }
  return `$${num?.toFixed(2)}`;
};

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const StockPage = () => {
  const { ticker } = useParams();
  const [stockInfo, setStockInfo] = useState(null);
  const [stockHistory, setStockHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('1y');
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  
  const timeRanges = [
    { label: '1M', value: '1mo' },
    { label: '3M', value: '3mo' },
    { label: '6M', value: '6mo' },
    { label: '1Y', value: '1y' },
    { label: '5Y', value: '5y' }
  ];
  
  useEffect(() => {
    const fetchStockData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Fetch stock information
        const infoResponse = await axios.get(`${API_URL}/api/stock-info/${ticker}`);
        if (infoResponse.data.success) {
          setStockInfo(infoResponse.data.data);
        }
        
        // Fetch stock price history
        await fetchHistoricalData(timeRange);
      } catch (err) {
        console.error('Error fetching stock data:', err);
        setError('Failed to load stock data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStockData();
  }, [ticker]);
  
  const fetchHistoricalData = async (period) => {
    try {
      const historyResponse = await axios.get(`${API_URL}/api/stock-history/${ticker}?period=${period}`);
      if (historyResponse.data.success) {
        setStockHistory(historyResponse.data.data);
        setTimeRange(period);
      }
    } catch (err) {
      console.error('Error fetching historical data:', err);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleAnalyze = async () => {
    setAnalysisLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/analyze`, { ticker });
      if (response.data.success) {
        setAnalysis(response.data.data.analysis);
      }
    } catch (err) {
      console.error('Error analyzing stock:', err);
      setError('Failed to analyze stock. Please try again later.');
    } finally {
      setAnalysisLoading(false);
    }
  };
  
  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  
  if (!stockInfo) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="warning">Stock data not found for ticker: {ticker}</Alert>
      </Container>
    );
  }
  
  // Prepare chart data
  const chartData = {
    labels: stockHistory?.map(item => item.date) || [],
    datasets: [
      {
        label: 'Price',
        data: stockHistory?.map(item => item.close) || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.1,
      },
    ],
  };
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${ticker} Stock Price History`,
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function(value) {
            return '$' + value.toFixed(2);
          }
        }
      }
    }
  };
  
  const isPositive = stockInfo.change > 0;
  
  return (
    <Container className="container">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Typography variant="h3">{ticker}</Typography>
            <Typography variant="h5" color="text.secondary">{stockInfo.name}</Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h4">${stockInfo.price?.toFixed(2)}</Typography>
            <Chip 
              icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={`${isPositive ? '+' : ''}${stockInfo.change?.toFixed(2)}%`}
              color={isPositive ? 'success' : 'error'}
              size="medium"
            />
          </Box>
        </Box>
      </Box>
      
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="Overview" />
            <Tab label="Chart" />
            <Tab label="Analysis" />
          </Tabs>
        </Box>
        
        {tabValue === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Market Information</Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Market Cap</Typography>
                    <Typography variant="body1">{formatNumber(stockInfo.marketCap)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Volume</Typography>
                    <Typography variant="body1">{formatNumber(stockInfo.volume)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Avg Volume</Typography>
                    <Typography variant="body1">{formatNumber(stockInfo.averageVolume)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Dividend Yield</Typography>
                    <Typography variant="body1">
                      {stockInfo.dividend !== 'N/A' ? `${stockInfo.dividend.toFixed(2)}%` : 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Valuation</Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">P/E Ratio</Typography>
                    <Typography variant="body1">
                      {stockInfo.pe !== 'N/A' ? stockInfo.pe.toFixed(2) : 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">EPS</Typography>
                    <Typography variant="body1">
                      {stockInfo.eps !== 'N/A' ? `$${stockInfo.eps.toFixed(2)}` : 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Target Low</Typography>
                    <Typography variant="body1">
                      {stockInfo.targetLow !== 'N/A' ? `$${stockInfo.targetLow.toFixed(2)}` : 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Target High</Typography>
                    <Typography variant="body1">
                      {stockInfo.targetHigh !== 'N/A' ? `$${stockInfo.targetHigh.toFixed(2)}` : 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
            
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Analyst Recommendation</Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                  {stockInfo.recommendation}
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        )}
        
        {tabValue === 1 && (
          <Box>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {timeRanges.map((range) => (
                <Button 
                  key={range.value}
                  variant={timeRange === range.value ? "contained" : "outlined"}
                  size="small"
                  onClick={() => fetchHistoricalData(range.value)}
                >
                  {range.label}
                </Button>
              ))}
            </Box>
            
            <Box sx={{ height: 400 }}>
              {stockHistory ? (
                <Line data={chartData} options={chartOptions} />
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                  <CircularProgress />
                </Box>
              )}
            </Box>
          </Box>
        )}
        
        {tabValue === 2 && (
          <Box>
            {!analysis && !analysisLoading && (
              <Box sx={{ textAlign: 'center', my: 4 }}>
                <Typography variant="body1" gutterBottom>
                  Get AI-powered analysis for {ticker} based on technical and fundamental indicators.
                </Typography>
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={handleAnalyze}
                  sx={{ mt: 2 }}
                >
                  Analyze Stock
                </Button>
              </Box>
            )}
            
            {analysisLoading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
              </Box>
            )}
            
            {analysis && (
              <Box className="analysis-container">
                <Typography variant="h6" gutterBottom>
                  AI Analysis for {ticker}
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                  {analysis}
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default StockPage;