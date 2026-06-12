# GitHub Actions Workflows

This directory contains automated workflows for maintaining the documentation.

## Sync Kubex Automation Engine Changelog

**File:** `workflows/sync-changelog.yml`

### What it does
Automatically syncs the Kubex Automation Engine CHANGELOG from the upstream helm-charts repository into the Release Notes documentation.

### When it runs
- **Automatically:** Daily at 2 AM UTC
- **Manually:** Can be triggered from the Actions tab in GitHub

### How it works
1. Fetches the latest CHANGELOG.md from: `https://github.com/densify-dev/helm-charts/blob/master/charts/kubex-automation-engine/CHANGELOG.md`
2. Converts the changelog format to Mintlify MDX accordion format
3. Updates the Release Notes file: `docs/WebHelp_Densify_Cloud/Content/Release_Notes/New_Features_Cloud.mdx`
4. Creates a pull request if changes are detected
5. PR includes labels `documentation` and `automated` for easy filtering

### Manual trigger
To manually run the sync:
1. Go to the **Actions** tab in GitHub
2. Select **Sync Kubex Automation Engine Changelog** workflow
3. Click **Run workflow**

### Testing locally
To test the sync script locally:

```bash
python3 .github/scripts/sync-changelog.py
```

### Customization
To change the sync schedule, edit the cron expression in `sync-changelog.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Cron examples:
- `0 2 * * *` - Daily at 2 AM UTC
- `0 2 * * 1` - Weekly on Monday at 2 AM UTC
- `0 */6 * * *` - Every 6 hours

### Source URL
The workflow syncs from this URL:
https://github.com/densify-dev/helm-charts/blob/master/charts/kubex-automation-engine/CHANGELOG.md

To change the source, update the `CHANGELOG_URL` variable in `scripts/sync-changelog.py`.
