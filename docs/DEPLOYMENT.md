# PythonAnywhere Deployment

Use these steps after pushing a new version to GitHub:

```bash
cd ~/metroclass
git pull origin main
~/metroclass/venv/bin/python manage.py migrate
~/metroclass/venv/bin/python manage.py collectstatic --noinput
```

Open the PythonAnywhere **Web** tab and select **Reload**. Then refresh the live website in the browser.

If the website shows an error, check the Error log from the Web tab before making another change.
