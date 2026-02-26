import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 10 },     // Stay at 10 users
    { duration: '30s', target: 50 },    // Ramp up to 50 users
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],      // Error rate should be less than 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // Test health endpoint
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  });

  // Test modules endpoint
  const modulesRes = http.get(`${BASE_URL}/api/v1/modules`);
  check(modulesRes, {
    'modules status is 200': (r) => r.status === 200,
    'modules response is array': (r) => {
      try {
        const data = JSON.parse(r.body);
        return Array.isArray(data);
      } catch {
        return false;
      }
    },
  });

  // Test contracts endpoint
  const contractsRes = http.get(`${BASE_URL}/api/v1/contracts`);
  check(contractsRes, {
    'contracts status is 200': (r) => r.status === 200,
  });

  // Test SLOs endpoint
  const slosRes = http.get(`${BASE_URL}/api/v1/slos`);
  check(slosRes, {
    'slos status is 200': (r) => r.status === 200,
  });

  sleep(1);
}







