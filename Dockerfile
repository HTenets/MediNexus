# Dev convenience: delegates to backend Dockerfile
ARG TARGET=backend
FROM infrastructure/docker/Dockerfile.${TARGET}
