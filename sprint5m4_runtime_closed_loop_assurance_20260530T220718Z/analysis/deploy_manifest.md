# Deploy Manifest — Sprint 5M4

**Node:** node006  
**Namespace:** trisla  
**Method:** Digest-only (`kubectl set image @sha256:…`)

| Component | Old | New |
|-----------|-----|-----|
| trisla-sla-agent-layer | sha256:3dad23e25b30… | sha256:bbad9901e902… |
| trisla-portal-backend | sha256:cab764f7c1cc… | sha256:2fd21a28c857… |
| trisla-portal-frontend | sha256:7ef311fcd8f5… | sha256:1179359a27e5… |

All rollouts: SUCCESS

E2E post-deploy: 4/4 PASS (`evidence/e2e_summary.json`)
