#!/usr/bin/env python3
"""Sync the Kubex automation stack Installation section into the docs."""

import re
from pathlib import Path
from urllib.request import Request, urlopen


SOURCE_URL = (
    "https://raw.githubusercontent.com/densify-dev/helm-charts/master/"
    "charts/kubex-automation-stack/README.md"
)
TARGET_FILE = Path("docs-kubex/Content/Kubex/Data_Collection_Overview.mdx")
START_MARKER = "{/* BEGIN KUBEX AUTOMATION STACK INSTALLATION */}"
END_MARKER = "{/* END KUBEX AUTOMATION STACK INSTALLATION */}"


def fetch_readme() -> str:
    request = Request(SOURCE_URL, headers={"User-Agent": "densify-docs-installation-sync"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_installation(readme: str) -> str:
    match = re.search(
        r"^## Installation\s*$.*?(?=^## \S|\Z)", readme, flags=re.MULTILINE | re.DOTALL
    )
    if not match:
        raise RuntimeError("Could not find the Installation section in the upstream README")

    section = match.group(0).rstrip()
    source_base = "https://github.com/densify-dev/helm-charts/blob/master/charts/kubex-automation-stack/"
    section = section.replace("[Sizing](#sizing)", "[Sizing](https://github.com/densify-dev/helm-charts/blob/master/charts/kubex-automation-stack/README.md#sizing)")
    section = section.replace("[Configuration](#configuration)", "[Configuration](https://github.com/densify-dev/helm-charts/blob/master/charts/kubex-automation-stack/README.md#configuration)")
    section = re.sub(r"\]\((values-edit\.yaml)\)", rf"]({source_base}\1)", section)
    return section


def update_target(installation: str) -> bool:
    current = TARGET_FILE.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r"\n.*?" + re.escape(END_MARKER),
        flags=re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{installation}\n{END_MARKER}"
    updated, count = pattern.subn(replacement, current, count=1)
    if count != 1:
        raise RuntimeError("Could not find the installation sync markers in the target MDX")
    if updated == current:
        print("Installation section is already up to date")
        return False
    TARGET_FILE.write_text(updated, encoding="utf-8")
    print(f"Updated {TARGET_FILE}")
    return True


if __name__ == "__main__":
    update_target(extract_installation(fetch_readme()))
