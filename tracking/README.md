# tracking app

installs telemetry to log all page requests with their details per logged in user

## download url
the logs can be extracted by creating a telemetry key in /admin/ and executing the following example command:
```wget --content-disposition --post-data 'key=<key>' https://<siteurl>/<url prefix setup in urls.py of root>/download/```