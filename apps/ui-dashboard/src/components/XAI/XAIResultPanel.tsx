import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  Paper,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';

interface XAIData {
  decision: 'ACCEPT' | 'REJECT' | 'RENEG';
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high';
  confidence: number;
  viability_score: number;
  justification: string;
  domains_evaluated: string[];
  features?: {
    name: string;
    importance: number;
    value: number;
  }[];
}

interface XAIResultPanelProps {
  slaId: string;
  xai: XAIData;
  txHash?: string;
  blockNumber?: number;
}

const XAIResultPanel: React.FC<XAIResultPanelProps> = ({ slaId, xai, txHash, blockNumber }) => {
  const getDecisionIcon = () => {
    switch (xai.decision) {
      case 'ACCEPT':
        return <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main' }} />;
      case 'REJECT':
        return <CancelIcon sx={{ fontSize: 40, color: 'error.main' }} />;
      case 'RENEG':
        return <WarningIcon sx={{ fontSize: 40, color: 'warning.main' }} />;
      default:
        return <InfoIcon sx={{ fontSize: 40 }} />;
    }
  };

  const getDecisionColor = () => {
    switch (xai.decision) {
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

  const getRiskColor = () => {
    switch (xai.risk_level) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card sx={{ mt: 2, border: `2px solid`, borderColor: `${getDecisionColor()}.main` }}>
      <CardContent>
        {/* Header with Decision */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {getDecisionIcon()}
          <Box sx={{ ml: 2 }}>
            <Typography variant="h5">
              Decision: <Chip label={xai.decision} color={getDecisionColor() as any} />
            </Typography>
            <Typography variant="body2" color="text.secondary">
              SLA ID: {slaId}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* XAI Metrics */}
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <InfoIcon sx={{ mr: 1 }} /> XAI - Explainability
        </Typography>

        <Grid container spacing={2}>
          {/* Risk Score */}
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Risk Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Box sx={{ flexGrow: 1, mr: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={xai.risk_score * 100}
                    color={getRiskColor() as any}
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Typography variant="h6">
                  {(xai.risk_score * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Chip
                label={xai.risk_level.toUpperCase()}
                color={getRiskColor() as any}
                size="small"
                sx={{ mt: 1 }}
              />
            </Paper>
          </Grid>

          {/* Confidence */}
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Confidence
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Box sx={{ flexGrow: 1, mr: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={xai.confidence * 100}
                    color="primary"
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Typography variant="h6">
                  {(xai.confidence * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Viability Score */}
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Viability Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Box sx={{ flexGrow: 1, mr: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={xai.viability_score * 100}
                    color={xai.viability_score > 0.5 ? 'success' : 'warning'}
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Typography variant="h6">
                  {(xai.viability_score * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Domains Evaluated */}
          <Grid item xs={12} sm={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Domains Evaluated
              </Typography>
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {xai.domains_evaluated.map((domain) => (
                  <Chip
                    key={domain}
                    label={domain}
                    size="small"
                    icon={<CheckCircleIcon />}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Justification */}
        <Typography variant="h6" gutterBottom>
          Justification
        </Typography>
        <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
          <Typography variant="body1">{xai.justification}</Typography>
        </Paper>

        {/* Feature Importance (if available) */}
        {xai.features && xai.features.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Feature Importance
            </Typography>
            <List>
              {xai.features.slice(0, 5).map((feature) => (
                <ListItem key={feature.name} divider>
                  <ListItemText
                    primary={feature.name}
                    secondary={`Value: ${feature.value.toFixed(2)}`}
                  />
                  <Box sx={{ width: 150, mr: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={feature.importance * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  <Typography variant="body2">
                    {(feature.importance * 100).toFixed(1)}%
                  </Typography>
                </ListItem>
              ))}
            </List>
          </>
        )}

        {/* Blockchain Info */}
        {txHash && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Blockchain Confirmation
            </Typography>
            <Paper sx={{ p: 2 }}>
              <Typography variant="body2" color="text.secondary">
                TX Hash
              </Typography>
              <Typography variant="body1" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                {txHash}
              </Typography>
              {blockNumber && (
                <>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Block Number
                  </Typography>
                  <Typography variant="body1">{blockNumber}</Typography>
                </>
              )}
            </Paper>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default XAIResultPanel;
