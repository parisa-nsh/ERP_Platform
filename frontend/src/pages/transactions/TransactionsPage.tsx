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
import { transactionsApi, itemsApi, warehousesApi, type InventoryTransaction, type TransactionCreate, type Item, type Warehouse } from '../../api/client';

const TX_TYPES = ['in', 'out', 'adjust', 'transfer'] as const;

const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<InventoryTransaction[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<InventoryTransaction | null>(null);
  const [form, setForm] = useState<TransactionCreate>({
    item_id: 0,
    warehouse_id: 0,
    transaction_type: 'in',
    quantity: 0,
  });
  const [saving, setSaving] = useState(false);
  const [filterItemId, setFilterItemId] = useState<number | ''>('');
  const [filterWarehouseId, setFilterWarehouseId] = useState<number | ''>('');
  const [filterType, setFilterType] = useState<string>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const [txRes, itemsRes, whRes] = await Promise.all([
        transactionsApi.list({
          limit: 2000,
          item_id: filterItemId || undefined,
          warehouse_id: filterWarehouseId || undefined,
          transaction_type: filterType || undefined,
        }),
        itemsApi.list({ limit: 500 }),
        warehousesApi.list({ limit: 500 }),
      ]);
      setTransactions(txRes.data);
      setItems(itemsRes.data);
      setWarehouses(whRes.data);
      setPage(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [filterItemId, filterWarehouseId, filterType]);

  const paginatedTransactions = useMemo(() => {
    const start = page * rowsPerPage;
    return transactions.slice(start, start + rowsPerPage);
  }, [transactions, page, rowsPerPage]);

  const handleChangePage = (_: unknown, newPage: number) => setPage(newPage);
  const handleChangeRowsPerPage = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(e.target.value, 10));
    setPage(0);
  };

  const openCreate = () => {
    setEditing(null);
    setForm({
      item_id: items[0]?.id ?? 0,
      warehouse_id: warehouses[0]?.id ?? 0,
      transaction_type: 'in',
      quantity: 0,
      unit_price: undefined,
    });
    setDialogOpen(true);
  };

  const openEdit = (tx: InventoryTransaction) => {
    setEditing(tx);
    setForm({
      item_id: tx.item_id,
      warehouse_id: tx.warehouse_id,
      transaction_type: tx.transaction_type as TransactionCreate['transaction_type'],
      quantity: Number(tx.quantity),
      unit_price: tx.unit_price != null ? Number(tx.unit_price) : undefined,
      notes: tx.notes ?? undefined,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        await transactionsApi.update(editing.id, {
          quantity: form.quantity,
          unit_price: form.unit_price,
          notes: form.notes,
        });
      } else {
        await transactionsApi.create({
          ...form,
          item_id: form.item_id || items[0]?.id!,
          warehouse_id: form.warehouse_id || warehouses[0]?.id!,
        });
      }
      setDialogOpen(false);
      fetchTransactions();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this transaction?')) return;
    try {
      await transactionsApi.delete(id);
      fetchTransactions();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed');
    }
  };

  const itemMap = Object.fromEntries(items.map((i) => [i.id, i]));
  const whMap = Object.fromEntries(warehouses.map((w) => [w.id, w]));

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h5">Inventory Transactions</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Item</InputLabel>
            <Select value={filterItemId} label="Item" onChange={(e) => setFilterItemId(e.target.value === '' ? '' : Number(e.target.value))}>
              <MenuItem value="">All</MenuItem>
              {items.map((i) => (
                <MenuItem key={i.id} value={i.id}>{i.sku}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Warehouse</InputLabel>
            <Select value={filterWarehouseId} label="Warehouse" onChange={(e) => setFilterWarehouseId(e.target.value === '' ? '' : Number(e.target.value))}>
              <MenuItem value="">All</MenuItem>
              {warehouses.map((w) => (
                <MenuItem key={w.id} value={w.id}>{w.code}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select value={filterType} label="Type" onChange={(e) => setFilterType(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              {TX_TYPES.map((t) => (
                <MenuItem key={t} value={t}>{t}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate} disabled={items.length === 0 || warehouses.length === 0}>
            Add Transaction
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
                  <TableCell>ID</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Warehouse</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Qty</TableCell>
                  <TableCell align="right">Unit price</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedTransactions.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.id}</TableCell>
                  <TableCell>{itemMap[row.item_id]?.name ?? row.item_id}</TableCell>
                  <TableCell>{whMap[row.warehouse_id]?.code ?? row.warehouse_id}</TableCell>
                  <TableCell>{row.transaction_type}</TableCell>
                  <TableCell align="right">{Number(row.quantity)}</TableCell>
                  <TableCell align="right">{row.unit_price != null ? Number(row.unit_price).toFixed(2) : '—'}</TableCell>
                  <TableCell>{new Date(row.created_at).toLocaleString()}</TableCell>
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
            count={transactions.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? 'Edit Transaction' : 'New Transaction'}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="dense" required>
            <InputLabel>Item</InputLabel>
            <Select
              value={form.item_id || ''}
              label="Item"
              onChange={(e) => setForm({ ...form, item_id: Number(e.target.value) })}
              disabled={!!editing}
            >
              {items.map((i) => (
                <MenuItem key={i.id} value={i.id}>{i.sku} – {i.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="dense" required>
            <InputLabel>Warehouse</InputLabel>
            <Select
              value={form.warehouse_id || ''}
              label="Warehouse"
              onChange={(e) => setForm({ ...form, warehouse_id: Number(e.target.value) })}
              disabled={!!editing}
            >
              {warehouses.map((w) => (
                <MenuItem key={w.id} value={w.id}>{w.code} – {w.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="dense" required>
            <InputLabel>Type</InputLabel>
            <Select
              value={form.transaction_type}
              label="Type"
              onChange={(e) => setForm({ ...form, transaction_type: e.target.value as TransactionCreate['transaction_type'] })}
              disabled={!!editing}
            >
              {TX_TYPES.map((t) => (
                <MenuItem key={t} value={t}>{t}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField margin="dense" label="Quantity" type="number" fullWidth required value={form.quantity || ''} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} />
          <TextField margin="dense" label="Unit price" type="number" fullWidth value={form.unit_price ?? ''} onChange={(e) => setForm({ ...form, unit_price: e.target.value ? Number(e.target.value) : undefined })} />
          <TextField margin="dense" label="Notes" fullWidth multiline value={form.notes ?? ''} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving || !form.item_id || !form.warehouse_id || form.quantity <= 0}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TransactionsPage;
