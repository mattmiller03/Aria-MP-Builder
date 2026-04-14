# Debug Folder

Use this folder for transferring logs and scratch files between machines.
Files in this folder are git-ignored except this README.

Common files to put here:
- `terminal.log` — console output from the server
- `adapter.log` — adapter container logs
- `casa-log.txt` — Aria Ops CASA service logs
- `validation.log` — mp-test validation output




The simplest test — just curl it from the machine that runs the adapter:


curl -s "https://prices.azure.com/api/retail/prices?\$filter=serviceName%20eq%20'Virtual%20Machines%20Dedicated%20Host'%20and%20armRegionName%20eq%20'usgovvirginia'%20and%20priceType%20eq%20'Consumption'" | python3 -m json.tool | head -30
That tells you two things at once:

Can the machine reach prices.azure.com
Does the region name format (usgovvirginia vs usgov virginia) return results
If you get results back, check the armSkuName values match what your hosts report as sku_name. If you get an empty Items array, try the spaced version:


curl -s "https://prices.azure.com/api/retail/prices?\$filter=serviceName%20eq%20'Virtual%20Machines%20Dedicated%20Host'%20and%20armRegionName%20eq%20'usgov%20virginia'%20and%20priceType%20eq%20'Consumption'" | python3 -m json.tool | head -30
If neither returns results, try dropping the region filter entirely to confirm the API is reachable:


curl -s "https://prices.azure.com/api/retail/prices?\$filter=serviceName%20eq%20'Virtual%20Machines%20Dedicated%20Host'" | python3 -m json.tool | head -30
If the machine can't reach prices.azure.com at all (timeout/connection refused), the air-gap is blocking it and we'll need to switch to a hardcoded pricing table instead.

curl -s -H "Authorization: Bearer <TOKEN>" "https://management.usgovcloudapi.net/subscriptions/<SUB_ID>/providers/Microsoft.Compute/hostGroups?api-version=2023-03-01&\$expand=instanceView" | python3 -m json.tool | grep -i skuName



You already have both in your adapter's credentials:

Sub ID — it's in your connections.json (or visible in the Azure portal under Subscriptions)
Bearer token — your adapter's auth.py handles this. You can grab one quickly with a Python one-liner from the MP Builder server:

cd /opt/aria/Aria-MP-Builder/Azure/app
python3 -c "
from auth import AzureAuthenticator
auth = AzureAuthenticator('<TENANT_ID>', '<CLIENT_ID>', '<CLIENT_SECRET>', 'government')
print(auth.get_token())
"
Replace the three values from your connections.json. That prints a bearer token you can paste into the curl.

Alternatively, skip all that and just check what SKUs you have from the mp-test output. When you run a collect, the adapter logs should show the host groups and hosts it found. Or check the Aria Ops UI — go to your Azure adapter objects, find the Dedicated Host objects, and look at the sku_name property.

If none of those are convenient, you can also check the Azure Gov portal at portal.azure.us > Dedicated Hosts — the SKU is listed on each host.

cd /opt/aria/Aria-MP-Builder/Azure/app
python3 -c "
from auth import AzureAuthenticator
from azure_client import AzureClient
auth = AzureAuthenticator('<TENANT_ID>', '<CLIENT_ID>', '<CLIENT_SECRET>', 'government')
client = AzureClient(auth, 'government')
subs = client.get_all('/subscriptions', '2022-12-01')
print(f'Service principal can see {len(subs)} subscriptions:')
for s in subs:
    print(f'  {s[\"displayName\"]} ({s[\"subscriptionId\"]})')
"




The adapter_definition code looks correct — all object types have proper keys. The "resource key=, resource args=[]" error is coming from the Aria Ops server during pak installation, not from the adapter code itself.

This is likely a conflict with the existing v1.4.0 installation that's in a failed state. The clobber didn't fully clean up, so Aria Ops has stale/empty resource kind entries from the previous failed install attempt.

Try this sequence on the Aria Ops node:


# 1. Check current pak state
curl -k -u admin "https://localhost/suite-api/api/solutions" | python3 -m json.tool | grep -A5 -i azure

# 2. Force uninstall the stuck pak via the API
TOKEN=$(curl -k -s -X POST "https://localhost/suite-api/api/auth/token/acquire" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PASSWORD","authSource":"local"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -k -X DELETE "https://localhost/suite-api/api/solutions/AzureGovCloud" \
  -H "Authorization: vRealizeOpsToken $TOKEN"

# 3. Restart CASA
sudo systemctl restart vmware-casa
Then wait a few minutes and do a fresh install of the v1.4.1 pak.

Important: deleting the solution via the API removes the adapter definition but your collected object data should persist in the datastore. When you reinstall with the same adapter kind (AzureGovAdapter) and the same object identifiers, Aria Ops will reconnect to the existing objects.


The VCSA patching process when vSAN is configured requires some specific steps to ensure cluster health is maintained throughout. Here's the proper method:
Patching VCSA 8 with vSAN Configured
Pre-Patch Checks
Before anything else:

Verify vSAN cluster health in Skyline Health — resolve any warnings/errors first
Confirm all hosts are in a Connected state and not in maintenance mode
Check vSAN resync status is 0% (no active resyncing)
Take a VCSA file-based backup (critical — if VCSA lives on vSAN, this is your only real safety net)
Note your current VCSA version and target patch level

The Core Consideration with vSAN
The VCSA itself may be running on the vSAN datastore, which creates a dependency loop during patching. vCenter needs to be online to manage vSAN, but patching takes vCenter offline temporarily. VMware handles this with vSAN ESA/OSA resiliency — the VMs keep running on the datastore even while vCenter is patched, since the vSAN data plane is independent of the management plane.
This means the patch is generally safe to apply without putting hosts in maintenance mode, as long as your cluster has proper redundancy (FTT policy met).
Patching Methods
Method 1: VAMI (Recommended for most environments)

Log into the VCSA VAMI at https://<vcsa-fqdn>:5480
Go to Update → Settings — verify your update source (VMware repo or local depot)
Click Check Updates
Stage the update first (Stage Only) — this downloads and prepares without applying
Once staged, click Stage and Install or Install if already staged
Accept the EULA and confirm the reboot
Monitor the update progress — VCSA will reboot automatically

Method 2: Lifecycle Manager (vLCM) — If managing VCSA via LCM
Available in vSphere 8 for appliance management; less common but centralizes patching alongside host baselines.
Method 3: CLI (ISO/offline patch)
bash# SSH into VCSA, enable bash shell
shell

# Stage and apply patch from depot or local ISO mount
software-packages install --iso --acceptEulas
Post-Patch Validation

Confirm vCenter services are healthy via VAMI → Services
Re-check vSAN Skyline Health — verify no new issues introduced
Confirm all hosts reconnected and cluster is fully healthy
Check vSAN resync status post-reboot
Validate your vSAN policies are still intact on critical VMs

Key Timing Notes

The VCSA reboot during patching typically takes 15–30 minutes
During that window, existing VMs on vSAN keep running — the data plane is unaffected
Any vCenter-dependent operations (vMotion, DRS, new VM deploys) will be unavailable during the outage window
Schedule during low-activity periods and communicate the management plane outage to stakeholders

The biggest risk isn't the patch itself — it's going in with an unhealthy vSAN cluster or skipping the file-based backup. Always back up first.