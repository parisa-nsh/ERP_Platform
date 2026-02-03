import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Refresh as RefreshIcon, Download as DownloadIcon } from '@mui/icons-material';
import { transactionsApi, mlApi, type ScoreResultItem } from '../../api/client';
import { downloadMlExportAsCsv } from '../../utils/mlExport';
import { getApiErrorMessage } from '../../utils/apiError';

const SCORE_LIMIT_OPTIONS = [50, 100, 200, 500];

const AnomalyPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ScoreResultItem[]>([]);
  const [modelLoaded, setModelLoaded] = useState<boolean | null>(null);
  const [scoreLimit, setScoreLimit] = useState(100);
  const [exporting, setExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const runScore = async () => {
    setLoading(true);
    setError(null);
    setResults([]);
    setModelLoaded(null);
    try {
      const { data: txList } = await transactionsApi.list({ limit: scoreLimit });
      const ids = txList.map((t) => t.id);
      if (ids.length === 0) {
        setError('No transactions to score. Add some transactions first.');
        setLoading(false);
        return;
      }
      const { data } = await mlApi.score({ transaction_ids: ids });
      setResults(data.results);
      setModelLoaded(data.model_loaded);
    } catch (e: unknown) {
      const msg = getApiErrorMessage(e, 'Request failed');
      setError(msg);
      if (msg.toLowerCase().includes('model not loaded')) {
        setModelLoaded(false);
      }
    } finally {
      setLoading(false);
    }
  };

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h5">Anomaly Detection</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <InputLabel>Limit</InputLabel>
            <Select value={scoreLimit} label="Limit" onChange={(e) => setScoreLimit(Number(e.target.value))}>
              {SCORE_LIMIT_OPTIONS.map((n) => (
                <MenuItem key={n} value={n}>{n}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<RefreshIcon />} onClick={runScore} disabled={loading}>
            {loading ? 'Scoring...' : 'Score recent'}
          </Button>
          <Button variant="outlined" startIcon={<DownloadIcon />} onClick={handleExportCsv} disabled={exporting}>
            {exporting ? 'Exporting...' : 'Export ML data (CSV)'}
          </Button>
        </Box>
      </Box>
      {exportMessage && (
        <Alert severity={exportMessage.startsWith('Downloaded') ? 'success' : 'error'} onClose={() => setExportMessage(null)} sx={{ mb: 2 }}>
          {exportMessage}
        </Alert>
      )}
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        Score the most recent transactions (limit above). Export downloads ML-ready data for the feature pipeline. Requires backend model (ML_MODEL_DIR) for scoring.
      </Typography>
      {modelLoaded === false && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          ML model is not loaded. Train the pipeline and set ML_MODEL_DIR on the backend, then restart the API.
        </Alert>
      )}
      {error && <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>{error}</Alert>}
      {loading && (
        <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
      )}
      {!loading && results.length > 0 && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Anomalies: {results.filter((r) => r.is_anomaly).length} of {results.length}
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Transaction ID</TableCell>
                  <TableCell align="right">Anomaly score</TableCell>
                  <TableCell>Cluster</TableCell>
                  <TableCell>Flag</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((r) => (
                  <TableRow key={r.transaction_id} sx={{ bgcolor: r.is_anomaly ? 'action.hover' : undefined }}>
                    <TableCell>{r.transaction_id}</TableCell>
                    <TableCell align="right">{r.anomaly_score.toFixed(4)}</TableCell>
                    <TableCell>{r.cluster_id}</TableCell>
                    <TableCell>
                      {r.is_anomaly ? <Chip label="Anomaly" color="error" size="small" /> : <Chip label="Normal" size="small" variant="outlined" />}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </Box>
  );
};

export default AnomalyPage;
