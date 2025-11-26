"""Tests for PowerBI service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.powerbi_service import PowerBIService


class TestPowerBIService:
    """Test cases for PowerBIService."""

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant-id',
        'POWERBI_CLIENT_ID': 'test-client-id',
        'POWERBI_CLIENT_SECRET': 'test-client-secret'
    })
    def test_service_initialization(self):
        """Test PowerBI service initialization with valid credentials."""
        service = PowerBIService()
        
        assert service.tenant_id == 'test-tenant-id'
        assert service.client_id == 'test-client-id'
        assert service.client_secret == 'test-client-secret'
        assert service.base_url == "https://api.powerbi.com/v1.0/myorg"

    @patch.dict('os.environ', {'POWERBI_TENANT_ID': '', 'POWERBI_CLIENT_ID': 'test', 'POWERBI_CLIENT_SECRET': 'test'})
    def test_service_initialization_missing_tenant(self):
        """Test service initialization fails without tenant ID."""
        with pytest.raises(ValueError, match="TENANT_ID not configured"):
            PowerBIService()

    @patch.dict('os.environ', {'POWERBI_TENANT_ID': 'test', 'POWERBI_CLIENT_ID': '', 'POWERBI_CLIENT_SECRET': 'test'})
    def test_service_initialization_missing_client_id(self):
        """Test service initialization fails without client ID."""
        with pytest.raises(ValueError, match="CLIENT_ID not configured"):
            PowerBIService()

    @patch.dict('os.environ', {'POWERBI_TENANT_ID': 'test', 'POWERBI_CLIENT_ID': 'test', 'POWERBI_CLIENT_SECRET': ''})
    def test_service_initialization_missing_client_secret(self):
        """Test service initialization fails without client secret."""
        with pytest.raises(ValueError, match="CLIENT_SECRET not configured"):
            PowerBIService()

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.msal.ConfidentialClientApplication')
    def test_get_access_token_success(self, mock_msal):
        """Test successful token acquisition."""
        # Mock MSAL response
        mock_app = Mock()
        mock_app.acquire_token_for_client.return_value = {
            'access_token': 'test-token-123'
        }
        mock_msal.return_value = mock_app
        
        service = PowerBIService()
        token = service._get_access_token()
        
        assert token == 'test-token-123'
        mock_app.acquire_token_for_client.assert_called_once()

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.msal.ConfidentialClientApplication')
    def test_get_access_token_failure(self, mock_msal):
        """Test token acquisition failure."""
        # Mock MSAL error response
        mock_app = Mock()
        mock_app.acquire_token_for_client.return_value = {
            'error': 'invalid_client',
            'error_description': 'Invalid client credentials'
        }
        mock_msal.return_value = mock_app
        
        service = PowerBIService()
        
        with pytest.raises(Exception, match="Failed to authenticate"):
            service._get_access_token()

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.requests.get')
    @patch.object(PowerBIService, '_get_access_token')
    def test_get_dashboards_success(self, mock_token, mock_requests):
        """Test getting dashboards from PowerBI."""
        # Mock token
        mock_token.return_value = 'test-token'
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {'id': 'dash1', 'displayName': 'Dashboard 1'},
                {'id': 'dash2', 'displayName': 'Dashboard 2'}
            ]
        }
        mock_requests.return_value = mock_response
        
        service = PowerBIService()
        dashboards = service.get_dashboards()
        
        assert len(dashboards) == 2
        assert dashboards[0]['id'] == 'dash1'
        assert dashboards[1]['displayName'] == 'Dashboard 2'

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.requests.get')
    @patch.object(PowerBIService, '_get_access_token')
    def test_get_dashboard_by_id(self, mock_token, mock_requests):
        """Test getting specific dashboard by ID."""
        mock_token.return_value = 'test-token'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'dash123',
            'displayName': 'Test Dashboard',
            'embedUrl': 'https://powerbi.com/embed/test'
        }
        mock_requests.return_value = mock_response
        
        service = PowerBIService()
        dashboard = service.get_dashboard('dash123')
        
        assert dashboard['id'] == 'dash123'
        assert dashboard['displayName'] == 'Test Dashboard'

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.requests.get')
    @patch.object(PowerBIService, '_get_access_token')
    def test_get_workspaces(self, mock_token, mock_requests):
        """Test getting workspaces from PowerBI."""
        mock_token.return_value = 'test-token'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {'id': 'ws1', 'name': 'Workspace 1'},
                {'id': 'ws2', 'name': 'Workspace 2'}
            ]
        }
        mock_requests.return_value = mock_response
        
        service = PowerBIService()
        workspaces = service.get_workspaces()
        
        assert len(workspaces) == 2
        assert workspaces[0]['name'] == 'Workspace 1'

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch.object(PowerBIService, '_get_access_token')
    def test_get_headers(self, mock_token):
        """Test getting authorization headers."""
        mock_token.return_value = 'test-token-123'
        
        service = PowerBIService()
        headers = service._get_headers()
        
        assert headers['Authorization'] == 'Bearer test-token-123'
        assert headers['Content-Type'] == 'application/json'

    @patch.dict('os.environ', {
        'POWERBI_TENANT_ID': 'test-tenant',
        'POWERBI_CLIENT_ID': 'test-client',
        'POWERBI_CLIENT_SECRET': 'test-secret'
    })
    @patch('services.powerbi_service.requests.get')
    @patch.object(PowerBIService, '_get_access_token')
    def test_api_error_handling(self, mock_token, mock_requests):
        """Test handling of API errors."""
        mock_token.return_value = 'test-token'
        
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_requests.return_value = mock_response
        
        service = PowerBIService()
        
        with pytest.raises(Exception):
            service.get_dashboards()


class TestPowerBIServiceIntegration:
    """Integration tests for PowerBI service (require valid credentials)."""

    @pytest.mark.skip(reason="Requires valid PowerBI credentials")
    def test_real_powerbi_connection(self):
        """Test real connection to PowerBI API (skipped by default)."""
        # This test would need real credentials
        # Uncomment and configure to test against real PowerBI
        service = PowerBIService()
        dashboards = service.get_dashboards()
        assert isinstance(dashboards, list)
