"""Collector for Azure App Services and Function Apps."""

import logging

from azure_client import AzureClient
from constants import API_VERSIONS, OBJ_APP_SERVICE, OBJ_RESOURCE_GROUP
from helpers import make_identifiers, extract_resource_group, safe_property

logger = logging.getLogger(__name__)


def collect_app_services(client: AzureClient, result, adapter_kind: str,
                         subscriptions: list):
    """Collect web apps and function apps across all subscriptions."""
    logger.info("Collecting app services")
    total = 0

    for sub in subscriptions:
        sub_id = sub["subscriptionId"]
        apps = client.get_all(
            path=f"/subscriptions/{sub_id}/providers/Microsoft.Web/sites",
            api_version=API_VERSIONS["web_apps"],
        )

        for app in apps:
            app_name = app["name"]
            rg_name = extract_resource_group(app.get("id", ""))
            props = app.get("properties", {})

            obj = result.object(
                adapter_kind=adapter_kind,
                object_kind=OBJ_APP_SERVICE,
                name=app_name,
                identifiers=make_identifiers([
                    ("subscription_id", sub_id),
                    ("resource_group", rg_name),
                    ("app_name", app_name),
                ]),
            )

            safe_property(obj, "app_name", app_name)
            safe_property(obj, "resource_id", app.get("id", ""))
            safe_property(obj, "location", app.get("location", ""))
            safe_property(obj, "subscription_id", sub_id)
            safe_property(obj, "resource_group", rg_name)

            # Kind: "app", "functionapp", "functionapp,linux", etc.
            kind = app.get("kind", "")
            safe_property(obj, "kind", kind)
            safe_property(obj, "is_function_app",
                          str("functionapp" in kind.lower()))

            safe_property(obj, "state", props.get("state", ""))
            safe_property(obj, "default_host_name",
                          props.get("defaultHostName", ""))
            safe_property(obj, "https_only",
                          str(props.get("httpsOnly", "")))
            safe_property(obj, "enabled", str(props.get("enabled", "")))

            # Host names
            host_names = props.get("hostNames", [])
            safe_property(obj, "host_names", ", ".join(host_names))

            # App Service Plan
            safe_property(obj, "server_farm_id",
                          props.get("serverFarmId", ""))

            # Availability state
            safe_property(obj, "availability_state",
                          props.get("availabilityState", ""))

            # Last modified
            safe_property(obj, "last_modified_time",
                          props.get("lastModifiedTimeUtc", ""))

            # Outbound IPs
            safe_property(obj, "outbound_ip_addresses",
                          props.get("outboundIpAddresses", ""))

            # Tags
            tags = app.get("tags", {})
            if tags:
                for key, value in tags.items():
                    safe_property(obj, f"tag_{key}", value)

            # Relationship: App -> Resource Group
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

        total += len(apps)

    logger.info("Collected %d app services", total)
