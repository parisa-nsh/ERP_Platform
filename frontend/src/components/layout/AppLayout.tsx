import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import axios from '../../utils/axios';
import { useDispatch, useSelector } from 'react-redux';
import { logout, setUser } from '../../store/slices/authSlice';
import type { User } from '../../store/slices/authSlice';
import { RootState } from '../../store';
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  AppBar,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Inventory2 as InventoryIcon,
  Warehouse as WarehouseIcon,
  SwapHoriz as TransactionIcon,
  WarningAmber as AnomalyIcon,
  Dashboard as DashboardIcon,
  Menu as MenuIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';

const DRAWER_WIDTH = 240;

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
  { path: '/items', label: 'Items', icon: <InventoryIcon /> },
  { path: '/warehouses', label: 'Warehouses', icon: <WarehouseIcon /> },
  { path: '/transactions', label: 'Transactions', icon: <TransactionIcon /> },
  { path: '/anomaly', label: 'Anomaly Detection', icon: <AnomalyIcon /> },
];

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const { user, token } = useSelector((state: RootState) => state.auth);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    if (token && !user) {
      axios.get<User>('/auth/me').then(({ data }) => dispatch(setUser(data))).catch(() => dispatch(logout()));
    }
  }, [token, user, dispatch]);

  const handleNav = (path: string) => {
    navigate(path);
    if (isMobile) setDrawerOpen(false);
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const drawer = (
    <Box sx={{ pt: 2 }}>
      <Typography variant="h6" sx={{ px: 2, pb: 2, fontWeight: 600 }}>
        ERP Inventory
      </Typography>
      <List>
        {navItems.map(({ path, label, icon }) => (
          <ListItemButton
            key={path}
            selected={location.pathname === path}
            onClick={() => handleNav(path)}
          >
            <ListItemIcon>{icon}</ListItemIcon>
            <ListItemText primary={label} />
          </ListItemButton>
        ))}
        <ListItemButton onClick={handleLogout} sx={{ mt: 1 }}>
          <ListItemIcon><LogoutIcon /></ListItemIcon>
          <ListItemText primary="Log out" />
        </ListItemButton>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            ML-Enabled ERP Inventory
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? 'temporary' : 'permanent'}
          open={isMobile ? drawerOpen : true}
          onClose={() => setDrawerOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              top: { md: 64 },
              height: { md: 'calc(100% - 64px)' },
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default AppLayout;
