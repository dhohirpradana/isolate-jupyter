# Gunakan base image Python
FROM python:3.8

# Instal kubectl
RUN apt-get update && apt-get install -y kubectl

# Copy file-file yang diperlukan ke dalam container
COPY . /app
WORKDIR /app

# Instal dependensi Python jika ada
RUN pip install -r requirements.txt

# Port yang digunakan oleh Gunicorn
EXPOSE 8000

# Command untuk menjalankan aplikasi
CMD ["gunicorn", "-b", "0.0.0.0:7788", "app:app"]
