import React, { useState } from 'react';
import { Box, Typography, Grid, Card, CardContent, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { Inventory2, Warehouse, SwapHoriz, Download } from '@mui/icons-material';
import { downloadMlExportAsCsv } from '../utils/mlExport';

const Dashboard: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const navigate = useNavigate();
  const [exporting, setExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const handleExportCsv = async () => {
    setExporting(true);
    setExportMessage(null);
    try {
      const { rows } = await downloadMlExportAsCsv();
      setExportMessage(`Downloaded ${rows} rows.`);
      setTimeout(() => setExportMessage(null), 4000);
    } catch (e) {
      setExportMessage(e instanceof Error ? e.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.full_name || user?.email}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        ML-Enabled ERP Inventory Intelligence Platform
      </Typography>
      {exportMessage && (
        <Alert severity={exportMessage.startsWith('Downloaded') ? 'success' : 'error'} onClose={() => setExportMessage(null)} sx={{ mb: 2 }}>
          {exportMessage}
        </Alert>
      )}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/items')}>
            <CardContent>
              <Inventory2 color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">Items</Typography>
              <Typography color="text.secondary">Manage products and SKUs</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/warehouses')}>
            <CardContent>
              <Warehouse color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">Warehouses</Typography>
              <Typography color="text.secondary">Manage locations</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ cursor: 'pointer' }} onClick={() => navigate('/transactions')}>
            <CardContent>
              <SwapHoriz color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h6">Transactions</Typography>
              <Typography color="text.secondary">View and filter inventory transactions</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>ML & Anomaly Detection</Typography>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                Export ML-ready transaction data (CSV) for the pipeline, or run anomaly scoring on recent transactions.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="outlined" startIcon={<Download />} onClick={handleExportCsv} disabled={exporting}>
                  {exporting ? 'Exporting...' : 'Export ML data (CSV)'}
                </Button>
                <Button variant="contained" onClick={() => navigate('/anomaly')}>
                  Open Anomaly Detection
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
