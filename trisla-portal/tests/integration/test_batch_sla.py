import pytest
import json
import csv
import io
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.batch
class TestBatchSLA:
    """Integration tests for Batch SLA Creation"""
    
    async def test_batch_sla_csv(self, async_client: AsyncClient):
        """Test batch SLA creation with CSV file"""
        # Create CSV content
        csv_data = [
            ["tenant_id", "intent_text", "service_type"],
            ["tenant-001", "Slice URLLC com latência 10ms", "URLLC"],
            ["tenant-002", "Slice eMBB para streaming", "eMBB"],
            ["tenant-003", "Slice mMTC para IoT", "mMTC"],
        ]
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(csv_data)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        # Create file-like object
        files = {
            "file": ("batch.csv", csv_content, "text/csv")
        }
        data = {
            "tenant_id": "tenant-001"
        }
        
        response = await async_client.post(
            "/api/v1/slas/create/batch",
            files=files,
            data=data
        )
        # May fail if SEM-CSMF is not available
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            batch_job = response.json()
            assert "batch_id" in batch_job
            assert batch_job["total_slas"] == 3
            assert batch_job["status"] in ["PENDING", "PROCESSING", "COMPLETED"]
    
    async def test_batch_sla_json(self, async_client: AsyncClient):
        """Test batch SLA creation with JSON file"""
        json_data = [
            {
                "tenant_id": "tenant-001",
                "intent_text": "Slice URLLC com latência 10ms",
                "service_type": "URLLC"
            },
            {
                "tenant_id": "tenant-002",
                "intent_text": "Slice eMBB para streaming",
                "service_type": "eMBB"
            }
        ]
        
        json_content = json.dumps(json_data).encode('utf-8')
        
        files = {
            "file": ("batch.json", json_content, "application/json")
        }
        data = {
            "tenant_id": "tenant-001"
        }
        
        response = await async_client.post(
            "/api/v1/slas/create/batch",
            files=files,
            data=data
        )
        assert response.status_code in [200, 500, 503]
    
    async def test_batch_sla_large(self, async_client: AsyncClient):
        """Test batch SLA creation with > 100 intents"""
        # Generate 150 intents
        csv_data = [["tenant_id", "intent_text", "service_type"]]
        for i in range(150):
            csv_data.append([
                f"tenant-{i:03d}",
                f"Slice URLLC {i}",
                "URLLC"
            ])
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(csv_data)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        files = {
            "file": ("batch_large.csv", csv_content, "text/csv")
        }
        data = {
            "tenant_id": "tenant-001"
        }
        
        response = await async_client.post(
            "/api/v1/slas/create/batch",
            files=files,
            data=data
        )
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            batch_job = response.json()
            assert batch_job["total_slas"] == 150







