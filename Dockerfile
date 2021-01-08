FROM python:3.8-alpine
RUN pip install csv-diff
WORKDIR /files
ENTRYPOINT ["csv-diff"]
CMD ["--help"]