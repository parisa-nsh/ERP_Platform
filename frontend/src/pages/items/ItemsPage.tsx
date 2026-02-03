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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TablePagination,
} from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { itemsApi, type Item, type ItemCreate } from '../../api/client';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50, 100];

const ItemsPage: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Item | null>(null);
  const [form, setForm] = useState<ItemCreate>({
    sku: '',
    name: '',
    description: '',
    category: '',
    unit_of_measure: 'EA',
  });
  const [saving, setSaving] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await itemsApi.list({ limit: 2000 });
      setItems(data);
      setPage(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const categories = useMemo(() => {
    const set = new Set<string>();
    items.forEach((i) => i.category && set.add(i.category));
    return Array.from(set).sort();
  }, [items]);

  const filteredItems = useMemo(() => {
    if (!categoryFilter) return items;
    return items.filter((i) => i.category === categoryFilter);
  }, [items, categoryFilter]);

  const paginatedItems = useMemo(() => {
    const start = page * rowsPerPage;
    return filteredItems.slice(start, start + rowsPerPage);
  }, [filteredItems, page, rowsPerPage]);

  const openCreate = () => {
    setEditing(null);
    setForm({ sku: '', name: '', description: '', category: '', unit_of_measure: 'EA' });
    setDialogOpen(true);
  };

  const openEdit = (item: Item) => {
    setEditing(item);
    setForm({
      sku: item.sku,
      name: item.name,
      description: item.description ?? '',
      category: item.category ?? '',
      unit_of_measure: item.unit_of_measure,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        await itemsApi.update(editing.id, {
          name: form.name,
          description: form.description || undefined,
          category: form.category || undefined,
          unit_of_measure: form.unit_of_measure,
        });
      } else {
        await itemsApi.create({
          ...form,
          unit_cost: form.unit_cost ?? undefined,
        });
      }
      setDialogOpen(false);
      fetchItems();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this item?')) return;
    try {
      await itemsApi.delete(id);
      fetchItems();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed');
    }
  };

  const handleChangePage = (_: unknown, newPage: number) => setPage(newPage);
  const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(e.target.value, 10));
    setPage(0);
  };

  useEffect(() => {
    setPage(0);
  }, [categoryFilter]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h5">Items</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={categoryFilter}
              label="Category"
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              {categories.map((c) => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate}>
            Add Item
          </Button>
        </Box>
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
                  <TableCell>SKU</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Unit cost</TableCell>
                  <TableCell align="right">UoM</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedItems.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.sku}</TableCell>
                    <TableCell>{row.name}</TableCell>
                    <TableCell>{row.category ?? '—'}</TableCell>
                    <TableCell align="right">{row.unit_cost != null ? Number(row.unit_cost).toFixed(2) : '—'}</TableCell>
                    <TableCell align="right">{row.unit_of_measure}</TableCell>
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
            count={filteredItems.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
          />
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? 'Edit Item' : 'New Item'}</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="SKU"
            fullWidth
            required
            value={form.sku}
            onChange={(e) => setForm({ ...form, sku: e.target.value })}
            disabled={!!editing}
          />
          <TextField margin="dense" label="Name" fullWidth required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <TextField margin="dense" label="Description" fullWidth value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <TextField margin="dense" label="Category" fullWidth value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          <TextField margin="dense" label="Unit of measure" fullWidth value={form.unit_of_measure} onChange={(e) => setForm({ ...form, unit_of_measure: e.target.value })} />
          {!editing && (
            <TextField margin="dense" label="Unit cost" type="number" fullWidth value={form.unit_cost ?? ''} onChange={(e) => setForm({ ...form, unit_cost: e.target.value ? Number(e.target.value) : undefined })} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving || !form.sku || !form.name}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ItemsPage;
