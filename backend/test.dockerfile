FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install pyright

COPY . .

CMD ["bash", "run_test.sh"]
