#!/usr/bin/env python3
"""
Sync Kubex Automation Engine CHANGELOG from upstream repository.
"""

import re
import requests
from pathlib import Path

# Configuration
CHANGELOG_URL = "https://raw.githubusercontent.com/densify-dev/helm-charts/master/charts/kubex-automation-engine/CHANGELOG.md"
RELEASE_NOTES_FILE = "docs/WebHelp_Densify_Cloud/Content/Release_Notes/release_notes_k8s_automation_engine.mdx"

# Markers to identify the section to replace
START_MARKER = "## Kubex Automation Engine"
LEGACY_MARKER = "### Legacy Kubex Automation Controller Release Notes"


def fetch_changelog():
    """Fetch the CHANGELOG from upstream repository."""
    print(f"Fetching CHANGELOG from {CHANGELOG_URL}")
    response = requests.get(CHANGELOG_URL, timeout=30)
    response.raise_for_status()
    return response.text


def parse_changelog_entry(version_block):
    """Parse a single version entry from the CHANGELOG."""
    # Extract version and date from header like: ## [1.4.0] - 2026-06-11
    header_match = re.match(r'^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})', version_block)
    if not header_match:
        return None

    version = header_match.group(1)
    date_str = header_match.group(2)

    # Convert date to readable format
    from datetime import datetime
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%B %d, %Y')

    # Extract content (everything after the header line)
    lines = version_block.split('\n')
    content_lines = []

    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped == '---':
            continue

        # Handle markdown h3 section headers - convert to bold text (no markdown headers allowed in accordions)
        if stripped.startswith('### Added'):
            # Add blank line before new section (except first)
            if content_lines:
                content_lines.append('')
            content_lines.append('**Added:**')
        elif stripped.startswith('### Changed'):
            if content_lines:
                content_lines.append('')
            content_lines.append('**Changed:**')
        elif stripped.startswith('### Fixed'):
            if content_lines:
                content_lines.append('')
            content_lines.append('**Fixed:**')
        else:
            # Regular content line - keep list items as-is
            content_lines.append(stripped)

    # Join with proper indentation - preserve empty lines for spacing
    formatted_lines = []
    for line in content_lines:
        formatted_lines.append(line)

    content = '\n    '.join(formatted_lines).strip()

    # Create a title for the accordion
    title_parts = []
    if '**Added:**' in content:
        # Extract first Added item as title
        added_match = re.search(r'\*\*Added:\*\* ([^\n]+)', content)
        if added_match:
            title_parts.append(added_match.group(1))

    if not title_parts:
        title_parts.append("Updates and Improvements")

    title = title_parts[0][:60]  # Truncate if too long

    return {
        'version': version,
        'date': formatted_date,
        'title': title,
        'content': content
    }


def convert_changelog_to_mdx(changelog_text):
    """Convert CHANGELOG markdown to Mintlify MDX accordion format."""
    # Split into version blocks
    version_blocks = re.split(r'^## ', changelog_text, flags=re.MULTILINE)[1:]

    mdx_sections = []

    for block in version_blocks:
        # Add back the ## that was removed by split
        block = '## ' + block
        entry = parse_changelog_entry(block)

        if entry:
            accordion = f'''<Accordion title="{entry['version']} - {entry['date']}">
  <Accordion title="{entry['title']}">
    {entry['content']}
  </Accordion>
</Accordion>'''
            mdx_sections.append(accordion)

    return '\n\n'.join(mdx_sections)


def update_release_notes(new_content):
    """Update the release notes file with new CHANGELOG content."""
    file_path = Path(RELEASE_NOTES_FILE)

    if not file_path.exists():
        print(f"Error: {RELEASE_NOTES_FILE} not found")
        return False

    # Read current content
    current_content = file_path.read_text(encoding='utf-8')

    # Find the section to replace
    start_idx = current_content.find(START_MARKER)
    legacy_idx = current_content.find(LEGACY_MARKER, start_idx)

    if start_idx == -1 or legacy_idx == -1:
        print("Error: Could not find markers in release notes file")
        return False

    # Build new content - just the header and changelog, no note
    header = '''## Kubex Automation Engine

'''

    new_section = header + new_content + '\n\n'

    # Replace the section
    before = current_content[:start_idx]
    after = current_content[legacy_idx:]

    # Add the deprecation note to the legacy section header
    legacy_with_note = '''### Legacy Kubex Automation Controller Release Notes

<Note>
The Kubex Automation Controller has been deprecated and replaced by the Kubex Automation Engine.
</Note>

'''

    # Replace just the legacy header line with header + note
    after = after.replace(LEGACY_MARKER + '\n\n', legacy_with_note)

    updated_content = before + new_section + after

    # Write back
    file_path.write_text(updated_content, encoding='utf-8')
    print(f"Updated {RELEASE_NOTES_FILE}")
    return True


def main():
    """Main execution."""
    try:
        # Fetch changelog
        changelog = fetch_changelog()

        # Convert to MDX format
        mdx_content = convert_changelog_to_mdx(changelog)

        # Update release notes file
        if update_release_notes(mdx_content):
            print("Sync completed successfully")
            return 0
        else:
            print("Sync failed")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
