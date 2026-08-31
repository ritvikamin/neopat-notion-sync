# NeoPAT → Notion Placement Sync

Automatically fetch placement drives from NeoPAT, normalize the placement data, and sync it into a Notion Job Application Tracker.

The project can be run locally for development/testing and can also be executed automatically through GitHub Actions using a self-hosted Windows runner.

## Features

- Fetch placement drives from NeoPAT
- Handle pagination automatically
- Normalize raw NeoPAT placement data
- Extract the highest available CTC
- Use `TBA` when compensation information is unavailable or too complex
- Sync placement data into an existing Notion database
- Prevent duplicate entries using the NeoPAT `drive_id`
- Update existing Notion entries instead of creating duplicates
- Store credentials securely using `.env` locally and GitHub Secrets in Actions
- Support manual GitHub Actions execution
- Support scheduled automatic synchronization
- Execute GitHub Actions jobs on a local Windows machine using a self-hosted runner

## Architecture

```text
                         GitHub
                           │
                           │ Workflow trigger
                           ▼
                GitHub Actions Workflow
                           │
                           ▼
                  Self-Hosted Runner
                    (Windows PC)
                           │
                           ▼
                    Python Application
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
          NeoPAT API                Notion API
              │                         │
              ▼                         ▼
      Placement Drives          Job Application Tracker
```

GitHub controls and dispatches the workflow, but the Python code actually runs on the configured Windows self-hosted runner.

---

## Project Structure

```text
neopat-notion-sync/
│
├── app/
│   ├── neopat.py
│   ├── normalizer.py
│   ├── notion.py
│   └── sync.py
│
├── .github/
│   └── workflows/
│       └── sync.yml
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# Requirements

- Windows
- Python 3.10+
- Git
- NeoPAT account
- Notion integration
- Existing Notion job application database
- GitHub repository
- Internet connection

For scheduled GitHub Actions execution, the self-hosted Windows machine must be:

- Powered on
- Connected to the internet
- Awake
- Running the GitHub Actions runner service

---

# 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd neopat-notion-sync
```

---

# 2. Create a Python Virtual Environment

Create the virtual environment:

```bash
python -m venv venv
```

Activate it on Windows.

### Command Prompt

```cmd
venv\Scripts\activate
```

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in the terminal.

---

# 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

# 4. Environment Variables

Create a `.env` file in the project root:

```env
NEOPAT_REFRESH_TOKEN=your_neopat_refresh_token
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id
NOTION_DATA_SOURCE_ID=your_notion_data_source_id
```

## Important

Never commit `.env` to GitHub.

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

The NeoPAT refresh token and Notion token are sensitive credentials. Treat them like passwords.

---

# 5. NeoPAT Authentication

`app/neopat.py` uses the NeoPAT refresh token to obtain an access token.

The refresh token is stored locally in `.env` during development.

The application refreshes the access token and then uses the access token to fetch placement drives.

Do not commit the refresh token to the repository.

If NeoPAT invalidates or expires the refresh token, it will need to be replaced/renewed according to NeoPAT's authentication process.

---

# 6. Notion Setup

The project syncs placement information into an existing Notion Job Application Tracker database.

The database used in the original setup contained:

| Property | Type |
|---|---|
| Company | Title |
| Position | Rich Text |
| Status | Multi Select |
| Application Date | Date |
| CTC | Rich Text |
| Next Action | Multi Select |
| Contact | Email |
| OA Date | Date |
| Mode | Select |

Your database can use different properties, but the property names/types expected by the code must match the implementation.

---

# 7. Create a Notion Integration

Create a Notion integration and obtain its API token.

Then share the Job Application Tracker database with the integration.

The integration needs permission to read and update the database.

Store the token in:

```env
NOTION_TOKEN=your_token
```

---

# 8. Notion Database ID and Data Source ID

The Notion page containing a database is not necessarily the database itself.

In the original setup, the Job Application Tracker was a page containing a child database. The database ID and data source ID were retrieved separately.

Store them in:

```env
NOTION_DATABASE_ID=...
NOTION_DATA_SOURCE_ID=...
```

`app/notion.py` can be used to inspect the Notion structure and properties during setup.

---

# 9. NeoPAT Scraper

`app/neopat.py` is responsible for communicating with NeoPAT.

