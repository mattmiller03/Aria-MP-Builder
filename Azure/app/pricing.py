"""Azure Retail Prices API client for dedicated host hourly rates.

The Retail Prices API (https://prices.azure.com/api/retail/prices) is
public — no authentication required. It serves pricing for both
commercial and government cloud SKUs.

If the API is unreachable (e.g., air-gapped environments), the module
falls back to a hardcoded pricing table in FALLBACK_PRICES.

Note: This endpoint is on commercial Azure infrastructure. The Cloud
Proxy must be able to reach prices.azure.com over HTTPS.
"""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"

# ---------------------------------------------------------------------------
# Fallback pricing table — Azure Gov dedicated host hourly rates (USD)
# Source: https://azure.microsoft.com/en-us/pricing/details/virtual-machines/dedicated-host/
# Last updated: 2026-04-10
#
# Update these when SKUs or pricing change. The API will be used
# preferentially when reachable; these are the air-gapped fallback.
# ---------------------------------------------------------------------------
FALLBACK_PRICES = {
    # Azure Gov (usgovvirginia) — fetched 2026-04-10 via fetch_pricing.py
    # DCadsv6 family
    "DCadsv6_Type1": 11.4840,
    # DCasv6 family
    "DCasv6_Type1": 9.1080,
    # DCsv2 family
    "DCsv2 Type 1": 1.0560,
    # Dadsv5 family
    "Dadsv5_Type1": 8.0700,
    # Dasv4 family
    "Dasv4_Type1": 6.6550,
    "Dasv4_Type2": 6.6550,
    # Dasv5 family
    "Dasv5_Type1": 6.7140,
    # Dasv6 family
    "Dasv6_Type1": 9.1080,
    # Ddsv4 family
    "Ddsv4_Type 1": 5.0340,
    "Ddsv4_Type2": 5.9770,
    # Dsv3 family
    "Dsv3_Type1": 4.2600,
    "Dsv3_Type2": 4.7930,
    "Dsv3_Type3": 5.3250,
    "Dsv3_Type4": 6.6560,
    # Dsv4 family
    "Dsv4_Type1": 5.3240,
    "Dsv4_Type2": 6.6550,
    # Dsv6 family
    "Dsv6_Type1": 13.3060,
    # ECadsv6 family
    "ECadsv6_Type1": 14.5730,
    # ECasv6 family
    "ECasv6_Type1": 11.9750,
    # Easv4 family
    "Easv4_Type1": 7.9730,
    "Easv4_Type2": 7.9730,
    # Easv6 family
    "Easv6_Type1": 11.9790,
    # Ebdsv5 family
    "Ebdsv5-Type1": 7.1100,
    # Ebsv5 family
    "Ebsv5-Type1": 6.3360,
    # Edsv4 family
    "Edsv4_Type 1": 6.3360,
    "Edsv4_Type2": 7.5240,
    # Esv3 family
    "Esv3_Type1": 4.6500,
    "Esv3_Type2": 5.1480,
    "Esv3_Type3": 5.1480,
    "Esv3_Type4": 6.9740,
    # Esv4 family
    "Esv4_Type1": 5.2830,
    "Esv4_Type2": 6.9340,
    # FXmds family
    "FXmds Type1": 1.2276,
    # Fsv2 family
    "Fsv2 Type3": 5.1610,
    "Fsv2_Type2": 4.0390,
    "Fsv2_Type4": 5.6100,
    # Lsv2 family
    "Lsv2_Type1": 8.2720,
    # Lsv3 family
    "Lsv3_Type1": 9.0990,
    # Mdmsv2MedMem family
    "Mdmsv2MedMem _Type1": 35.2310,
    # Mdsv2MedMem family
    "Mdsv2MedMem_Type1": 17.6090,
    # Mmsv2MedMem family
    "Mmsv2MedMem-Type1": 34.6752,
    # Ms family
    "Ms_Type1": 17.6030,
    # Msm family
    "Msm_Type1": 35.2360,
    # Msmv2 family
    "Msmv2_Type1": 136.3300,
    # Msv2 family
    "Msv2_Type1": 68.1730,
    # NVasv4 family
    "NVasv4_Type1": 8.9700,
    # NVsv3 family
    "NVsv3_Type1": 6.2700,
}


