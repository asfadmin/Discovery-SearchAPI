import pytest

def pytest_addoption(parser):
	parser.addoption("--api", action="store", default=None,
		help = "Override which api ALL .yml tests use with this. (DEV/PROD or SOME-URL)")
	parser.addoption("--only-run", action="store", default=None,
		help = "Only run tests whos name begin with this parameter")



@pytest.fixture
def api(request):
	return request.config.getoption('--api')

@pytest.fixture
def only_run(request):
	return request.config.getoption('--only-run')

