import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { api } from '../../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const Administration: React.FC = () => {
  const [value, setValue] = useState(0);
  const [tenants, setTenants] = useState<any[]>([]);
  const [modules, setModules] = useState<any[]>([]);
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    loadTenants();
    loadModules();
  }, []);

  const loadTenants = async () => {
    try {
      const response = await api.get('/api/v1/admin/tenants');
      setTenants(response.data);
    } catch (error) {
      console.error('Error loading tenants:', error);
    }
  };

  const loadModules = async () => {
    try {
      const response = await api.get('/api/v1/admin/modules');
      setModules(response.data);
    } catch (error) {
      console.error('Error loading modules:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Administração
      </Typography>

      <Card>
        <Tabs value={value} onChange={(e, newValue) => setValue(newValue)}>
          <Tab label="Tenants" />
          <Tab label="Módulos" />
          <Tab label="Configurações" />
        </Tabs>

        <TabPanel value={value} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button variant="contained" onClick={() => setOpenDialog(true)}>
              Novo Tenant
            </Button>
          </Box>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Nome</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tenants.map((tenant) => (
                  <TableRow key={tenant.id}>
                    <TableCell>{tenant.id}</TableCell>
                    <TableCell>{tenant.name}</TableCell>
                    <TableCell>{tenant.email}</TableCell>
                    <TableCell>{tenant.status}</TableCell>
                    <TableCell>
                      <Button size="small">Editar</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={value} index={1}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Módulo</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Versão</TableCell>
                  <TableCell>Configuração</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {modules.map((module) => (
                  <TableRow key={module.name}>
                    <TableCell>{module.name}</TableCell>
                    <TableCell>{module.status}</TableCell>
                    <TableCell>{module.version}</TableCell>
                    <TableCell>
                      <Button size="small">Configurar</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={value} index={2}>
          <Typography>Configurações gerais do sistema</Typography>
        </TabPanel>
      </Card>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Novo Tenant</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Nome" margin="normal" />
          <TextField fullWidth label="Email" margin="normal" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button variant="contained" onClick={() => setOpenDialog(false)}>
            Criar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Administration;

