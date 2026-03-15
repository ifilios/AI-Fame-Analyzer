# Dockerfile για AI Fame Analyzer
FROM python:3.11-slim

# Ορίζουμε working directory
WORKDIR /app

# Αντιγράφουμε όλα τα αρχεία της εφαρμογής στον container
COPY . .

# Εγκατάσταση dependencies
RUN pip install --no-cache-dir fastapi uvicorn openai python-dotenv requests pytrends pydantic

# Εκθέτουμε το port που τρέχει η εφαρμογή
EXPOSE 9000

# Ορισμός περιβαλλοντικών μεταβλητών από .env αν θέλεις (προαιρετικό)
# ENV OPEN_AI_KEY=...
# ENV SERPER_API_KEY=...
# ...

# Command για να τρέξει η εφαρμογή με uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]