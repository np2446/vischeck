import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  TextField,
  Typography,
  Container,
  createTheme,
  ThemeProvider,
  CssBaseline
} from '@mui/material';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

const theme = createTheme({
  palette: {
    primary: {
      main: '#0078D4',
    },
    secondary: {
      main: '#FFFFFF',
    },
    background: {
      default: '#F3F2F1',
    },
  },
  typography: {
    fontFamily: 'Segoe UI, sans-serif',
    fontSize: 14,
  },
});

function PasswordPage({ setAuth }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const navigate = useNavigate(); // Create a navigate function instance

  const verifyPassword = async () => {
    try {
      const response = await axios.get('https://intense-sands-59577-33fe9a67166e.herokuapp.com/password' + "?given_password=" + password);
      if (response.data.correct === true) {
        setAuth(true);  // Set authentication state to true
        navigate('/');  // Navigate to the main page
      } else {
        setError(true);
        setPassword('');
      }
    } catch (error) {
      setError(true);
      console.error('Error verifying password:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh'
          }}
        >
          <Typography variant="h5" component="h1" sx={{ mb: 4 }}>
            Enter Password
          </Typography>
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={error}
            helperText={error ? "Incorrect password, please try again." : ""}
            sx={{ mb: 2, width: '100%' }}
          />
          <Button variant="contained" color="primary" onClick={verifyPassword}>
            Submit
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default PasswordPage;