import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Layout from './components/Layout';
import TenantPortal from './components/TenantPortal/TenantPortal';
import Monitoring from './components/Monitoring/Monitoring';
import Administration from './components/Administration/Administration';
import SlicesState from './components/SlicesState/SlicesState';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/tenant" replace />} />
            <Route path="/tenant" element={<TenantPortal />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/administration" element={<Administration />} />
            <Route path="/slices" element={<SlicesState />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;

