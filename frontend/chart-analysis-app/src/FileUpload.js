import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Papa from 'papaparse';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  Typography,
  createTheme,
  ThemeProvider,
  LinearProgress,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';
import ReactMarkdown from 'react-markdown';

const theme = createTheme({
  palette: {
    primary: {
      main: '#0078D4', // Microsoft blue
    },
    secondary: {
      main: '#FFFFFF', // White accents
    },
    background: {
      default: '#F3F2F1', // Light gray for Fluent Design consistency
    },
  },
  typography: {
    fontFamily: 'Segoe UI, sans-serif',
    fontSize: 14,
    button: {
      textTransform: 'none',
    },
  },
});

function FileUpload() {
  const [backendUrl, setBackendUrl] = useState("https://intense-sands-59577-33fe9a67166e.herokuapp.com/process-data");
  const [chartImage, setChartImage] = useState(null);
  const [chartDataCSV, setChartDataCSV] = useState(null);
  const [fullDataCSV, setFullDataCSV] = useState(null);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({
    image: null,
    chartData: null,
    fullData: null,
  });
  const [typedResponse, setTypedResponse] = useState('');

  useEffect(() => {
    if (response) {
      // set reponse to empty string to clear the previous response
      setTypedResponse(response[0]);
      let index = 0;
      const interval = setInterval(() => {
        if (index < response.length && response[index]) {
          setTypedResponse(prev => prev + response[index]);
          index += 1;
        } else {
          clearInterval(interval);
        }
      }, 1); // Adjust typing speed (lower value = faster)
      return () => clearInterval(interval);
    }
  }, [response]);

  // Refs for file inputs
  const imageInputRef = useRef(null);
  const chartDataInputRef = useRef(null);
  const fullDataInputRef = useRef(null);

  const handleImageChange = e => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      setChartImage(reader.result.split(',')[1]); // Remove the data URL part
      setUploadStatus(prev => ({ ...prev, image: file.name }));
    };
    reader.readAsDataURL(file);
  };

  const handleChartDataChange = e => {
    const file = e.target.files[0];
    setChartDataCSV(file);
    setUploadStatus(prev => ({ ...prev, chartData: file.name }));
  };

  const handleFullDataChange = e => {
    const file = e.target.files[0];
    setFullDataCSV(file);
    setUploadStatus(prev => ({ ...prev, fullData: file.name }));
  };

  const handleRemoveFile = field => {
    if (field === 'image') {
      setChartImage(null);
      setUploadStatus(prev => ({ ...prev, image: null }));
      if (imageInputRef.current) imageInputRef.current.value = null; // Clear input value
    }
    if (field === 'chartData') {
      setChartDataCSV(null);
      setUploadStatus(prev => ({ ...prev, chartData: null }));
      if (chartDataInputRef.current) chartDataInputRef.current.value = null; // Clear input value
    }
    if (field === 'fullData') {
      setFullDataCSV(null);
      setUploadStatus(prev => ({ ...prev, fullData: null }));
      if (fullDataInputRef.current) fullDataInputRef.current.value = null; // Clear input value
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Only check if chartImage is present
    if (!chartImage) return;
  
    setLoading(true);
  
    // If chartDataCSV or fullDataCSV are provided, parse them; otherwise, set them to null
    const chartData = chartDataCSV ? await parseCSV(chartDataCSV) : null;
    const fullData = fullDataCSV ? await parseCSV(fullDataCSV) : null;
  
    try {
      console.log("Sending data to backend..." + backendUrl);
      const response = await axios.post(backendUrl, {
        chart_data: chartData,
        full_data: fullData,
        chart_base64: chartImage
      });
      setResponse(response.data);
    } catch (error) {
      setResponse(`Error uploading files: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const parseCSV = file => {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: results => {
          const rows = results.data;
          const columns = {};
  
          rows.forEach((row, rowIndex) => {
            Object.keys(row).forEach(colName => {
              if (!columns[colName]) columns[colName] = {};
              columns[colName][rowIndex] = row[colName];
            });
          });
  
          // Resolve with a column-oriented data structure:
          resolve(columns);
        },
        error: err => reject(err),
      });
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(180deg, #F3F2F1, #FFFFFF)',
          padding: 4,
        }}
      >
        <Container maxWidth="md">
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            align="center"
            sx={{ color: '#0078D4', fontWeight: 600 }}
          >
            VisCheck
          </Typography>

          <Typography
            variant="body1"
            align="left"
            sx={{ color: '#000000', marginBottom: 2 }}
          >
            Please upload the files below to receive AI-generated recommendations on the ethical and aesthetic aspects of your data visualization. <strong>At minimum, provide the chart image.</strong> Data files should be in CSV format. If your chart represents only a portion of a larger dataset, consider uploading the full dataset as well for a more in-depth analysis.
          </Typography>

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
          >
            {['image', 'chartData', 'fullData'].map((field, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<UploadFileIcon />}
                  component="label"
                  color="primary"
                >
                  {`Upload ${field === 'image' ? 'Chart Image' : field === 'chartData' ? 'Chart Data (CSV)' : 'Full Data (CSV)'}`}
                  <input
                    type="file"
                    hidden
                    accept={field === 'image' ? 'image/*' : '.csv'}
                    onChange={field === 'image' ? handleImageChange : field === 'chartData' ? handleChartDataChange : handleFullDataChange}
                    ref={field === 'image' ? imageInputRef : field === 'chartData' ? chartDataInputRef : fullDataInputRef}
                  />
                </Button>
                {uploadStatus[field] && (
                  <>
                    <Typography variant="body2" color="primary">
                      {uploadStatus[field]}
                    </Typography>
                    <IconButton
                      sx={{ color: 'black' }}
                      onClick={() => handleRemoveFile(field)}
                      size="small"
                    >
                      <CloseIcon />
                    </IconButton>
                  </>
                )}
              </Box>
            ))}

            <Button
              type="submit"
              variant="contained"
              color="secondary"
              disabled={!chartImage}
            >
              Submit
            </Button>
          </Box>

          {loading && (
            <Box sx={{ marginTop: 4 }}>
              <Typography variant="body1" align="center" color="primary">
                Asking our AI Overlords for Ethical and Aesthetic Guidance...
              </Typography>
              <LinearProgress color="primary" />
            </Box>
          )}

          {!loading && response && (
            <Card sx={{ marginTop: 4, boxShadow: 2, borderRadius: 2 }}>
              <CardContent>
                <Typography variant="h6" component="div" sx={{ color: '#0078D4' }}>
                  Response
                </Typography>
                <Box sx={{ textAlign: 'left', fontFamily: 'Segoe UI', fontSize: '1rem', whiteSpace: 'pre-wrap' }}>
                  <ReactMarkdown>{typedResponse}</ReactMarkdown>
                </Box>
              </CardContent>
            </Card>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default FileUpload;