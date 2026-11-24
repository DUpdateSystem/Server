#!/usr/bin/env bash
set -euo pipefail

image=${1:?Usage: smoke-hello.sh IMAGE}
engine=${CONTAINER_ENGINE:-docker}
container=$("$engine" run -d --network none -e discovery_url=tcp://127.0.0.1:5256 "$image" hello)
trap '"$engine" rm -f "$container" >/dev/null' EXIT

for _ in {1..15}; do
    if "$engine" exec "$container" python -c '
from urllib.request import urlopen

with urlopen("http://127.0.0.1:5255/about", timeout=2) as response:
    assert response.status == 200 and b"DUpdateSystem" in response.read()
with urlopen("http://127.0.0.1:5255/server/status_check", timeout=2) as response:
    assert response.status == 204
' >/dev/null 2>&1; then
        echo 'HTTP smoke: /about 200, /server/status_check 204'
        exit 0
    fi
    if [[ $("$engine" inspect -f '{{.State.Running}}' "$container") != true ]]; then
        break
    fi
    sleep 1
done

"$engine" logs "$container" >&2
exit 1
