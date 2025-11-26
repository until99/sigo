# Power BI Setup Guide

This guide explains how to configure Power BI integration for the SIGO application.

## Prerequisites

- Access to Azure Portal with admin privileges for your tenant
- Power BI Pro or Premium license

## Step 1: Register Application in Azure AD

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure the application:
   - **Name**: `SIGO Power BI Integration` (or your preferred name)
   - **Supported account types**: Select "Accounts in this organizational directory only (Single tenant)"
   - **Redirect URI**: Leave blank for now
5. Click **Register**

## Step 2: Note Your Credentials

After registration, you'll see the application overview page. Note down:

- **Application (client) ID**: Copy this value
- **Directory (tenant) ID**: Copy this value

## Step 3: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "SIGO API Secret")
4. Choose an expiration period (recommended: 24 months)
5. Click **Add**
6. **IMPORTANT**: Copy the secret **Value** immediately (you won't be able to see it again)

## Step 4: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Power BI Service**
4. Choose **Delegated permissions** and add:
   - `Dashboard.Read.All`
   - `Dataset.Read.All`
   - `Workspace.Read.All`
5. Also add **Application permissions**:
   - `Dashboard.Read.All`
   - `Dataset.Read.All`
   - `Workspace.Read.All`
   - `Tenant.Read.All` (if you need tenant-wide access)
6. Click **Add permissions**

## Step 5: Grant Admin Consent

**CRITICAL**: Your Azure AD admin must grant consent for these permissions.

1. In the **API permissions** page, click **Grant admin consent for [Your Tenant]**
2. Click **Yes** to confirm
3. Verify all permissions show a green checkmark under "Status"

## Step 6: Create Security Group in Azure AD (Required)

**IMPORTANT**: Power BI doesn't allow you to add service principals directly. You must add them to an Azure AD Security Group first.

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **Groups**
3. Click **New group**
4. Configure the group:
   - **Group type**: Security
   - **Group name**: `powerbi_service` (or your preferred name)
   - **Group description**: "Security group for Power BI service principals"
   - **Membership type**: Assigned
5. Click **Create**
6. Open the newly created group
7. Go to **Members** > **Add members**
8. Search for your application name (e.g., "SIGO Power BI Integration")
9. Select your service principal and click **Select**

## Step 7: Enable Power BI Service Admin Settings

1. Go to [Power BI Admin Portal](https://app.powerbi.com/admin-portal)
2. Navigate to **Tenant settings**
3. Scroll to **Developer settings**
4. Find **Allow service principals to use Power BI APIs**
5. Enable the toggle
6. Select **Specific security groups (Recommended)**
7. In the text box, type and select the security group you created (e.g., `powerbi_service`)
8. Click **Apply**

**Note**: Changes may take 15-30 minutes to propagate.

**Why this is needed**: Power BI admin settings only accept Security Groups, not individual applications. The service principal must be a member of a security group that is then added to the Power BI tenant settings.

## Step 8: Configure Environment Variables

Create or update your `.env` file in the `sigo-api` directory:

```env
# Power BI Configuration
POWERBI_TENANT_ID=your-tenant-id-here
POWERBI_CLIENT_ID=your-client-id-here
POWERBI_CLIENT_SECRET=your-client-secret-here
```

Replace the placeholder values with the actual credentials from Steps 2 and 3.

## Step 9: Test the Connection

Run your API and test the Power BI connection:

```bash
cd sigo-api
# Start your API server
# Make a request to a Power BI endpoint
```

## Troubleshooting

### Error: Application not found in directory

**Problem**: `Application with identifier 'xxx' was not found in the directory 'yyy'`

**Solutions**:

- Verify you're using the correct **Tenant ID** from your Azure AD
- Ensure the **Client ID** matches your app registration
- Check that you're logged into the correct Azure tenant

### Error: Insufficient privileges

**Problem**: `AADSTS65001: The user or administrator has not consented`

**Solutions**:

- Admin consent hasn't been granted (see Step 5)
- Wait 15-30 minutes after granting consent for changes to propagate
- Verify the service principal is enabled in Power BI Admin Portal (Step 6)

### Error: Invalid client secret

**Problem**: Authentication fails with "invalid_client"

**Solutions**:

- The client secret may have expired - create a new one
- Ensure you copied the secret **Value**, not the Secret ID
- Check for extra spaces or characters when pasting into .env

### Error: AADSTS700016

**Problem**: Application not installed by administrator

**Solutions**:

- Complete Step 5 to grant admin consent
- Ensure the app registration exists in the correct tenant
- Verify service principals are enabled in Power BI (Step 6)

## Security Best Practices

1. **Rotate secrets regularly**: Set a calendar reminder to rotate client secrets before expiration
2. **Use least privilege**: Only grant the minimum required permissions
3. **Protect .env files**: Never commit `.env` files to version control (add to `.gitignore`)
4. **Use Azure Key Vault**: For production, consider storing secrets in Azure Key Vault
5. **Monitor access**: Regularly review application sign-in logs in Azure AD

## Additional Resources

- [Power BI REST API Documentation](https://docs.microsoft.com/en-us/rest/api/power-bi/)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Service Principal with Power BI](https://docs.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
