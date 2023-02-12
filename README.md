# Comb
uOttaHack project

To run the server locally, you need to follow these steps:
1. Install a chrome driver that matches your version of chrome from https://chromedriver.chromium.org/downloads.

2. Add a .env file in the backend folder with this key-value pair:

`CHROMEDRIVER_PATH=(path to your chromedriver)/chromedriver.exe`

3. From the terminal, navigate to the backend directory

4. Install venv if you don't have it (for macOS: `python3 install venv`)

5. Create a new venv in the Comb backend directory:

`python3 -m venv [name]`

6. Enter the new venv from your shell:

`source [name]/bin/activate`

7. Install all of the package requirements:

`pip install -r requirements.txt`

8. Launch the API server with this command:

`uvicorn api:app`

If there were no problems during setup, you should see similar output to this in your shell:
```
INFO:     Started server process [11461]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
