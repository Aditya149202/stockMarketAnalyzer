import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box,
  Chip
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

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

const StockCard = ({ stock }) => {
  const isPositive = stock.change > 0;
  
  return (
    <Card className="stock-card" component={Link} to={`/stock/${stock.ticker}`} 
      sx={{ 
        textDecoration: 'none',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: '0 10px 20px rgba(0,0,0,0.2)'
        }
      }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="div">
            {stock.ticker}
          </Typography>
          <Chip 
            icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
            label={`${isPositive ? '+' : ''}${stock.change?.toFixed(2)}%`}
            color={isPositive ? 'success' : 'error'}
            size="small"
          />
        </Box>
        
        <Typography sx={{ mb: 1.5 }} color="text.secondary">
          {stock.name}
        </Typography>
        
        <Typography variant="h6" component="div" sx={{ mt: 2 }}>
          {typeof stock.price === 'number' ? `$${stock.price.toFixed(2)}` : stock.price}
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Market Cap: {formatNumber(stock.marketCap)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            P/E: {stock.pe !== 'N/A' ? stock.pe?.toFixed(2) : 'N/A'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StockCard;