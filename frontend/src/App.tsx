import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';

import ErrorBoundary from './components/ErrorBoundary';
import LoginForm from './components/auth/LoginForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import ItemsPage from './pages/items/ItemsPage';
import WarehousesPage from './pages/warehouses/WarehousesPage';
import TransactionsPage from './pages/transactions/TransactionsPage';
import AnomalyPage from './pages/anomaly/AnomalyPage';
import theme from './theme';
import store from './store';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="items" element={<ItemsPage />} />
        <Route path="warehouses" element={<WarehousesPage />} />
        <Route path="transactions" element={<TransactionsPage />} />
        <Route path="anomaly" element={<AnomalyPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </ThemeProvider>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;
