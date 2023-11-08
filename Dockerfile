
FROM ghcr.io/xu-cheng/texlive-full:20231101

RUN apk add --no-cache python3 zip

ENTRYPOINT [ "python", "src/package.py" ]

