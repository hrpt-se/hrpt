# hrpt

## Settings

The site uses different settings depending on the environment and all setting files are stored in the hrpt folder.
The file `base.py` file contains common settings for all environments and should never be used directly.
The `localsettings.py` file is intended for development, `testsettings.py` is intended for test/staging and  `prodsettings.py` is intended for
production.

### Environment variables & Secrets

Any settings that should be kept out of git (for example the secret key, DB-credentials or API keys) can be stored in a
file named `*secrets.py` in the folder _secrets. There is a `*secrets.py.template` file that can be used as a template
for each environment, containing more info.
