# Technology Stack

## Backend

- **Framework**: Django 5.2.4
- **Language**: Python 3.x
- **Database**: MySQL (via PyMySQL connector)
  - Host: 172.16.4.181:6666
  - Database: SDashboard
- **ORM**: Django ORM with managed=False models (database-first approach)

## Frontend

- **Templates**: Django template engine
- **Styling**: Custom CSS with modern theme (green/white color scheme)
- **JavaScript**: Vanilla JS for interactivity
- **UI Features**: Waterfall loading animations, glass morphism effects, responsive design

## Key Libraries

- `lebai-sdk`: Robotic arm control
- `opencv-python`: Computer vision processing
- `pandas`, `numpy`: Data analysis
- `nest-asyncio`: Async support for robotic arm operations
- `websockets`, `aiohttp`: Real-time communication
- `flask`: Additional API endpoints (MCP service)

## Hardware Integration

- **Robotic Arm**: Lebai robot (IP: 172.16.4.78)
- **Vision System**: YOLOv11 detection service (optional, http://172.16.4.223:5000)

## Common Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Start on specific host/port
python manage.py runserver 0.0.0.0:8000
```

### Database

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell
```

### Docker (Optional)

```bash
# Build image
docker build -t dashboard-app .

# Run container
docker run -p 8000:8000 dashboard-app
```

## Configuration Notes

- **CSRF**: Some API endpoints use `@csrf_exempt` decorator for external integrations
- **Static Files**: Located in `main/static/`, served via Django's static file handling
- **Session Management**: Django sessions for user authentication
- **Middleware**: Custom authentication middleware in `main/middlewares/AuthLogin.py`
- **Time Zone**: UTC (configured in settings)
- **Debug Mode**: Currently enabled (DEBUG=True) - disable for production

## API Patterns

- RESTful JSON APIs in `main/api.py`
- View-based rendering in `main/views.py`
- URL routing in `DashBoard/urls.py` and `main/urls.py`
- Decorators: `@require_POST`, `@require_http_methods`, `@csrf_exempt`
