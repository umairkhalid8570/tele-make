#!/bin/bash
community=$(cd -- "$(dirname "$0")" &> /dev/null && cd ../../.. && pwd)

"$community/applets/web/tooling/disable.sh"
"$community/applets/web/tooling/enable.sh"
