"""Collector for Azure Managed Disks."""

import logging

from azure_client import AzureClient
from constants import API_VERSIONS, OBJ_DISK, OBJ_RESOURCE_GROUP, OBJ_VIRTUAL_MACHINE
from helpers import make_identifiers, extract_resource_group, safe_property, sanitize_tag_key

logger = logging.getLogger(__name__)


def collect_disks(client: AzureClient, result, adapter_kind: str,
                  subscriptions: list):
    """Collect managed disks across all subscriptions."""
    logger.info("Collecting disks")
    total = 0

    for sub in subscriptions:
        sub_id = sub["subscriptionId"]
        disks = client.get_all(
            path=f"/subscriptions/{sub_id}/providers/Microsoft.Compute/disks",
            api_version=API_VERSIONS["disks"],
        )

        for disk in disks:
            disk_name = disk["name"]
            rg_name = extract_resource_group(disk.get("id", ""))
            props = disk.get("properties", {})
            sku = disk.get("sku", {})

            obj = result.object(
                adapter_kind=adapter_kind,
                object_kind=OBJ_DISK,
                name=disk_name,
                identifiers=make_identifiers([
                    ("subscription_id", sub_id),
                    ("resource_group", rg_name),
                    ("disk_name", disk_name),
                ]),
            )

            safe_property(obj, "disk_name", disk_name)
            safe_property(obj, "resource_id", disk.get("id", ""))
            safe_property(obj, "location", disk.get("location", ""))
            safe_property(obj, "subscription_id", sub_id)
            safe_property(obj, "resource_group", rg_name)
            safe_property(obj, "sku_name", sku.get("name", ""))
            safe_property(obj, "sku_tier", sku.get("tier", ""))
            safe_property(obj, "disk_size_gb", props.get("diskSizeGB", ""))
            safe_property(obj, "disk_iops_read_write",
                          props.get("diskIOPSReadWrite", ""))
            safe_property(obj, "disk_mbps_read_write",
                          props.get("diskMBpsReadWrite", ""))
            safe_property(obj, "disk_state", props.get("diskState", ""))
            safe_property(obj, "os_type", props.get("osType", ""))
            safe_property(obj, "time_created", props.get("timeCreated", ""))
            safe_property(obj, "provisioning_state",
                          props.get("provisioningState", ""))
            safe_property(obj, "encryption_type",
                          props.get("encryption", {}).get("type", ""))
            safe_property(obj, "network_access_policy",
                          props.get("networkAccessPolicy", ""))

            # Tags
            tags = disk.get("tags", {})
            if tags:
                for key, value in tags.items():
                    safe_property(obj, f"tag_{sanitize_tag_key(key)}", value)

            # Zones
            zones = disk.get("zones", [])
            if zones:
                safe_property(obj, "availability_zone", ", ".join(zones))

            # Relationship: Disk -> Resource Group
            if rg_name:
                rg_obj = result.object(
                    adapter_kind=adapter_kind,
                    object_kind=OBJ_RESOURCE_GROUP,
                    name=rg_name,
                    identifiers=make_identifiers([
                        ("subscription_id", sub_id),
                        ("resource_group_name", rg_name),
                    ]),
                )
                obj.add_parent(rg_obj)

            # Relationship: Disk -> VM (parent) via managedBy
            managed_by = disk.get("managedBy", "")
            safe_property(obj, "attached_vm_id", managed_by)
            if managed_by:
                vm_name = managed_by.split("/")[-1] if managed_by else ""
                vm_rg = extract_resource_group(managed_by)
                if vm_name and vm_rg:
                    safe_property(obj, "attached_vm_name", vm_name)
                    vm_obj = result.object(
                        adapter_kind=adapter_kind,
                        object_kind=OBJ_VIRTUAL_MACHINE,
                        name=vm_name,
                        identifiers=make_identifiers([
                            ("subscription_id", sub_id),
                            ("resource_group", vm_rg),
                            ("vm_name", vm_name),
                        ]),
                    )
                    obj.add_parent(vm_obj)

        total += len(disks)

    logger.info("Collected %d disks", total)
