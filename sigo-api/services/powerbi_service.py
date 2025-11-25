"""Power BI Service - Integration with Microsoft Power BI REST API"""

import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class PowerBIService:
    """Service for interacting with Power BI REST API."""

    def __init__(self):
        self.tenant_id = os.getenv("POWERBI_TENANT_ID")
        self.client_id = os.getenv("POWERBI_CLIENT_ID")
        self.client_secret = os.getenv("POWERBI_CLIENT_SECRET")
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self._access_token = None
        self._token_expiry = None

    def _get_access_token(self) -> str:
        """Get or refresh access token for Power BI API.

        Returns:
            Access token string

        Raises:
            Exception: If authentication fails
        """
        if self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry:
                return self._access_token

        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 300)

        return self._access_token

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
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return True

    def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all workspaces.

        Returns:
            List of workspace dictionaries
        """
        url = f"{self.base_url}/groups"
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.post(url, headers=self._get_headers(), json={})
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
        response = requests.get(url, headers=self._get_headers())
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
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