It:

1. Refreshes the access token
2. Fetches placement drives
3. Handles pagination
4. Returns the placement data

Example:

```text
Fetched page 1: 12 drives
Fetched page 2: 12 drives
Fetched page 3: 12 drives
Fetched page 4: 12 drives
Fetched page 5: 12 drives
Fetched page 6: 3 drives

Total drives: 63
```

The number of drives will change as NeoPAT data changes.

Run it locally:

```bash
python -m app.neopat
```

---

# 10. Normalization

`app/normalizer.py` converts the raw NeoPAT response into a simpler structure used by the sync process.

Example:

```python
{
    "drive_id": "...",
    "company_name": "Groww",
    "ctc": "26 LPA",
    "application_deadline": "2026-07-04"
}
```

## CTC Handling

If a placement contains multiple roles:

```text
Full Stack Intern: 25 LPA
Product Analyst Intern: 10 LPA
```

the normalizer takes the highest interpretable value:

```text
25 LPA
```

If the salary information cannot be reliably interpreted, it uses:

```text
TBA
```

This avoids displaying a potentially misleading value.

Run the normalizer test:

```bash
python -m app.normalizer
```

---

# 11. Notion Sync

`app/notion.py` handles communication with Notion.

Placements are identified using the NeoPAT:

```text
drive_id
```

If a placement already exists, the existing Notion page is updated.

If it does not exist, a new page is created.

This prevents duplicate pages when the sync runs repeatedly.

Example behavior:

```text
Placement already exists
```

or:

```text
Created Notion page
```

Run the Notion module:

```bash
python -m app.notion
```

---

# 12. Main Sync Process

`app/sync.py` coordinates the entire pipeline.

```text
Start
  │
  ▼
Refresh NeoPAT access token
  │
  ▼
Fetch placement drives
  │
  ▼
Normalize placement data
  │
  ▼
Query existing Notion applications
  │
  ▼
For each NeoPAT placement
  │
  ├── Exists → Update Notion page
  │
  └── New    → Create Notion page
  │
  ▼
Sync complete
```

Run the complete sync locally:

```bash
python -m app.sync
```

Example successful output:

```text
Starting placement sync

[1/63] Updated
[2/63] Updated
...
[63/63] Updated

Sync complete | Created: 0 | Updated: 63 | Failed: 0
```

---

# 13. GitHub Actions

The workflow is located at:

```text
.github/workflows/sync.yml
```

The workflow uses a self-hosted runner:

```yaml
runs-on: self-hosted
```

It also supports manual execution:

```yaml
workflow_dispatch:
```

---

# 14. GitHub Secrets

Go to:

```text
GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
```

Add these repository secrets:

```text
NEOPAT_REFRESH_TOKEN
NOTION_TOKEN
NOTION_DATABASE_ID
NOTION_DATA_SOURCE_ID
```

Do not put the actual values directly into `sync.yml`.

The workflow passes them to Python as environment variables:

```yaml
env:
  NEOPAT_REFRESH_TOKEN: ${{ secrets.NEOPAT_REFRESH_TOKEN }}
  NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
  NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
  NOTION_DATA_SOURCE_ID: ${{ secrets.NOTION_DATA_SOURCE_ID }}
```

---

# 15. Self-Hosted GitHub Actions Runner

The self-hosted runner is used because NeoPAT may reject requests coming from GitHub-hosted infrastructure.

Instead of:

```text
GitHub
  ↓
GitHub-hosted Ubuntu machine
  ↓
NeoPAT
```

the setup uses:

```text
GitHub
  ↓
Self-hosted runner
  ↓
Your Windows PC
  ↓
NeoPAT
```

This makes the actual API request originate from the local Windows machine.

---

# 16. Install the Self-Hosted Runner

Go to:

```text
GitHub Repository
→ Settings
→ Actions
→ Runners
→ New self-hosted runner
```

Select:

```text
Windows
x64
```

GitHub will provide the exact download and configuration commands.

Create the runner directory:

```powershell
mkdir C:\actions-runner
cd C:\actions-runner
```

Download and extract the runner using the commands supplied by GitHub.

Configure it:

```powershell
.\config.cmd
```

### Runner group

Use:

```text
Default
```

