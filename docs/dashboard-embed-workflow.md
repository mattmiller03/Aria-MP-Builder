# Embedding Dashboards in the Management Pack

Dashboards can be bundled into the `.pak` file so they auto-install when the pack is deployed. This eliminates the need to manually build dashboards after each pak upgrade.

## Workflow

### 1. Build the Dashboard in the Aria Ops UI

Build and configure your dashboard manually in Aria Ops first. Use your `AzureGovAdapter` objects and metrics. Test that all widgets, interactions, and filters work correctly.

### 2. Export the Dashboard

1. Navigate to **Visualize > Dashboards**
2. Click **Manage** (gear icon)
3. Select the dashboard you want to export
4. Click **...** (three dots) > **Export**
5. A `.zip` file downloads

**Important:** Export dashboards one at a time. Selecting multiple combines them into a single JSON, which is harder to manage.

### 3. Prepare the Content Directory

Unzip the export. The structure inside is:

```
dashboard/
├── dashboard.json
└── resources/
    └── resources.properties
```

Rename the folder to match your dashboard name and place it in `Azure/content/dashboards/`:

```
Azure/content/dashboards/
├── DedicatedHostDetail/
│   ├── DedicatedHostDetail.json
│   └── resources/
│       └── resources.properties
├── AzureGovOverview/
│   ├── AzureGovOverview.json
│   └── resources/
│       └── resources.properties
└── VirtualMachineAnalysis/
    ├── VirtualMachineAnalysis.json
    └── resources/
        └── resources.properties
```

**Rules:**
- The directory name and JSON filename must match (without extension)
- Each dashboard gets its own subdirectory
- The `resources/resources.properties` file contains localization strings

### 4. Handle Configuration Files (if needed)

Some widgets reference external configuration files that are **NOT** included in the dashboard export:

| Widget Type | Config Location |
|-------------|----------------|
| Text Widget Content | `content/files/txtwidget/` |
| Resource Kind Metrics (Scoreboard) | `content/files/reskndmetric/` |
| Topology Widget | `content/files/topowidget/` |

If your dashboard uses a **Scoreboard** widget that references `AzureGov_All_KPIs.xml`, that file must exist in `content/files/reskndmetric/` (already created).

To export these from the Aria Ops UI:
1. **Configure > Configuration Files**
2. Find the relevant file
3. Export and place in the appropriate `content/files/` subdirectory

### 5. Build the Pak

Run `mp-build` as normal. The `content/` directory is automatically included in the pak:

```bash
sudo mp-build -i --no-ttl --registry-tag "<REGISTRY-IP>:5000/azuregovcloud-adapter" -P 8181
```

### 6. Verify After Install

After uploading the pak to Aria Ops:
1. Go to **Visualize > Dashboards**
2. The exported dashboards should appear automatically
3. Verify widgets populate with data after the next collection cycle

## Current Content Structure

```
Azure/content/
├── alertdefs/
│   └── AzureGov_Alert_Defs.xml          # 7 alerts, 14 symptoms
├── dashboards/
│   └── (add exported dashboard folders here)
├── files/
│   └── reskndmetric/
│       └── AzureGov_All_KPIs.xml        # KPI metrics for scoreboards
└── traversalSpecs/
    └── AzureGovTraversalSpecs.xml       # Object navigation paths
```

## Limitations

- **Views** cannot be embedded in paks (SDK limitation). Build manually in UI.
- Dashboard interactions reference widget UUIDs — they're specific to each export.
- If the adapter kind or resource kind keys change, dashboard JSON must be updated to match.
