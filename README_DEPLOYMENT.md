# Deployment Instructions for Vercel

This project can be deployed to Vercel using the following steps:

1. Push your code to a GitHub repository (already done).

2. Go to [Vercel](https://vercel.com/) and sign up or log in.

3. Click on "New Project" and import your GitHub repository.

4. Vercel will detect the `vercel.json` configuration file and set up the Python backend deployment.

5. Configure any environment variables if needed in the Vercel dashboard.

6. Click "Deploy" to start the deployment process.

7. Once deployed, Vercel will provide a URL where your app is accessible.

Note: The `vercel.json` file routes all requests to `SourceCode/app.py` which is the Python backend entry point.

If you want to deploy static files or frontend separately, configure accordingly in Vercel.

For more details, refer to the [Vercel Python documentation](https://vercel.com/docs/runtimes/python).
