"""Scrub sensitive data from log files before committing.

Usage:
    python scrub.py <input_file> [output_file]

If no output file is specified, overwrites the input file.
Add your hostnames, IPs, and other sensitive strings to the
REPLACEMENTS dict below.
"""

import re
import sys

# ============================================================
# Add your sensitive values here — these get replaced
# ============================================================
REPLACEMENTS = {
    # Hostnames
    "DAISV0TP003": "ARIAOPS-NODE",
    "DAISV0TP004": "CLOUD-PROXY",
    "daisv0tp003": "ariaops-node",
    "daisv0tp004": "cloud-proxy",

    # IPs — add your actual IPs here
    "214.73.76.134": "MP-BUILDER-IP",
    "214.73.76.149": "CLOUD-PROXY-IP",
    # "10.x.x.x": "INTERNAL-IP",

    # Usernames
    "vropsssh": "svcaccount",

    # Azure tenant/subscription — add if needed
    # "6dee1d83-8de8-49bb-bc0d-fd8812473904": "TENANT-ID",
    # "988779d0-a914-4d28-8db2-56ae35c26853": "SUB-ID",
    # "a3e73c56-50f4-401e-8695-791bc44afed5": "SUB-ID-2",
}


def scrub(text):
    for sensitive, placeholder in REPLACEMENTS.items():
        text = text.replace(sensitive, placeholder)

    # Also catch any IP addresses not in the list (x.x.x.x pattern)
    # Uncomment the next line to replace ALL IPs:
    # text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'X.X.X.X', text)

    return text


def main():
    if len(sys.argv) < 2:
        print("Usage: python scrub.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    scrubbed = scrub(content)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(scrubbed)

    print(f"Scrubbed {len(REPLACEMENTS)} patterns in {input_file} -> {output_file}")


if __name__ == "__main__":
    main()
