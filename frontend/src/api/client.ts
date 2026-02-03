import axios from '../utils/axios';

// Items
export const itemsApi = {
  list: (params?: { skip?: number; limit?: number; category?: string }) =>
    axios.get<Array<Item>>('/items', { params }),
  get: (id: number) => axios.get<Item>(`/items/${id}`),
  create: (data: ItemCreate) => axios.post<Item>('/items', data),
  update: (id: number, data: Partial<ItemCreate>) => axios.patch<Item>(`/items/${id}`, data),
  delete: (id: number) => axios.delete(`/items/${id}`),
};

// Warehouses
export const warehousesApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    axios.get<Array<Warehouse>>('/warehouses', { params }),
  get: (id: number) => axios.get<Warehouse>(`/warehouses/${id}`),
  create: (data: WarehouseCreate) => axios.post<Warehouse>('/warehouses', data),
  update: (id: number, data: Partial<WarehouseCreate>) => axios.patch<Warehouse>(`/warehouses/${id}`, data),
  delete: (id: number) => axios.delete(`/warehouses/${id}`),
};

// Inventory transactions
export const transactionsApi = {
  list: (params?: { skip?: number; limit?: number; item_id?: number; warehouse_id?: number; transaction_type?: string }) =>
    axios.get<Array<InventoryTransaction>>('/inventory-transactions', { params }),
  get: (id: number) => axios.get<InventoryTransaction>(`/inventory-transactions/${id}`),
  create: (data: TransactionCreate) => axios.post<InventoryTransaction>('/inventory-transactions', data),
  update: (id: number, data: Partial<TransactionCreate>) => axios.patch<InventoryTransaction>(`/inventory-transactions/${id}`, data),
  delete: (id: number) => axios.delete(`/inventory-transactions/${id}`),
};

// ML
export interface MLExportRow {
  transaction_id: number;
  item_id: number;
  item_sku: string;
  item_category: string | null;
  warehouse_id: number;
  warehouse_code: string;
  transaction_type: string;
  quantity: number;
  unit_price: number | null;
  total_amount: number | null;
  reference_type: string | null;
  created_at: string;
  created_at_ts: number;
}

export interface MLExportResponse {
  rows: MLExportRow[];
  total_count: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export const mlApi = {
  score: (body: { transaction_ids?: number[]; transactions?: Record<string, unknown>[] }) =>
    axios.post<ScoreResponse>('/ml/score', body),
  export: (params?: { offset?: number; limit?: number }) =>
    axios.get<MLExportResponse>('/ml/export', { params }),
};

// Types
export interface Item {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  category: string | null;
  unit_cost: number | null;
  unit_of_measure: string;
  is_active: boolean;
  created_at: string;
}

export interface ItemCreate {
  sku: string;
  name: string;
  description?: string;
  category?: string;
  unit_cost?: number;
  unit_of_measure?: string;
}

export interface Warehouse {
  id: number;
  code: string;
  name: string;
  location: string | null;
  is_active: boolean;
  created_at: string;
}

export interface WarehouseCreate {
  code: string;
  name: string;
  location?: string;
}

export interface InventoryTransaction {
  id: number;
  item_id: number;
  warehouse_id: number;
  transaction_type: string;
  quantity: number;
  unit_price: number | null;
  total_amount: number | null;
  reference_type: string | null;
  reference_id: string | null;
  notes: string | null;
  created_by: number | null;
  created_at: string;
}

export interface TransactionCreate {
  item_id: number;
  warehouse_id: number;
  transaction_type: 'in' | 'out' | 'adjust' | 'transfer';
  quantity: number;
  unit_price?: number;
  reference_type?: string;
  reference_id?: string;
  notes?: string;
}

export interface ScoreResultItem {
  transaction_id: number;
  anomaly_score: number;
  cluster_id: number;
  is_anomaly: boolean;
}

export interface ScoreResponse {
  results: ScoreResultItem[];
  model_loaded: boolean;
}
