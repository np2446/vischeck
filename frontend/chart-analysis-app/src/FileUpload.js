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
  TextField,
  CssBaseline
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CloseIcon from '@mui/icons-material/Close';

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
  const backendUrl = process.env.BACKEND_URL + '/process-data' || 'localhost:8000/process-data'; 
  const [chartImage, setChartImage] = useState(null);
  const [chartDataCSV, setChartDataCSV] = useState(null);
  const [fullDataCSV, setFullDataCSV] = useState(null);
  const [additionalInfo, setAdditionalInfo] = useState('');
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
      // go through the response and remove any asterisks
      const responseText = response.replace(/\*/g, '');
      setTypedResponse(responseText);
    }
  }, [response]);

  const imageInputRef = useRef(null);
  const chartDataInputRef = useRef(null);
  const fullDataInputRef = useRef(null);

  const handleImageChange = e => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      setChartImage(reader.result.split(',')[1]);
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
      if (imageInputRef.current) imageInputRef.current.value = null;
    }
    if (field === 'chartData') {
      setChartDataCSV(null);
      setUploadStatus(prev => ({ ...prev, chartData: null }));
      if (chartDataInputRef.current) chartDataInputRef.current.value = null;
    }
    if (field === 'fullData') {
      setFullDataCSV(null);
      setUploadStatus(prev => ({ ...prev, fullData: null }));
      if (fullDataInputRef.current) fullDataInputRef.current.value = null;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!chartImage) return;

    setLoading(true);
    const chartData = chartDataCSV ? await parseCSV(chartDataCSV) : null;
    const fullData = fullDataCSV ? await parseCSV(fullDataCSV) : null;

    try {
      const response = await axios.post(backendUrl, {
        chart_data: chartData,
        full_data: fullData,
        chart_base64: chartImage,
        additional_info: additionalInfo 
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

          resolve(columns);
        },
        error: err => reject(err),
      });
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="xl">
        <Box sx={{
          display: 'flex',
          flexDirection: 'row',
          gap: 2,
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          paddingTop: 4
        }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ color: '#0078D4', fontWeight: 600 }}>
              VisCheck
            </Typography>
            <Typography variant="body1" align="left" sx={{ color: '#000000', marginBottom: 2 }}>
              Please upload the files below to receive AI-generated recommendations on the ethical and aesthetic aspects of your data visualization. <strong>At minimum, provide the chart image.</strong> Data files should be in CSV format. If your chart represents only a portion of a larger dataset, consider uploading the full dataset as well for a more in-depth analysis.
            </Typography>
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
              <TextField
                label="Additional Information"
                variant="outlined"
                multiline
                rows={4}
                value={additionalInfo}
                onChange={(e) => setAdditionalInfo(e.target.value)}
                placeholder="Provide any additional context or instructions for the AI here..."
              />
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
          </Box>
          {!loading && response && (
            <Card sx={{ flex: 1, boxShadow: 2, borderRadius: 2 }}>
              <CardContent>
                <Typography variant="h6" component="div" sx={{ color: '#0078D4' }}>
                  Response
                </Typography>
                <Box sx={{ textAlign: 'left', fontFamily: 'Segoe UI', fontSize: '1rem', whiteSpace: 'pre-wrap' }}>
                  <Typography>{typedResponse}</Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default FileUpload;