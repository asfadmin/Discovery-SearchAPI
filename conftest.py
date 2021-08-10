import argparse
import yaml
import requests

def api_type(user_input: str) -> str:
    user_input = str(user_input).lower()
    # Grab list of maturities, for available API's:
    with open("maturities.yml", "r") as ymlfile:
        maturities = yaml.safe_load( ymlfile.read() )
    api_info = None # Will be: ("api url: str", "is_flex_maturity: bool")
    for nickname, info in maturities.items():
        # If you gave it the nickname, or the url of a known api:
        if user_input in [ nickname.lower(), maturities[nickname]["this_api"], ]:
            api_info = {
                "this_api": maturities[nickname]["this_api"],
                "flexible_maturity": maturities[nickname]["flexible_maturity"],
            }
            break
    # Make sure you hit an option in maturities.yml
    assert api_info is not None, "Error: api '{0}' not found in maturities.yml file. Can pass in full url, or key of maturity.".format(user_input)

    # Assume it's a url now, and try to connect:
    try:
        requests.get(api_info["this_api"]).raise_for_status()
    except (requests.ConnectionError, requests.exceptions.HTTPError) as e:
        raise argparse.ArgumentTypeError("ERROR: Could not connect to url '{0}'. Message: '{1}'.".format(user_input, str(e)))

    # It connected!! You're good:
    return api_info

def pytest_addoption(parser):
    parser.addoption("--api", action="store", type=api_type, default="local",
        help = "Which API to hit when running tests (LOCAL/DEV/TEST/PROD, or url).")

