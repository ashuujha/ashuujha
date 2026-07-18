# GitHub Profile Setup & Automation Guide

This document describes how to deploy, configure, and maintain your premium developer dashboard.

## 📁 Repository Structure

```
.
├── .github/
│   └── workflows/
│       ├── profile.yml         # Main automation workflow (runs scripts, commits updates)
│       └── snake.yml           # Generates contribution grid snake animation
├── assets/
│   ├── avatar.png              # Cached GitHub avatar
│   ├── ascii_art.txt           # Generated grayscale ASCII art
│   ├── header.svg              # CSS Typing animation header
│   ├── terminal.svg            # Side-by-side Terminal Card SVG
│   └── github-contribution-grid-snake.svg # Generated contribution snake
├── scripts/
│   ├── generate_ascii.py       # Converts avatar to ASCII
│   ├── fetch_stats.py          # Queries GitHub API for details
│   ├── generate_neofetch.py    # Merges ASCII + stats into terminal card
│   └── update_readme.py        # Compiles README from template
├── doc/
│   ├── README.template.md      # Template containing structural tags
│   └── SETUP.md                # This setup guide (port details & dispatches)
├── README.md                   # Generated final profile page
└── config.json                 # Custom profile configuration parameters
```

---

## ⚙️ Step-by-Step Setup

### Step 1: Create a Personal Access Token (PAT)
To enable the profile updater to fetch search statistics (like total commits, pull requests, issues) and trigger updates from other repositories, you need a Personal Access Token (Classic).

1. Go to your GitHub Settings -> **Developer Settings** -> **Personal Access Tokens** -> **Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Set the name to `GH_PAT_PROFILE`.
4. Select the following scopes:
   - `repo` (Full control of private and public repositories)
   - `workflow` (Update GitHub Actions workflows)
5. Generate the token and copy the value immediately.

### Step 2: Add Secrets to Your Profile Repository
In your `ashuujha/ashuujha` repository:
1. Go to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret**.
3. Name: `GH_PAT` (or `GH_TOKEN`).
4. Value: Paste your Personal Access Token.
5. Click **Add secret**.

### Step 3: Trigger Updates from ALL Other Repositories
To automatically update your profile README whenever you push code to *any* of your other repositories:

1. Create a workflow file `.github/workflows/trigger_profile.yml` in each of your other active repositories.
2. Paste the following configuration:
   ```yaml
   name: Trigger Profile Update

   on:
     push:
       branches:
         - main
         - master

   jobs:
     notify:
       runs-on: ubuntu-latest
       steps:
         - name: Emit Repository Dispatch
           uses: peter-evans/repository-dispatch@v3
           with:
             token: ${{ secrets.GH_PAT }}
             repository: ashuujha/ashuujha
             event-type: repo-update
   ```
3. Make sure to add the same `GH_PAT` secret to those repositories as well. Whenever you push to those repositories, it will trigger the `repo-update` event, which automatically updates the profile dashboard!

### Step 4: Configure WakaTime Integration
To enable coding analytics:
1. Sign up on [WakaTime](https://wakatime.com) if you haven't already.
2. In your WakaTime account settings, enable displaying your coding statistics publicly.
3. In `config.json` in your profile repository, make sure `"wakatime_username"` matches your WakaTime username.

---

## 🛠️ Customization Guide

You can customize almost everything by editing `config.json` in the root of the repository:
- **`typing_texts`**: Add/remove lines that type out letter-by-letter in the header.
- **`about`**: Add professional descriptions of your work.
- **`socials`**: Add your actual profiles (they will automatically show up as terminal ports).
- **`tech_stack`**: Add/remove technologies. They will render as clean, modern HTML `<kbd>` labels matching GitHub's native style.

---

## 🔧 Troubleshooting & FAQ

#### The workflow runs but doesn't commit anything
The commit step compares the newly compiled files with existing ones. If nothing changed, it will exit gracefully without making a commit to avoid commit spam.

#### API Rate Limit errors
The scripts will run under your token if `GH_PAT` is provided, which gives you 5,000 API requests per hour. If the token is invalid or missing, it will use public REST endpoints (60 requests per hour), which may result in rate-limit failures in busy environments. Always verify your `GH_PAT` is set up correctly in Secrets.