by pressing Enter.

### Runner name

Example:

```text
neopat-runner
```

### Labels

Keep the default labels:

```text
self-hosted
Windows
X64
```

### Work folder

Use the default:

```text
_work
```

---

# 17. Install the Runner as a Windows Service

During runner configuration, choose:

```text
Y
```

when asked:

```text
Would you like the runner as a service?
```

The runner service will then start automatically with Windows.

You do not need to keep a terminal open.

Check the service:

```powershell
Get-Service "actions.runner.<OWNER>-<REPO>.<RUNNER_NAME>"
```

Expected:

```text
Status
------
Running
```

If the runner service is running and the PC is online, GitHub can send jobs to it.

---

# 18. System-Wide Python

The self-hosted runner runs as a Windows service and may not have access to a developer's user-level Python installation or activated virtual environment.

For the runner, install Python system-wide.

Example location:

```text
C:\Program Files\Python310\
```

Add these directories to the **System PATH**:

```text
C:\Program Files\Python310
C:\Program Files\Python310\Scripts
```

Verify from a new terminal:

```powershell
where.exe python
```

and:

```powershell
python --version
```

Example:

```text
C:\Program Files\Python310\python.exe
Python 3.10.11
```

If the system PATH is changed after the runner service starts, restart the service:

```powershell
Restart-Service "actions.runner.<OWNER>-<REPO>.<RUNNER_NAME>"
```

The local development `venv` is separate from the Python installation used by the self-hosted runner.

---

# 19. GitHub Actions Workflow

A typical `sync.yml` is:

```yaml
name: NeoPAT Placement Sync

on:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

jobs:
  sync:
    runs-on: self-hosted

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Check Python
        run: |
          python --version
          python -m pip --version

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt

      - name: Run placement sync
        env:
          NEOPAT_REFRESH_TOKEN: ${{ secrets.NEOPAT_REFRESH_TOKEN }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          NOTION_DATA_SOURCE_ID: ${{ secrets.NOTION_DATA_SOURCE_ID }}
        run: |
          python -m app.sync
```

---

# 20. Scheduling

The workflow supports manual and scheduled execution.

Manual:

```yaml
workflow_dispatch:
```

Scheduled:

```yaml
schedule:
  - cron: "0 4 * * *"
```

GitHub Actions cron uses UTC.

For example:

```text
0 4 * * *
```

runs at:

```text
04:00 UTC
09:30 IST
```

GitHub may occasionally start scheduled workflows later than the exact cron time.

To change the schedule, edit the cron expression in `sync.yml`.

---

# 21. Requirements for Scheduled Runs

Because the workflow uses a self-hosted runner, the runner machine must be available.

At the scheduled time, the Windows PC should be:

- Powered on
- Connected to the internet
- Awake
- Running the runner service

You do **not** need:

- VS Code open
- PowerShell open
- Command Prompt open
- The local Python `venv` activated

The runner service operates in the background.

---

# 22. What Happens During an Automated Run

```text
GitHub scheduler
       │
       ▼
Workflow triggered
       │
       ▼
GitHub finds self-hosted runner
       │
       ▼
Windows PC receives job
       │
       ▼
Repository checked out
       │
       ▼
System Python executes
       │
       ▼
Dependencies installed
       │
       ▼
python -m app.sync
       │
       ├───────────────┐
       ▼               ▼
    NeoPAT          Notion
       │               │
       └───────┬───────┘
               ▼
          Sync complete
```

The runner checks out the code from the GitHub repository. It does not execute whatever code happens to be in the developer's local VS Code folder.

---

# 23. Manual GitHub Workflow Trigger

To test the automation manually:

1. Go to **GitHub → Actions**
2. Select **NeoPAT Placement Sync**
3. Click **Run workflow**
4. Select `main`
5. Click **Run workflow**
6. Open the new run
7. Open the `sync` job

A successful run should show:

```text
Starting placement sync
...
Sync complete | Created: X | Updated: Y | Failed: 0
```

---

# 24. Troubleshooting

## `python` is not recognized

Run:

```powershell
where.exe python
```

Verify that the System PATH contains:

```text
C:\Program Files\Python310
C:\Program Files\Python310\Scripts
```

Restart the runner service:

