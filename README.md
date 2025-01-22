# Django Real-time Notification System

A Django application that implements real-time notifications using Django Channels and WebSocket. This system allows for instant delivery of notifications to specific users through persistent WebSocket connections.

## Project Structure 

```
realtime_notification/
├── realtime_notification/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
│ ├── routing.py
│ ├── consumers.py
│ ├── models.py
│ ├── views.py
│ └── serializers.py
├── manage.py
├── requirements.txt
└── README.md
```
## Features

- Real-time WebSocket notifications
- User-specific notification channels
- Asynchronous message handling
- Django Channels integration
- Redis as message broker

## Prerequisites

- Python 3.8+
- Redis Server
- Virtual Environment (recommended)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/shreena-apl/realtime_notifications.git
cd realtime_notification
```

2. **Create and activate virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows
venv\Scripts\activate

# For Linux/MacOS
source venv/bin/activate
```

3. **Install dependencies**

Create a `requirements.txt` file with the following content:
```txt
Django>=4.2.0
channels>=4.0.0
daphne>=4.0.0
channels-redis>=4.1.0
djangorestframework>=3.14.0
```

Install the requirements:
```bash
pip install -r requirements.txt
```

4. **Configure Redis**

Make sure Redis server is installed and running on your system:
- For Windows: Download and install from [Redis Windows](https://github.com/microsoftarchive/redis/releases)
- For Linux: `sudo apt-get install redis-server`
- For MacOS: `brew install redis`

5. **Apply migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

## Running the Application

1. **Start Redis Server**
```bash
# Linux/MacOS
redis-server

# Windows
redis-server.exe
```

2. **Run the Application**

Using Daphne (recommended for production):
```bash
daphne -b 0.0.0.0 -p 8000 realtime_notification.asgi:application
```

Using Django development server (for development only):
```bash
python manage.py runserver
```

## WebSocket Usage

### Connecting to WebSocket

```javascript
let socket = new WebSocket("ws://localhost:8000/ws/notifications/");

socket.onopen = function() {
    console.log("WebSocket connection established.");
    // Send the message after the connection is open
    socket.send(JSON.stringify({message: "Hello, Shreena!"}));
};

socket.onmessage = function(event) {
    console.log("Received:", event.data);
};

socket.onerror = function(error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function(event) {
    console.log("WebSocket connection closed:", event);
};
```

## API Endpoints

- WebSocket: `ws://localhost:8000/ws/notifications/`
- Add other API endpoints specific to your application

## Configuration

The application uses the following key configurations in `settings.py`:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## Notes for Windows Users

## Browser Content Security Policy (CSP) Configuration

If your browser blocks the WebSocket connection due to Content Security Policy (CSP) restrictions, you need to configure CSP directives in your Django `settings.py`. Add the following:

```python
CSP_CONNECT_SRC = ["'self'", "ws://localhost:8000"]
```

Make sure to include the `CSPMiddleware` in your middleware settings:

```python
MIDDLEWARE = [
    # Other middleware...
    'csp.middleware.CSPMiddleware',
]
```

You also need to install the `django-csp` package if it is not already installed:

```bash
pip install django-csp
```
