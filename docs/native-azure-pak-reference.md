# Native Azure Management Pack Reference

Analysis of VMware's official Management Pack for Microsoft Azure (v8.18.0, EOGS Sept 2025). Used as the template for building feature parity in our custom Azure Gov pack.

Source paks extracted from Aria Ops:
- `MicrosoftAzureAdapter-818024067771.pak` (68MB) — main adapter
- `MicrosoftAzure-90020231005113122.pak` (18MB) — SQL content pak

## Resource Types (80+)

### Compute (7 types)
| Native Key | Our Equivalent | Metrics |
|-----------|---------------|---------|
| `AZURE_VIRTUAL_MACHINE` | `azure_virtual_machine` | CPU%, Disk R/W Bytes, Disk R/W Ops, Network In/Out |
| `AZURE_VIRTUAL_SCALESET` | not implemented | 20 metrics |
| `AZURE_VIRTUAL_SCALESET_INSTANCE` | not implemented | 9 metrics |
| `AZURE_COMPUTE_HOSTGROUPS` | `azure_host_group` | none (properties only) |
| `AZURE_DEDICATE_HOST` | `azure_dedicated_host` | none (we added pricing!) |
| `AZURE_AVAILABILITY_SETS` | not implemented | none |
| `AZURE_PROXIMITY_PLACEMENT_GROUP` | not implemented | none |

### Storage (2 types)
| Native Key | Our Equivalent | Metrics |
|-----------|---------------|---------|
| `AZURE_STORAGE_DISK` | `azure_disk` | none |
| `AZURE_STORAGE_ACCOUNT` | `azure_storage_account` | 42 metrics (we have 7) |

### Database (9 types)
| Native Key | Our Equivalent | Metrics |
|-----------|---------------|---------|
| `AZURE_SQL_SERVER` | `azure_sql_server` | CPU%, Data I/O, DTU, Sessions, Workers |
| `AZURE_SQL_DATABASE` | `azure_sql_database` | 24+ metrics (we have 15) |
| `AZURE_POSTGRESQL_SERVER` | not implemented | 15 metrics |
| `AZURE_MYSQL_SERVER` | not implemented | 15 metrics |
| `AZURE_SQL_MANAGEDINSTANCES` | not implemented | properties only |
| `AZURE_MARIADB_SERVER` | not implemented | properties only |
| `AZURE_DB_ACCOUNT` (CosmosDB) | not implemented | 5 metrics |

### Networking (18 types)
| Native Key | Our Equivalent | Metrics |
|-----------|---------------|---------|
| `AZURE_LB` | `azure_load_balancer` | 4 metrics |
| `AZURE_NW_INTERFACE` | `azure_network_interface` | 4 metrics |
| `AZURE_VIRTUAL_NETWORK` | `azure_virtual_network` | RTT, failed pings |
| `AZURE_VIRTUAL_NETWORK_GATEWAY` | not implemented | 10 metrics |
| `AZURE_APPLICATION_GATEWAY` | not implemented | 21 metrics |
| `AZURE_PUBLIC_IPADDRESSES` | `azure_public_ip` | properties only |
| `AZURE_EXPRESSROUTE_CIRCUITS` | `azure_expressroute_circuit` | properties only |
| Others (NSG, Route Tables, DNS, Firewall, etc.) | not implemented | properties only |

### Application (3 types)
| Native Key | Our Equivalent | Metrics |
|-----------|---------------|---------|
| `AZURE_APP_SERVICE` | `azure_app_service` | 35 metrics (we have 0) |
| `AZURE_FUNCTIONS_APP` | not implemented | properties only |
| `AZURE_APP_SERVICE_PLAN` | not implemented | properties only |

## Key Metrics by Resource Type

### Virtual Machine (matches our implementation)
- `CPU|CPU_USAGE` (%) — maps to Azure Monitor `Percentage CPU`
- `Disk|disk_read_operations` — `Disk Read Operations/Sec`
- `Disk|disk_write_operations` — `Disk Write Operations/Sec`
- `Disk|DATA_READ_DISK` (bytes) — `Disk Read Bytes`
- `Disk|DATA_WRITE_DISK` (bytes) — `Disk Write Bytes`
- `Network|NETWORK_IN` (bytes) — `Network In Total`
- `Network|NETWORK_OUT` (bytes) — `Network Out Total`

### SQL Database (we have most of these)
- `CPU|cpu_usage`, `DTU_PERCENTAGE`, `DWU_PERCENTAGE`
- `Storage|data_io`, `Storage|log_io`, `Storage|storage_usage`
- `Network|successful_connections`, `Network|failed_connections`
- `Workload|sessions`, `Workload|workers`

## Alert Thresholds (from native pak)

| Alert | Resource | Metric | Warning | Immediate | Critical |
|-------|----------|--------|---------|-----------|----------|
| CPU High | VM | `CPU\|CPU_USAGE` | >85% | >90% | >95% |
| DTU High | SQL DB | `DTU_PERCENTAGE` | >85% | >90% | >95% |
| DWU High | SQL DB | `DWU_PERCENTAGE` | >85% | >90% | >95% |
| Data Space High | SQL DB | `DATA_SPACE_USED_PERCENT` | >85% | >90% | >95% |
| Availability Low | Storage | availability | <95% | — | — |
| VM Powered Off | VM | `powerState` | != "Powered On" | — | — |
| App Not Running | App Service | `state` | != "Running" | — | — |

Wait/cancel cycles: 3 for metric symptoms, 2 for property symptoms.

## Traversal Hierarchy

```
Subscription
  └── Resource Group
        ├── Host Group > Dedicated Host > VM > Disk
        ├── VM > Disk
        ├── SQL Server > SQL Database
        ├── VNet > Subnet, NIC, VNet Gateway
        ├── Public IP > LB, App Gateway, VNet Gateway, NIC
        ├── K8s Cluster > Scale Set > Scale Set Instance
        ├── Container Group > Container
        ├── Storage Account
        ├── Load Balancer
        ├── App Service
        ├── Key Vault
        └── (many more...)
```

## Dashboard Inventory (native pak)

1. Azure Application Gateway (5 widgets)
2. Azure Availability (16 widgets)
3. Azure Inventory (5 widgets)
4. Azure Kubernetes Service Overview (8 widgets)
5. Azure Load Balancer (6 widgets)
6. Azure Optimization (9 widgets)
7. Azure SQL Database (7 widgets)
8. Azure Virtual Machine (17 widgets)
9. Azure Virtual Network Overview (8 widgets)
10. Azure Virtual Network Gateway (6 widgets)
11. Azure Storage Account Overview (23 widgets)

## What We Have That They Don't

- **Dedicated host pricing** — hourly/monthly rates from Azure Retail Prices API
- **VM-to-host capacity tracking** — vm_size_summary, allocatable_vm_summary
- **Disk SKU tracking per host** — vm_disk_skus
- **Air-gapped pricing fallback** — hardcoded table with fetch_pricing.py updater

## Priority Gaps to Close

1. **App Service metrics** (35 in native pack, 0 in ours)
2. **Storage Account sub-service metrics** (42 in native, 7 in ours)
3. **Virtual Network metrics** (RTT, failed pings)
4. **VMSS support** (if applicable to Azure Gov)
5. **PostgreSQL/MySQL metrics** (if deployed)
6. **Application Gateway metrics** (if deployed)
