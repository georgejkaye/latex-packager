
FROM ghcr.io/xu-cheng/texlive-full:20231101

RUN apk add --no-cache python3 zip inkscape openjdk8

RUN wget https://gitlab.com/pdftk-java/pdftk/-/jobs/924565145/artifacts/raw/build/libs/pdftk-all.jar
RUN mv pdftk-all.jar /usr/local/bin/pdftk.jar

COPY pdftk /usr/local/bin/

RUN chmod 755 /usr/local/bin/pdftk*

WORKDIR /app
COPY package.py ./package.py
COPY bookmarks.py ./bookmarks.py

ENTRYPOINT [ "python", "/app/package.py" ]

