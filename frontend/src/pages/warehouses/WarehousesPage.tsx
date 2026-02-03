import React, { useEffect, useState, useMemo } from 'react';
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  TablePagination,
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { warehousesApi, type Warehouse, type WarehouseCreate } from '../../api/client';

const WarehousesPage: React.FC = () => {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Warehouse | null>(null);
  const [form, setForm] = useState<WarehouseCreate>({ code: '', name: '', location: '' });
  const [saving, setSaving] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  const paginatedWarehouses = useMemo(() => {
    const start = page * rowsPerPage;
    return warehouses.slice(start, start + rowsPerPage);
  }, [warehouses, page, rowsPerPage]);

  const fetchWarehouses = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await warehousesApi.list({ limit: 500 });
      setWarehouses(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load warehouses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ code: '', name: '', location: '' });
    setDialogOpen(true);
  };

  const openEdit = (wh: Warehouse) => {
    setEditing(wh);
    setForm({ code: wh.code, name: wh.name, location: wh.location ?? '' });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        await warehousesApi.update(editing.id, { name: form.name, location: form.location || undefined });
      } else {
        await warehousesApi.create(form);
      }
      setDialogOpen(false);
      fetchWarehouses();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this warehouse?')) return;
    try {
      await warehousesApi.delete(id);
      fetchWarehouses();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed');
    }
  };

  const handleChangePage = (_: unknown, newPage: number) => setPage(newPage);
  const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(e.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Warehouses</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
          Add Warehouse
        </Button>
      </Box>
      {error && <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? (
        <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedWarehouses.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.code}</TableCell>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.location ?? '—'}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => openEdit(row)}><EditIcon /></IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={warehouses.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? 'Edit Warehouse' : 'New Warehouse'}</DialogTitle>
        <DialogContent>
          <TextField margin="dense" label="Code" fullWidth required value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} disabled={!!editing} />
          <TextField margin="dense" label="Name" fullWidth required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <TextField margin="dense" label="Location" fullWidth value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving || !form.code || !form.name}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WarehousesPage;
