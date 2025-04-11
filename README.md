# OverKeef

From inside the folder build the Docker image:

```bash
docker buildx build --progress=plain --platform linux/amd64 -t resume-builder:latest --load .
```
Run the Docker container:

```bash
docker run --platform linux/amd64 -p 8501:8501  resume-builder:latest
```