def get_dedicated_host_prices(region: str) -> dict:
    """Fetch hourly rates for all Dedicated Host SKUs in a given region.

    Tries the Azure Retail Prices API first. If unreachable or returns
    no results, falls back to the hardcoded FALLBACK_PRICES table.

    Args:
        region: Azure region name (e.g., "usgov virginia", "usgovvirginia").

    Returns:
        Dict mapping SKU name (e.g., "DSv3-Type1") to hourly USD rate.
    """
    # Try the live API first
    prices = _fetch_from_api(region)

    if prices:
        logger.info("Fetched %d dedicated host SKU prices from API for '%s'",
                     len(prices), region)
        return prices

    # Fall back to hardcoded table — expand with alternate name formats
    # so lookups work regardless of whether ARM returns "DSv3-Type1",
    # "Dsv3_Type1", or "Dsv3-Type1"
    fallback = {}
    for sku, rate in FALLBACK_PRICES.items():
        fallback[sku] = rate
        fallback[sku.replace("_", "-")] = rate
        fallback[sku.replace("-", "_")] = rate

    logger.info("Using fallback pricing table (%d SKUs) — API unavailable "
                "or returned no results for '%s'", len(FALLBACK_PRICES), region)
    return fallback


def _fetch_from_api(region: str) -> dict:
    """Attempt to fetch pricing from the Azure Retail Prices API.

    Returns:
        Dict of {sku_name: hourly_rate}, or empty dict on failure.
    """
    prices = {}

    # OData filter for Dedicated Host consumption prices in the region
    # Dedicated hosts are under serviceName 'Virtual Machines' with
    # productName containing 'Dedicated Host'
    odata_filter = (
        f"serviceName eq 'Virtual Machines' "
        f"and contains(productName, 'Dedicated Host') "
        f"and armRegionName eq '{region}' "
        f"and priceType eq 'Consumption'"
    )

    url = RETAIL_PRICES_URL
    params = {"$filter": odata_filter}

    try:
        while url:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get("Items", []):
                sku_name = item.get("armSkuName", "")
                unit_price = item.get("unitPrice", 0.0)
                unit_of_measure = item.get("unitOfMeasure", "")

                # Only take hourly rates, skip reserved/spot
                if sku_name and unit_of_measure == "1 Hour":
                    # Normalize SKU: API returns "Dsv3_Type2",
                    # ARM returns "DSv3-Type2". Store both forms.
                    hyphen_name = sku_name.replace("_", "-")

                    # Prefer the lowest non-zero price (base pay-as-you-go)
                    for name in (sku_name, hyphen_name):
                        if name not in prices or (
                            unit_price > 0 and unit_price < prices[name]
                        ):
                            prices[name] = unit_price

            # Follow pagination
            next_link = data.get("NextPageLink")
            if next_link:
                url = next_link
                params = {}  # NextPageLink includes query params
            else:
                url = None

    except Exception as e:
        logger.warning("Retail Prices API unreachable: %s", e)

    return prices


def get_all_dedicated_host_prices(regions: list) -> dict:
    """Fetch dedicated host prices across multiple regions.

    Args:
        regions: List of Azure region names.

    Returns:
        Dict mapping (region, sku_name) to hourly USD rate.
    """
    all_prices = {}
    seen_regions = set()

    for region in regions:
        region_lower = region.lower()
        if region_lower in seen_regions:
            continue
        seen_regions.add(region_lower)

        region_prices = get_dedicated_host_prices(region_lower)
        for sku_name, rate in region_prices.items():
            all_prices[(region_lower, sku_name)] = rate

    return all_prices
