"""Azure Retail Prices API client for dedicated host hourly rates.

The Retail Prices API (https://prices.azure.com/api/retail/prices) is
public — no authentication required. It serves pricing for both
commercial and government cloud SKUs.

Note: This endpoint is on commercial Azure infrastructure. The Cloud
Proxy must be able to reach prices.azure.com over HTTPS.
"""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"


def get_dedicated_host_prices(region: str) -> dict:
    """Fetch hourly rates for all Dedicated Host SKUs in a given region.

    Args:
        region: Azure region name (e.g., "usgov virginia", "usgov arizona").

    Returns:
        Dict mapping SKU name (e.g., "DSv3-Type1") to hourly USD rate.
        Returns empty dict on failure.
    """
    prices = {}

    # OData filter for Dedicated Host consumption prices in the region
    odata_filter = (
        f"serviceName eq 'Virtual Machines Dedicated Host' "
        f"and armRegionName eq '{region}' "
        f"and priceType eq 'Consumption'"
    )

    url = RETAIL_PRICES_URL
    params = {"$filter": odata_filter}

    try:
        while url:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            for item in data.get("Items", []):
                sku_name = item.get("armSkuName", "")
                unit_price = item.get("unitPrice", 0.0)
                unit_of_measure = item.get("unitOfMeasure", "")

                # Only take hourly rates, skip reserved/spot
                if sku_name and unit_of_measure == "1 Hour":
                    # Prefer the lowest non-zero price (base pay-as-you-go)
                    if sku_name not in prices or (
                        unit_price > 0 and unit_price < prices[sku_name]
                    ):
                        prices[sku_name] = unit_price

            # Follow pagination
            next_link = data.get("NextPageLink")
            if next_link:
                url = next_link
                params = {}  # NextPageLink includes query params
            else:
                url = None

    except Exception as e:
        logger.warning("Failed to fetch dedicated host prices: %s", e)

    logger.info("Fetched %d dedicated host SKU prices for region '%s'",
                len(prices), region)
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
