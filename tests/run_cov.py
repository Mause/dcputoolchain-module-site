import coverage

import run_tests

cov = coverage.coverage()
cov.start()

run_tests.main()

cov.stop()
cov.save()

# import pudb
# pudb.set_trace()
cov.html_report(omit=[
    "*.google_appengine*",
    "*dms_venv*",
    "*slpp*",
    "*tests*",
    "*appengine_config*"
])
