import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { api } from '../../services/api';

interface Slice {
  id: string;
  type: string;
  status: string;
  resources: {
    cpu: string;
    memory: string;
    bandwidth: string;
  };
  health: string;
}

interface Module {
  name: string;
  status: string;
  health: string;
  last_update: string;
}

const SlicesState: React.FC = () => {
  const [slices, setSlices] = useState<Slice[]>([]);
  const [modules, setModules] = useState<Module[]>([]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/slices');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'slice_update') {
        loadData();
      }
    };
    return () => ws.close();
  }, []);

  const loadData = async () => {
    try {
      const [slicesRes, modulesRes] = await Promise.all([
        api.get('/api/v1/slices'),
        api.get('/api/v1/modules/status'),
      ]);
      setSlices(slicesRes.data);
      setModules(modulesRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Slices & Estado dos Módulos
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Network Slices
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>CPU</TableCell>
                      <TableCell>Memória</TableCell>
                      <TableCell>Bandwidth</TableCell>
                      <TableCell>Health</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {slices.map((slice) => (
                      <TableRow key={slice.id}>
                        <TableCell>{slice.id}</TableCell>
                        <TableCell>
                          <Chip label={slice.type} size="small" />
                        </TableCell>
                        <TableCell>{slice.status}</TableCell>
                        <TableCell>{slice.resources.cpu}</TableCell>
                        <TableCell>{slice.resources.memory}</TableCell>
                        <TableCell>{slice.resources.bandwidth}</TableCell>
                        <TableCell>
                          <Chip
                            label={slice.health}
                            color={getHealthColor(slice.health) as any}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Estado dos Módulos
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Módulo</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Health</TableCell>
                      <TableCell>Última Atualização</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {modules.map((module) => (
                      <TableRow key={module.name}>
                        <TableCell>{module.name}</TableCell>
                        <TableCell>{module.status}</TableCell>
                        <TableCell>
                          <Chip
                            label={module.health}
                            color={getHealthColor(module.health) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{new Date(module.last_update).toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SlicesState;

