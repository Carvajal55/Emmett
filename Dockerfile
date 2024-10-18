FROM ubuntu:20.04

# Evitar interacción durante la instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

ADD ./conf/requirements.txt /code/
RUN apt-get update

# Instalar dependencias del sistema, incluyendo el cliente MySQL
RUN apt-get install -y pkg-config build-essential python3-pip libpq-dev wget unzip libmysqlclient-dev python3-dev \
    python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info tzdata default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Actualizar pip y evitar conflictos con pycparser
RUN pip install --upgrade pip
RUN pip install --ignore-installed -r requirements.txt

# Copiar código fuente
ADD ./src/ /code/

ARG DJANGO_APP
ENV DJANGO_APP=${DJANGO_APP}

# Exponer puerto
EXPOSE 8000

# Ejecutar el servidor Django
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
