$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "C:\Program Files\DsNET Corp\aTube Catcher\Resource\python-3.13.1-embed-amd64\python.exe"
$sitePackages = Join-Path $env:APPDATA "Python\Python313\site-packages"

$script = @"
import sys
sys.path[:0] = [r'$sitePackages', r'$projectRoot']
from app import create_app

app = create_app()
app.run(debug=True)
"@

& $pythonExe -c $script
