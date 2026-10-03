# ercol Outlet dining monitor

Checks the ercol Outlet every 30 minutes and emails you when a new dining table or dining chair is listed.

## Setup (about 10 minutes)
1. **Gmail app password**: turn on 2-Step Verification on your Google account, then go to
   myaccount.google.com/apppasswords and create one. Copy the 16-character password.
2. **Create a GitHub repo** (public keeps Actions unlimited and free) and upload `monitor.py`,
   `README.md` and the `.github/workflows/monitor.yml` file, keeping that folder path.
3. **Add secrets**: repo Settings > Secrets and variables > Actions > New repository secret:
   - `SMTP_USER`: your Gmail address
   - `SMTP_PASSWORD`: the app password
   - `EMAIL_TO`: where alerts go (optional; defaults to SMTP_USER)
4. **Run it once**: Actions tab > "ercol outlet monitor" > Run workflow. The first run records
   current stock without emailing. From then on you only get emails for new listings.

## Notes
- Edit the exclude lists at the top of `monitor.py` to fine-tune what counts as dining.
- If the page layout changes, the run fails and GitHub emails you about the failed workflow.
- GitHub may pause schedules on repos with no activity for 60 days; re-enable from the Actions tab if so.
- Not using Gmail? Set an `SMTP_HOST` secret and add it to the workflow env.
