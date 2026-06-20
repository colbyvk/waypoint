# Waypoint sandbox image — scan UNTRUSTED code (including the code-executing
# dynamic lanes) in isolation. Driven by bin/waypoint-sandboxed, which adds
# --network none, a read-only source mount, non-root, dropped capabilities, and
# an ephemeral container. The container itself is the trust boundary.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Waypoint's Python detectors (the fast tier + the Python dynamic lane).
RUN python -m venv .venv \
    && .venv/bin/pip install --no-cache-dir --upgrade pip \
    && .venv/bin/pip install --no-cache-dir \
        semgrep ruff bandit mypy pip-audit pyyaml hypothesis pytest

# Waypoint source (rules + scripts). .dockerignore keeps host state out.
COPY . /app

# Output dirs writable by the unprivileged run user; HOME on tmpfs at run time.
RUN mkdir -p /app/reports/_work /app/beacons \
    && chmod -R 0777 /app/reports /app/beacons
ENV HOME=/tmp
USER 65532

# Inside this locked-down container, the dynamic lanes are allowed to run.
ENV WAYPOINT_TRUSTED=1
ENTRYPOINT ["bin/waypoint"]
