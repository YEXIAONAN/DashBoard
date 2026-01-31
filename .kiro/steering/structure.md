# Project Structure

## Root Directory Layout

```
/
├── DashBoard/              # Django project configuration
│   ├── settings.py         # Main settings (database, middleware, apps)
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI application entry point
├── main/                   # Primary Django app
│   ├── models.py           # Database models (Users, Dishes, Orders, etc.)
│   ├── views.py            # View functions for page rendering
│   ├── api.py              # RESTful API endpoints
│   ├── admin.py            # Django admin configuration
│   ├── middlewares/        # Custom middleware (auth, cache control)
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images, fonts
│   ├── migrations/         # Database migration files
│   └── data/               # CSV data files for seeding
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── dish_task_config.py     # Robotic arm task mappings
```

## Key Directories

### `/main/templates/`
HTML templates for all pages:
- `index.html` - Home page with recommendations
- `orders.html` - Dish browsing and ordering
- `profile.html` - User profile and settings
- `repo.html` - Nutrition reports
- `order_history.html` - Past orders
- `ai_health_advisor.html` - AI chat interface
- `login.html` - Authentication

### `/main/static/`
Static assets organized by type:
- `css/` - Stylesheets
- `js/` - JavaScript files
- `Images/` - Dish images and UI assets
- `fonts/` - Custom fonts
- `webfonts/` - Icon fonts

### `/main/data/`
CSV files for data import:
- `dishes.csv` - Dish catalog
- `users.csv` - User accounts
- `orders.csv` - Order records
- `dish_ingredients.csv` - Dish-ingredient relationships
- `raw_materials.csv` - Ingredient nutritional data

### `/mcp/`
Model Context Protocol service:
- `main.py` - MCP server implementation
- `simple_server.py` - Simplified MCP server
- `.env` - Environment configuration

### `/pysh/`
Python utility scripts:
- `test_*.py` - Various test scripts
- `create_table.py` - Database setup
- `keep_alive_script.py` - Service monitoring

### `/sql/`
SQL scripts:
- `SDashboard.sql` - Database schema
- `create_chat_history_table.sql.sql` - Chat history table
- `optimize_queries.sql` - Performance optimizations

### `/docs/`
Documentation:
- `lebai.md` - Robotic arm integration guide
- `README.md` - General documentation

### `/Readme/`
Project documentation organized by date and feature:
- `2026-01-24_现代主题/` - Modern theme updates
- `2026-01-26_最新优化/` - Latest optimizations
- `计划/` - Planning documents

## Code Organization Patterns

### Models (`main/models.py`)
- Database-first approach with `managed = False`
- Models: Users, Dishes, Orders, OrderItems, RawMaterials, DishIngredients, Admin, OrderEvaluation, ChatHistory
- Foreign key relationships between orders, users, and dishes

### Views (`main/views.py`)
- Function-based views for page rendering
- Session-based user authentication
- Aggregation queries for nutrition statistics
- Helper functions: `getUserSession()`, `personalized()`, `get_nutrient_sums_for_week()`

### APIs (`main/api.py`)
- JSON response endpoints
- Order submission and management
- Robotic arm control (`start_pickup_process`, `execute_order_tasks`)
- Chat history management
- Authentication endpoints (`login_v`, `logout`)

### URL Routing
- Root URLs in `DashBoard/urls.py`
- App-specific URLs typically in `main/urls.py` (if exists)
- API endpoints prefixed with `/api/`

### Middleware
- `AuthLogin.py` - Session-based authentication
- `CacheControlMiddleware.py` - Static file caching

## Naming Conventions

- **Python files**: snake_case (e.g., `dish_task_config.py`)
- **Templates**: lowercase with underscores (e.g., `order_history.html`)
- **CSS classes**: kebab-case (e.g., `.nutrition-card`)
- **Database tables**: lowercase with underscores (e.g., `order_items`)
- **Model classes**: PascalCase (e.g., `OrderItems`)
- **Functions**: snake_case (e.g., `submit_order()`)

## Configuration Files

- `dish_task_config.py` - Robotic arm task mappings and YOLO class mappings
- `DashBoard/settings.py` - Django configuration
- `requirements.txt` - Python dependencies
- `.env` files - Environment-specific settings (in mcp/)
