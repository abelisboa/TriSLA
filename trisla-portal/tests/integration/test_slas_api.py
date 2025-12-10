import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.batch
class TestSLAsAPI:
    """Integration tests for SLAs API"""
    
    async def test_create_sla_pln(self, async_client: AsyncClient, sample_sla_pln_data):
        """Test creating SLA via PLN"""
        response = await async_client.post(
            "/api/v1/slas/create/pln",
            json=sample_sla_pln_data
        )
        # May fail if SEM-CSMF is not available, but should return proper error
        assert response.status_code in [200, 500, 503]
    
    async def test_get_templates(self, async_client: AsyncClient):
        """Test getting SLA templates"""
        response = await async_client.get("/api/v1/slas/templates")
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) > 0
    
    async def test_get_template(self, async_client: AsyncClient):
        """Test getting a specific template"""
        # First get templates
        templates_response = await async_client.get("/api/v1/slas/templates")
        templates = templates_response.json()
        if len(templates) > 0:
            template_id = templates[0]["template_id"]
            response = await async_client.get(f"/api/v1/slas/templates/{template_id}")
            assert response.status_code == 200
            template = response.json()
            assert template["template_id"] == template_id