```powershell
Restart-Service "actions.runner.<OWNER>-<REPO>.<RUNNER_NAME>"
```

---

## Workflow uses `/home/runner`

If logs contain:

```text
/home/runner/work/
```

the workflow is using a GitHub-hosted Linux runner.

The workflow should contain:

```yaml
runs-on: self-hosted
```

A Windows self-hosted runner should show paths similar to:

```text
C:\actions-runner\_work\
```

---

## `actions/setup-python` causes Windows permission errors

For this setup, `actions/setup-python` is not required because Python is installed system-wide on the self-hosted machine.

Use:

```yaml
python --version
```

and:

```yaml
python -m app.sync
```

instead.

This avoids requiring the runner service account to modify the Windows registry.

---

## NeoPAT returns HTTP 403

First check whether the workflow is actually running on the self-hosted runner.

The runner should be visible under:

```text
Repository
→ Settings
→ Actions
→ Runners
```

with status:

```text
Idle
```

or:

```text
Busy
```

If the logs show:

```text
/home/runner/
```

the workflow is still running on GitHub's hosted infrastructure.

If the workflow is definitely running locally and NeoPAT still returns 403, check the refresh token and NeoPAT authentication state.

---

## Notion returns an error

Verify:

- `NOTION_TOKEN`
- `NOTION_DATABASE_ID`
- `NOTION_DATA_SOURCE_ID`
- The Notion integration has access to the database
- Property names and types match the code

---

## Duplicate Notion entries

The sync identifies placements using the NeoPAT `drive_id`.

Intended behavior:

```text
Existing drive_id
      ↓
Update existing Notion page
```

New placement:

```text
New drive_id
      ↓
Create new Notion page
```

If duplicate rows already exist from older manual entries, they may need to be cleaned up manually. Manual company names may not exactly match NeoPAT company names, so deleting duplicates based only on company name can be unreliable.

---

# 25. Security

Never commit:

```text
.env
```

Never commit:

- NeoPAT refresh tokens
- Notion API tokens
- Any other API credentials

Use:

```text
Local development
→ .env

GitHub Actions
→ GitHub Secrets
```

Sensitive values should never appear directly in source code or workflow files.

If a secret is accidentally committed, rotate/revoke it immediately.

---

# 26. Development Workflow

Create a feature branch:

```bash
git checkout -b feature/my-change
```

Make changes and test locally:

```bash
python -m app.sync
```

Then:

```bash
git add .
git commit -m "feat: description"
git push
```

Create a Pull Request:

```text
feature/my-change
        ↓
      main
```

Merge the PR into `main`.

GitHub Actions will then use the code from the updated GitHub repository.

---

# 27. Git Workflow Used by This Project

A typical change follows:

```text
Local changes
     ↓
git add
     ↓
git commit
     ↓
git push feature branch
     ↓
Pull Request
     ↓
Merge into main
     ↓
GitHub Actions
```

Avoid committing secrets or local environment files.

---

# 28. Data Synced

For each placement drive, the current normalization layer produces:

```text
NeoPAT Drive ID
Company Name
CTC
Application Deadline
```

Example:

```python
{
    "drive_id": "dbc971fc-730f-4dd6-997a-f68750575db7",
    "company_name": "Groww",
    "ctc": "26 LPA",
    "application_deadline": "2026-07-04"
}
```

---

# 29. Successful Sync Example

A successful run can look like:

```text
Starting placement sync

[1/63] Updated
[2/63] Updated
...
[63/63] Updated

Sync complete | Created: 0 | Updated: 63 | Failed: 0
```

Meaning:

```text
Created = New Notion pages
Updated = Existing Notion pages updated
Failed  = Placements that could not be synced
```

The number of placements will change as NeoPAT data changes.

---

# 30. Future Improvements

Possible improvements:

- Better CTC parsing
- Sync additional placement fields
- Detect closed/cancelled drives
- Add more detailed Notion properties
- Improve retry handling
- Log failed placements separately
- Send notifications when new placements appear
- Handle refresh-token expiration more gracefully
- Improve scheduled-run reliability
- Use a dedicated always-on machine for the self-hosted runner
- Add automated tests
- Add CI checks before merging

---

# License

Add your preferred license here.

If this project is intended only for personal/college use, you can leave the repository without a license.
