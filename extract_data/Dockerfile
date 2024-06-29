FROM python:3.9-slim

# Installing python dependencies
RUN python -m pip install --upgrade pip && python -m pip install bs4 requests selenium 

# Installing chrome inside docker container
RUN apt-get update && apt-get install -y wget unzip curl xvfb && apt-get clean \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    apt-get install -y google-chrome-stable_current_amd64.deb=114.0.5735.90-1

# Install ChromeDriver for the specific Chrome version
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# # Install ChromeDriver
# RUN CHROME_VERSION=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") && \
#     CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
#     wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
#     unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#     chmod +x /usr/local/bin/chromedriver


COPY . /extract_data

WORKDIR /extract_data

# Set the display port to avoid crash
ENV DISPLAY=:99    

# Start Xvfb and then run the script
CMD ["sh", "-c", "Xvfb :99 -screen 0 1280x1024x24 & python run.py"]`