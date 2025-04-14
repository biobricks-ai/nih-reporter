{ lib
, pkgs
, fetchPypi
, fetchFromGitHub
 }:

self: super: {
  webdriver-manager = super.buildPythonPackage rec {
    pname = "webdriver-manager";
    version = "4.0.2";
    pyproject = true;

    disabled = super.pythonOlder "3.7";

    src = fetchFromGitHub {
      owner = "SergeyPirogov";
      repo = "webdriver_manager";
      rev = "v${version}";
      hash = "sha256-ZmrQa/2vPwYgSvY3ZUvilg4RizVXpu5hvJJBQVXkK8E=";
    };

    __darwinAllowLocalNetworking = true;

    build-system = with super; [ setuptools ];

    dependencies = with super; [
      packaging
      python-dotenv
      requests
    ];

    nativeCheckInputs = with super; [
      pybrowsers
      pytestCheckHook
      selenium
    ];

    disabledTestPaths = [
      # Tests require network access and browsers available
      "tests_negative/"
      "tests_xdist/"
      "tests/test_brave_driver.py"
      "tests/test_chrome_driver.py"
      "tests/test_chrome_driver.py"
      "tests/test_chromium_driver.py"
      "tests/test_custom_http_client.py"
      "tests/test_downloader.py"
      "tests/test_edge_driver.py"
      "tests/test_firefox_manager.py"
      "tests/test_ie_driver.py"
      "tests/test_opera_manager.py"
      "tests/test_opera_manager.py"
      "tests/test_silent_global_logs.py"
    ];

  };
}
