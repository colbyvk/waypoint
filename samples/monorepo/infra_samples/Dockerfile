# Intentionally insecure Dockerfile -- Waypoint Trivy/hadolint fixture. Do not deploy.
# Classic Dockerfile smells for Trivy misconfig / hadolint to catch. No custom
# Semgrep rule targets this file.

# trivy plant: 'latest' base image tag — unpinned, non-reproducible (DS001 / AVD-DS-0001)
FROM python:latest

# trivy plant: secret baked into an ENV instruction (DS / secret scanner)
ENV AWS_SECRET_ACCESS_KEY="EXAMPLE-not-a-real-aws-secret"
ENV DB_PASSWORD="s3cr3t-litera1-passw0rd"

WORKDIR /app

# trivy plant: ADD used to fetch a remote URL instead of COPY (DS005 / AVD-DS-0005)
ADD https://example.com/app/bootstrap.sh /app/bootstrap.sh

COPY . /app

RUN pip install -r requirements.txt

# trivy plant: no USER instruction — container runs as root (DS002 / AVD-DS-0002)
EXPOSE 8080
CMD ["python", "app.py"]
