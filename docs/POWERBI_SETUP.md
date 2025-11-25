# Power BI Integration Setup

Este documento explica como configurar as credenciais do Power BI para integração com a API SIGO.

## Pré-requisitos

- Conta Microsoft com acesso ao Power BI
- Permissões de administrador no Azure AD (para criar app registration)
- Workspace do Power BI configurado

## Passo 1: Criar App Registration no Azure Portal

1. Acesse o [Azure Portal](https://portal.azure.com)
2. Navegue para **Azure Active Directory** > **App registrations**
3. Clique em **New registration**
4. Configure:
   - **Name**: SIGO Power BI Integration
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Deixe em branco por enquanto
5. Clique em **Register**

## Passo 2: Obter Credenciais

### Tenant ID
1. Na página Overview do seu App Registration, copie o **Directory (tenant) ID**
2. Cole no `.env`: `POWERBI_TENANT_ID=seu-tenant-id`

### Client ID (Application ID)
1. Na mesma página Overview, copie o **Application (client) ID**
2. Cole no `.env`: `POWERBI_CLIENT_ID=seu-client-id`

### Client Secret
1. No menu lateral, vá em **Certificates & secrets**
2. Clique em **New client secret**
3. Adicione uma descrição (ex: "SIGO API Key")
4. Escolha uma validade (recomendado: 24 months)
5. Clique em **Add**
6. **IMPORTANTE**: Copie o **Value** imediatamente (não será mostrado novamente!)
7. Cole no `.env`: `POWERBI_CLIENT_SECRET=seu-client-secret`

## Passo 3: Configurar Permissões da API

1. No menu lateral do App Registration, vá em **API permissions**
2. Clique em **Add a permission**
3. Selecione **Power BI Service**
4. Escolha **Application permissions**
5. Adicione as seguintes permissões:
   - `Dashboard.Read.All`
   - `Dashboard.ReadWrite.All`
   - `Dataset.Read.All`
   - `Dataset.ReadWrite.All`
   - `Workspace.Read.All`
   - `Workspace.ReadWrite.All`
6. Clique em **Add permissions**
7. **IMPORTANTE**: Clique em **Grant admin consent for [sua organização]**

## Passo 4: Configurar Power BI Service

1. Acesse o [Power BI Admin Portal](https://app.powerbi.com/admin-portal)
2. Vá em **Tenant settings**
3. Em **Developer settings**, habilite:
   - **Service principals can use Power BI APIs**
   - **Service principals can access read-only admin APIs**
4. Adicione o Service Principal (seu App Registration) aos grupos permitidos

## Passo 5: Adicionar Service Principal ao Workspace

Para cada workspace que você deseja acessar via API:

1. Abra o workspace no Power BI Service
2. Clique em **Workspace settings** (ícone de engrenagem)
3. Vá em **Access**
4. Clique em **Add people or groups**
5. Procure pelo nome do seu App Registration (SIGO Power BI Integration)
6. Atribua a role apropriada (Admin, Member, ou Contributor)
7. Clique em **Add**

## Passo 6: Testar a Integração

Após configurar todas as credenciais no `.env`, teste a integração:

```bash
# Inicie a API
uv run ./main.py

# Em outro terminal, teste o endpoint de sync
curl -X POST http://localhost:8000/v1/powerbi/sync
```

Se tudo estiver configurado corretamente, você verá os dashboards sendo sincronizados.

## Arquivo .env Exemplo

```env
# Power BI Configurations
POWERBI_TENANT_ID=12345678-1234-1234-1234-123456789abc
POWERBI_CLIENT_ID=87654321-4321-4321-4321-987654321xyz
POWERBI_CLIENT_SECRET=abc123~XYZ789.def456-GHI012
```

## Troubleshooting

### Erro: "AADSTS700016: Application not found in directory"
- Verifique se o TENANT_ID e CLIENT_ID estão corretos
- Certifique-se de que o App Registration não foi deletado

### Erro: "Insufficient privileges to complete the operation"
- Verifique se concedeu admin consent para as permissões
- Certifique-se de que habilitou service principals no Power BI Admin Portal
- Adicione o service principal ao workspace

### Erro: "The refresh operation is not supported for this dataset"
- Alguns datasets não suportam refresh via API
- Verifique se o dataset está em um workspace Premium ou Premium Per User

## Documentação Oficial

- [Power BI REST API](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [Service Principal Authentication](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal)
- [Power BI API Permissions](https://learn.microsoft.com/en-us/power-bi/developer/embedded/embed-service-principal-certificate#step-2---create-an-azure-ad-security-group)
