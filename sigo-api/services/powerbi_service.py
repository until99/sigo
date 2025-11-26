"""Power BI Service - Integration with Microsoft Power BI REST API"""

import msal
import requests
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class PowerBIService:
    """Service for interacting with Power BI REST API using MSAL authentication."""

    def __init__(self):
        self.tenant_id = os.getenv("POWERBI_TENANT_ID")
        self.client_id = os.getenv("POWERBI_CLIENT_ID")
        self.client_secret = os.getenv("POWERBI_CLIENT_SECRET")
        self.base_url = "https://api.powerbi.com/v1.0/myorg"

        # Validate credentials
        if not self.tenant_id:
            raise ValueError(
                "Power BI TENANT_ID not configured. Please set POWERBI_TENANT_ID in .env file. "
                "See docs/POWERBI_SETUP.md for setup instructions."
            )
        if not self.client_id:
            raise ValueError(
                "Power BI CLIENT_ID not configured. Please set POWERBI_CLIENT_ID in .env file. "
                "See docs/POWERBI_SETUP.md for setup instructions."
            )
        if not self.client_secret:
            raise ValueError(
                "Power BI CLIENT_SECRET not configured. Please set POWERBI_CLIENT_SECRET in .env file. "
                "See docs/POWERBI_SETUP.md for setup instructions."
            )

    def _get_access_token(self) -> str:
        """Get access token for Power BI API using MSAL.

        Returns:
            Access token string

        Raises:
            Exception: If authentication fails
        """
        app_msal = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )

        token_result = app_msal.acquire_token_for_client(
            scopes=["https://analysis.windows.net/powerbi/api/.default"]
        )

        if not token_result:
            raise Exception(
                "Failed to acquire token from Power BI. "
                "Please verify your credentials in .env file. "
                "See docs/POWERBI_SETUP.md for setup instructions."
            )

        if "access_token" in token_result:
            return token_result["access_token"]

        # Handle error in token result
        error_desc = token_result.get(
            "error_description", token_result.get("error", "Unknown error")
        )
        raise Exception(
            f"Failed to authenticate with Power BI: {error_desc}. "
            f"Please verify your credentials in .env file. "
            f"See docs/POWERBI_SETUP.md for setup instructions."
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_dashboards(self) -> List[Dict[str, Any]]:
        """Get all dashboards from Power BI.

        Returns:
            List of dashboard dictionaries
        """
        url = f"{self.base_url}/dashboards"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("value", [])

    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Get a specific dashboard by ID.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard dictionary
        """
        url = f"{self.base_url}/dashboards/{dashboard_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()

    def get_workspace_dashboards(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all dashboards in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of dashboard dictionaries
        """
        url = f"{self.base_url}/groups/{workspace_id}/dashboards"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("value", [])

    def get_workspace_dashboard(
        self, workspace_id: str, dashboard_id: str
    ) -> Dict[str, Any]:
        """Get a specific dashboard in a workspace.

        Args:
            workspace_id: Workspace ID
            dashboard_id: Dashboard ID

        Returns:
            Dashboard dictionary
        """
        url = f"{self.base_url}/groups/{workspace_id}/dashboards/{dashboard_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()

    def delete_dashboard(self, workspace_id: str, dashboard_id: str) -> bool:
        """Delete a dashboard from a workspace.

        Args:
            workspace_id: Workspace ID
            dashboard_id: Dashboard ID

        Returns:
            True if successful
        """
        url = f"{self.base_url}/groups/{workspace_id}/dashboards/{dashboard_id}"
        response = requests.delete(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return True

    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces.

        Returns:
            List of workspace dictionaries
        """
        url = f"{self.base_url}/groups"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("value", [])

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Get a specific workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace dictionary
        """
        workspaces = self.get_workspaces()
        for workspace in workspaces:
            if workspace.get("id") == workspace_id:
                return workspace
        raise ValueError(f"Workspace {workspace_id} not found")

    def refresh_dataset(self, workspace_id: str, dataset_id: str) -> bool:
        """Trigger a refresh for a dataset.

        Args:
            workspace_id: Workspace ID
            dataset_id: Dataset ID

        Returns:
            True if refresh was triggered
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        response = requests.post(url, headers=self._get_headers(), json={}, timeout=30)
        response.raise_for_status()
        return True

    def get_dataset_refresh_history(
        self, workspace_id: str, dataset_id: str
    ) -> List[Dict[str, Any]]:
        """Get refresh history for a dataset.

        Args:
            workspace_id: Workspace ID
            dataset_id: Dataset ID

        Returns:
            List of refresh history records
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("value", [])

    def get_dataset(self, workspace_id: str, dataset_id: str) -> Dict[str, Any]:
        """Get dataset information.

        Args:
            workspace_id: Workspace ID
            dataset_id: Dataset ID

        Returns:
            Dataset dictionary
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()
