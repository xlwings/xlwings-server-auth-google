# Python backend for Google Sheets with FastAPI and xlwings

This is a sample repo with boilerplate code to build a FastAPI backend for Google Sheets, connected by xlwings PRO. It shows:

* How to authenticate users for a specific Google Workspace domain (previously called G Suite)
* How to access the user object
* How to authorize users based on their group membership. Groups can be queried from any service you like (e.g., Okta, Azure AD or LDAP), but this repo shows how to define them in environment variables or how to query Google Directory (see below under _Google Directory integration_).

NOTE: while this repo uses FastAPI, xlwings is framework-agnostic, so it's easy enough to swap FastAPI with your favorite tool, whether that's Django, Flask, etc.

## Instructions

1. Click one of the following buttons to deploy this repo to your favorite service:    
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

   [![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

2. You will be asked to provide two environment variables:
   * `XLWINGS_LICENSE_KEY`: visit https://www.xlwings.org/trial to get a free trial license for xlwings PRO. Note that xlwings PRO is free for non-commercial use, see: https://docs.xlwings.org/en/stable/pro.html
   * `GOOGLE_ALLOWED_DOMAINS`: type in your domain(s) that you use on Google Workspace in the form of a list, i.e., `["yourdomain.com"]`.
3. Once the server is up and running, open a new Google Sheet, go to `Extensions` > `Apps Script` and paste the content of `xlwings.js` into an Apps Script module. At the top, replace `URL` with the actual url of your backend. Now you can run the three functions: `hello1`, `hello2` and `hello3` that demonstrate the use of authentication and authorization.

NOTE:
* When you run your very first function in Apps Script, you will be asked for a few permissions.
* The `hello3` function will give you a permission error as its purpose is to demo authorization. To authorize yourself, go back to your server and add the env var `GROUP_ADMIN` with the following value `["you@yourdomain.com"]`. In Render, you will do that under `Dashboard` > `Environment`. Make sure to hit `Save Changes`, which will start a new deploy. Once deployed, try again: `hello3` will now work for you (but will continue to block anybody else of your Google Workspace organization).
* Instead of running the function directly in the Apps Script editor, you could draw a button on the sheet or build a Google Sheets extension.

## Local development

To develop locally, follow these steps:

* Copy `.env.template` to `.env` and fill in at least `XLWINGS_LICENSE_KEY` and `GOOGLE_ALLOWED_DOMAINS`. Note that `.env` is part of `.gitignore`.
* Run `pip install -r requirements.txt`
* Run the server with `python run.py`

To connect directly to Google Sheets, you can:

* Expose your local port via a tool like `ngrok`
* Develop in a cloud-based IDE like GitPod where you can easily expose a port

Alternatively, you could also develop against a local Desktop Excel version.

For more detailed information about all these options, see:  
https://docs.xlwings.org/en/stable/remote_interpreter.html

## Running tests

If you have gone through the steps under _local development_, you can run the tests as follows:  

* Install the additionally required packages by running `pip install -r requirements-dev.txt`.
* Run the tests by running the following command in your Terminal (in the root directory): `pytest`

You'll find the test configuration in `pyproject.toml`.

## Google Directory integration

To be able to use FastAPI's scope-based permissioning system in connection with your Google groups, you'll need to set up a GCP service account according to these instructions.

NOTE: this is only required if you want to query your groups from Google Directory (part of Google Workspace), it is **not** required if you only need authentication or would like to use a different directory service.

### Google Cloud Console (GCP)
1. Sign in to Google cloud console at https://console.cloud.google.com.
2. Double-check that you're logged in with the correct account on the top right.
3. Click on the dropdown next to the GCP logo on the top left: in the pop-up that opens, click on `New Project` on the top right. Give it a project name e.g., `xlwings`, `Google Directory` or similar. Once created (this may take a moment), refresh the page and select your newly created project in the dropdown next to the GCP logo. Note that no billing account is required, and you could also use an existing project instead of creating a new one.
4. In the navigation menu on the left (the "hamburger"), click on `APIs & Services` > `Enabled APIs & services` (if you don't see `APIs & Services`, click on `More Products` first). Click on `+ Enable APIs and Services` at the top and search for `Admin SDK API`. Then click on `Enable`.
5. In the navigation menu, click on `APIs & Services` > `Credentials`. At the top, click on `+ Create Credentials` > `Service account`. Give it a name (this should automatically create a `Service account ID`), then click on `Done` (you can ignore the rest).
6. Now you can see the new service account listed: click on it and select `Keys` in the tabs at the top. Click on the `Add Key` dropdown and select `Create new key`. In the pop-up, select `JSON`, then click on `Create`. This downloads a JSON file to your computer. This file has sensitive information, so keep it secure.
7. On the `Details` tab, make note of the `Unique ID` of the service account as you will need it in the next steps.

### Google Workspace Admin Console
1. Sign in to your Google Admin console at https://admin.google.com.
2. Again: make sure to log in with the proper account.
3. On the menu on the left-hand side, select `Security` > `Overview`. Scroll down on the page, then click on `API controls`. At the bottom of the page you'll find `Domain wide delegation`. Click on the `Manage Domain Wide Delegation` link. Now click on `Add new` and paste the `Client ID` (the `Unique ID` that we noted previously from GCP). Add the following two OAuth Scopes: `https://www.googleapis.com/auth/admin.directory.group.readonly` and `https://www.googleapis.com/auth/admin.directory.group.member.readonly` (once you paste one, there will be another line appearing where you can paste the second one). See https://developers.google.com/admin-sdk/directory/reference/rest for other potential scopes, if you're implementation differs from this project.

### FastAPI

1. Now you can use the `is_member` function from `directory_google.py` by switching the respective import statement at the top of the `auth.py` module. By providing one or multiple Google group emails, the app will require that the user is part of that group. So you'll need to change the following endpoint under `app/api/myspreadsheet.py` and replace `"group_admin"` with the email of the Google group:

    ```python
    @router.post("/hello3")
    async def hello3(
        data: dict = Body,
        current_user: User = Security(authorize, scopes=["mygroup@mydomain.com"])
    ):
        pass
    ```

2. Paste the JSON string from the downloaded file from GCP as your `GOOGLE_SERVICE_ACCOUNT_INFO` env var (make sure to enclose it in single quotes if you run things locally and paste this into the `.env` file).
3. Set the `GOOGLE_DELEGATE_EMAIL` env var to your own email as this account will eventually be used to access the Google directory, see https://developers.google.com/admin-sdk/directory/v1/guides/delegation for further information.
