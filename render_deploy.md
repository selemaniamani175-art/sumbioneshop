# SumbioneShop Render Deployment

Target Render service name: `sumbioneshop`
Target URL: `https://sumbioneshop.onrender.com`

## Deploy
1. Create a GitHub repository and upload this project.
2. In Render choose **New → Blueprint** and connect the GitHub repository.
3. Render reads `render.yaml` and creates the web service and PostgreSQL database.
4. Wait for the build to finish.
5. Open `https://sumbioneshop.onrender.com`.
6. In the Render Shell run:
   `python manage.py createsuperuser`
7. Log in and create the business users/products/customers.

## Important
The free Render plan is suitable for testing/demo use. Free web services sleep after inactivity and their local filesystem is ephemeral. The app is configured for PostgreSQL rather than SQLite online so business data is not stored on the web service filesystem.

If the exact `sumbioneshop.onrender.com` hostname is unavailable because another Render service already uses it, choose another unique service name; Render generates the `onrender.com` subdomain from the service name.
