
FROM ghcr.io/xu-cheng/texlive-full:20231101

RUN apk add --no-cache python3 zip inkscape

WORKDIR /app
COPY package.py ./package.py

ENTRYPOINT [ "python", "/app/package.py" ]

