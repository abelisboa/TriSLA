import pytest
from playwright.async_api import async_playwright, Page, Browser


@pytest.mark.e2e
class TestPortalE2E:
    """End-to-end tests for the portal"""
    
    @pytest.fixture
    async def browser(self):
        """Browser fixture"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            yield browser
            await browser.close()
    
    @pytest.fixture
    async def page(self, browser: Browser):
        """Page fixture"""
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        yield page
        await page.close()
    
    async def test_overview_page_loads(self, page: Page):
        """Test that overview page loads"""
        await page.wait_for_load_state("networkidle")
        # Check for main heading
        heading = await page.locator("h1").first()
        assert await heading.is_visible()
        assert "Overview" in await heading.text_content()
    
    async def test_modules_page_navigation(self, page: Page):
        """Test navigation to modules page"""
        # Click on Modules link
        await page.click('text=Modules')
        await page.wait_for_load_state("networkidle")
        
        # Check for modules heading
        heading = await page.locator("h1").first()
        assert await heading.is_visible()
        assert "Módulos" in await heading.text_content() or "Modules" in await heading.text_content()
    
    async def test_contracts_page_loads(self, page: Page):
        """Test contracts page loads"""
        await page.goto("http://localhost:3000/contracts")
        await page.wait_for_load_state("networkidle")
        
        heading = await page.locator("h1").first()
        assert await heading.is_visible()
    
    async def test_sla_creation_pln_page(self, page: Page):
        """Test SLA creation PLN page"""
        await page.goto("http://localhost:3000/slas/create/pln")
        await page.wait_for_load_state("networkidle")
        
        # Check for form elements
        tenant_input = await page.locator('input[type="text"]').first()
        assert await tenant_input.is_visible()
        
        textarea = await page.locator('textarea').first()
        assert await textarea.is_visible()
    
    async def test_xai_viewer_page(self, page: Page):
        """Test XAI viewer page"""
        await page.goto("http://localhost:3000/xai")
        await page.wait_for_load_state("networkidle")
        
        heading = await page.locator("h1").first()
        assert await heading.is_visible()
        assert "XAI" in await heading.text_content()







