import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Collapse,
  Grid,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import WarningIcon from '@mui/icons-material/Warning';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { api } from '../../services/api';
import XAIResultPanel from '../XAI/XAIResultPanel';

interface SLARecord {
  sla_id: string;
  intent_id: string;
  service_type: 'eMBB' | 'URLLC' | 'mMTC';
  decision: 'ACCEPT' | 'REJECT' | 'RENEG';
  timestamp: string;
  tx_hash?: string;
  block_number?: number;
  xai?: {
    risk_score: number;
    risk_level: string;
    confidence: number;
    viability_score: number;
    justification: string;
    domains_evaluated: string[];
  };
}

const COLORS = ['#4caf50', '#f44336', '#ff9800'];
const TYPE_COLORS = ['#2196f3', '#9c27b0', '#00bcd4'];

interface SLARowProps {
  sla: SLARecord;
}

const SLARow: React.FC<SLARowProps> = ({ sla }) => {
  const [open, setOpen] = useState(false);

  const getDecisionIcon = () => {
    switch (sla.decision) {
      case 'ACCEPT':
        return <CheckCircleIcon color="success" />;
      case 'REJECT':
        return <CancelIcon color="error" />;
      case 'RENEG':
        return <WarningIcon color="warning" />;
      default:
        return null;
    }
  };

  const getDecisionColor = () => {
    switch (sla.decision) {
      case 'ACCEPT':
        return 'success';
      case 'REJECT':
        return 'error';
      case 'RENEG':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            {sla.sla_id.slice(0, 16)}...
          </Typography>
        </TableCell>
        <TableCell>
          <Chip label={sla.service_type} size="small" color="primary" variant="outlined" />
        </TableCell>
        <TableCell>
          <Chip
            icon={getDecisionIcon()}
            label={sla.decision}
            color={getDecisionColor() as any}
            size="small"
          />
        </TableCell>
        <TableCell>
          {sla.xai && (
            <Chip
              label={`${(sla.xai.risk_score * 100).toFixed(0)}%`}
              size="small"
              color={
                sla.xai.risk_level === 'low'
                  ? 'success'
                  : sla.xai.risk_level === 'medium'
                  ? 'warning'
                  : 'error'
              }
              variant="outlined"
            />
          )}
        </TableCell>
        <TableCell>{new Date(sla.timestamp).toLocaleString()}</TableCell>
        <TableCell>
          {sla.block_number ? (
            <Chip label={`#${sla.block_number}`} size="small" variant="outlined" />
          ) : (
            '-'
          )}
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 2 }}>
              {sla.xai && (
                <XAIResultPanel
                  slaId={sla.sla_id}
                  xai={{
                    decision: sla.decision,
                    risk_score: sla.xai.risk_score,
                    risk_level: sla.xai.risk_level as any,
                    confidence: sla.xai.confidence,
                    viability_score: sla.xai.viability_score,
                    justification: sla.xai.justification,
                    domains_evaluated: sla.xai.domains_evaluated,
                  }}
                  txHash={sla.tx_hash}
                  blockNumber={sla.block_number}
                />
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

const SLAListPanel: React.FC = () => {
  const [slas, setSlas] = useState<SLARecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSLAs();
  }, []);

  const loadSLAs = async () => {
    try {
      setLoading(true);
      // Try to get from Kafka events or backend
      const response = await api.get('/api/v1/sla/history');
      setSlas(response.data.slas || []);
    } catch (error) {
      console.error('Error loading SLAs:', error);
      // Fallback to mock data for development
      setSlas([
        {
          sla_id: 'sla-demo-001',
          intent_id: 'intent-demo-001',
          service_type: 'eMBB',
          decision: 'ACCEPT',
          timestamp: new Date().toISOString(),
          tx_hash: '0x3d84417bd1c9c08fcedd171aaaca9950bbdfb0612e05a7520ba61e4902074a3b',
          block_number: 101,
          xai: {
            risk_score: 0.25,
            risk_level: 'low',
            confidence: 0.99,
            viability_score: 0.85,
            justification: 'SLA eMBB aceito. ML prevê risco BAIXO (score: 0.25). SLOs viáveis. Dominios: RAN, Transporte.',
            domains_evaluated: ['RAN', 'Transport', 'Core'],
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate statistics
  const stats = {
    total: slas.length,
    accept: slas.filter((s) => s.decision === 'ACCEPT').length,
    reject: slas.filter((s) => s.decision === 'REJECT').length,
    reneg: slas.filter((s) => s.decision === 'RENEG').length,
    embb: slas.filter((s) => s.service_type === 'eMBB').length,
    urllc: slas.filter((s) => s.service_type === 'URLLC').length,
    mmtc: slas.filter((s) => s.service_type === 'mMTC').length,
  };

  const statusData = [
    { name: 'ACCEPT', value: stats.accept },
    { name: 'REJECT', value: stats.reject },
    { name: 'RENEG', value: stats.reneg },
  ].filter((d) => d.value > 0);

  const typeData = [
    { name: 'eMBB', value: stats.embb },
    { name: 'URLLC', value: stats.urllc },
    { name: 'mMTC', value: stats.mmtc },
  ].filter((d) => d.value > 0);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        SLA Overview
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography variant="h3" align="center">
                {stats.total}
              </Typography>
              <Typography variant="body2" align="center" color="text.secondary">
                Total SLAs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card sx={{ borderLeft: '4px solid', borderLeftColor: 'success.main' }}>
            <CardContent>
              <Typography variant="h3" align="center" color="success.main">
                {stats.accept}
              </Typography>
              <Typography variant="body2" align="center" color="text.secondary">
                Accepted
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card sx={{ borderLeft: '4px solid', borderLeftColor: 'error.main' }}>
            <CardContent>
              <Typography variant="h3" align="center" color="error.main">
                {stats.reject}
              </Typography>
              <Typography variant="body2" align="center" color="text.secondary">
                Rejected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card sx={{ borderLeft: '4px solid', borderLeftColor: 'warning.main' }}>
            <CardContent>
              <Typography variant="h3" align="center" color="warning.main">
                {stats.reneg}
              </Typography>
              <Typography variant="body2" align="center" color="text.secondary">
                Renegotiation
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SLAs by Decision
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SLAs by Service Type
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={typeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#2196f3">
                    {typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={TYPE_COLORS[index % TYPE_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* SLA Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            SLA History
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell />
                  <TableCell>SLA ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Decision</TableCell>
                  <TableCell>Risk Score</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Block</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {slas.map((sla) => (
                  <SLARow key={sla.sla_id} sla={sla} />
                ))}
                {slas.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary">No SLAs found</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SLAListPanel;
