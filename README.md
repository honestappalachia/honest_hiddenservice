# For developers

After you've cloned the repo, first create a local virtualenv ('./env' is
already in gitignore).

    $ virtualenv --distribute env
    $ . env/bin/activate

Install the site's dependencies with pip:

    (env) $ pip install -r requirements.txt 

Now, you need to update the settings file for you own use.

    (env) $ cp settings_template.cfg settings.cfg

Edit `settings.cfg`, filling in your own values for any redacted fields.

Now you can run the Flask development server:

    (env) $ ./app.py

Make sure you write unit tests (`tests.py`) for any added functionality. Please
make sure the tests pass before committing code.
