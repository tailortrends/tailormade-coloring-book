FROM python:3.12-slim

# PDF generation uses ReportLab (pure Python, base-14 fonts built in) and Pillow
# (manylinux wheels bundle their own libs), so no system packages are required.

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
