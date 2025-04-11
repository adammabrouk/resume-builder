FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update 

RUN apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-luatex \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-bibtex-extra \
    texlive-science \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false 
RUN poetry install --only main --no-interaction --no-ansi --no-root

RUN chmod 1777 /tmp
# Copy project files
COPY . /app

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
