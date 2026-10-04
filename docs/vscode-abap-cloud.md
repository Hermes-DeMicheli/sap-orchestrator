# VS Code Remote Development -- SAP ABAP Cloud

## Prerequisites

1. SAP BTP subaccount with ABAP Environment enabled
2. Cloud Connector configured (TCP tunnel to on-premise ABAP)
3. VS Code with extensions installed (see below)
4. Network access to ABAP Cloud endpoint (HTTPS, port 443)

## Extensions

- **SAP BTP Tools** (SAP) -- provides ABAP Cloud connection profile
- **Remote - SSH** (Microsoft) -- if connecting via jump host
- **Remote - Tunnels** (Microsoft) -- alternative without SSH key

## Connection Profile Setup

1. Open VS Code, Extensions panel, search "SAP BTP Tools"
2. Click "Add Connection Profile" in ABAP Perspectives view
3. Fill in:
   - Profile Name: `sap-orchestrator-abap`
   - ABAP Cloud URL: `https://<tenant>.abap.cloud.sap`
   - Client: `<your-client>`
   - User: `<your-user>`
   - Authentication: OAuth2SAMLBearerAssertion or X.509
4. Save profile -- VS Code stores credentials in session token cache

## Connect

1. ABAP Perspectives panel (left sidebar)
2. Right-click the profile, select "Connect"
3. Authenticate via browser pop-up (OAuth2) or certificate prompt
4. Once connected, you can:
   - Browse ADT repository structure
   - Activate objects (F8)
   - Set breakpoints and debug (F5)
   - Open ABAP editor, CDS view editor, behavior definition editor

## Local Development with ADT

1. Create a new project in ABAP Perspective
2. Import the repository content via `git clone` into the ABAP repo
3. Use VS Code Source Control to commit/push back to GitHub
4. Activate all objects before testing

## Troubleshooting

- Connection timeout: check Cloud Connector tunnel status
- 403 Forbidden: verify user has ABAP Development role
- Activation errors: check syntax via ABAP editor "Check" function (F2)