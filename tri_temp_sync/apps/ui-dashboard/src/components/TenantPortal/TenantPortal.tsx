import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { api } from '../../services/api';

interface SLARequest {
  id: string;
  tenant_id: string;
  service_type: 'eMBB' | 'URLLC' | 'mMTC';
  status: 'pending' | 'accepted' | 'rejected' | 'active';
  created_at: string;
  sla_requirements: {
    latency?: string;
    throughput?: string;
    reliability?: number;
  };
}

const TenantPortal: React.FC = () => {
  const [requests, setRequests] = useState<SLARequest[]>([]);
  const [formData, setFormData] = useState({
    service_type: 'eMBB' as 'eMBB' | 'URLLC' | 'mMTC',
    latency: '',
    throughput: '',
    reliability: '',
  });
  const [openForm, setOpenForm] = useState(false);

  useEffect(() => {
    loadRequests();
    // WebSocket para atualizações em tempo real
    const ws = new WebSocket('ws://localhost:8080/ws/tenant');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'request_update') {
        loadRequests();
      }
    };
    return () => ws.close();
  }, []);

  const loadRequests = async () => {
    try {
      const data = await api.get('/api/v1/tenant/requests');
      setRequests(data.data);
    } catch (error) {
      console.error('Error loading requests:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const intent = {
        intent_id: `intent-${Date.now()}`,
        tenant_id: 'tenant-001', // Em produção, obter do contexto de autenticação
        service_type: formData.service_type,
        sla_requirements: {
          latency: formData.latency || undefined,
          throughput: formData.throughput || undefined,
          reliability: formData.reliability ? parseFloat(formData.reliability) : undefined,
        },
      };

      await api.post('/api/v1/intents', intent);
      setOpenForm(false);
      setFormData({ service_type: 'eMBB', latency: '', throughput: '', reliability: '' });
      loadRequests();
    } catch (error) {
      console.error('Error creating request:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
      case 'active':
        return 'success';
      case 'rejected':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Tenant Portal</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenForm(!openForm)}
        >
          Nova Requisição SLA
        </Button>
      </Box>

      {openForm && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Nova Requisição de SLA
            </Typography>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Tipo de Slice</InputLabel>
                    <Select
                      value={formData.service_type}
                      onChange={(e) =>
                        setFormData({ ...formData, service_type: e.target.value as any })
                      }
                    >
                      <MenuItem value="eMBB">eMBB (Enhanced Mobile Broadband)</MenuItem>
                      <MenuItem value="URLLC">URLLC (Ultra-Reliable Low-Latency)</MenuItem>
                      <MenuItem value="mMTC">mMTC (massive Machine-Type)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Latência (ex: 10ms)"
                    value={formData.latency}
                    onChange={(e) => setFormData({ ...formData, latency: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Throughput (ex: 100Mbps)"
                    value={formData.throughput}
                    onChange={(e) => setFormData({ ...formData, throughput: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Confiabilidade (ex: 0.999)"
                    value={formData.reliability}
                    onChange={(e) => setFormData({ ...formData, reliability: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button type="submit" variant="contained">
                      Enviar Requisição
                    </Button>
                    <Button variant="outlined" onClick={() => setOpenForm(false)}>
                      Cancelar
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Requisições de SLA
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Latência</TableCell>
                  <TableCell>Throughput</TableCell>
                  <TableCell>Data</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>{request.id}</TableCell>
                    <TableCell>
                      <Chip label={request.service_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={request.status}
                        color={getStatusColor(request.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{request.sla_requirements.latency || '-'}</TableCell>
                    <TableCell>{request.sla_requirements.throughput || '-'}</TableCell>
                    <TableCell>{new Date(request.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TenantPortal;

