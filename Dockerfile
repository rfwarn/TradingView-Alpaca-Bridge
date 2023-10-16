FROM python:3.11.6-slim

WORKDIR /usr/src/app

# ADD AlpacaTVBridge.py .
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# CMD [ "flask", "./AlpacaTVBridge.py", "--host=0.0.0.0"]
CMD [ "python", "./AlpacaTVBridge.py", "serveTV"]