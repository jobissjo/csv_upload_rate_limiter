# CSV USER Upload 

A Django REST API project for CSV file uploads with user authentication and comprehensive testing.

## Features

- JWT-based authentication with custom user model
- CSV file upload endpoints
- Swagger API documentation
- Comprehensive test suite with pytest
- Custom management commands for token generation

## Prerequisites

- Python 3.12.10
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jobissjo/csv_upload_rate_limiter
cd csv_upload_rate_limiter
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment (using Python 3.12.10)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Since the project uses a custom user model (AbstractBaseUser), you need to create migrations first:

```bash
# Create migrations for the custom user model
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## API Documentation

Visit `http://127.0.0.1:8000/api/schema/docs/` for interactive Swagger documentation to test the API endpoints.

### Testing File Upload

1. **Primary method**: Use the Swagger UI at `/api/schema/docs/`
2. **Alternative method**: If Swagger file upload doesn't work, you can:
   - Use the `/api/schema/` endpoint in Swagger to download the OpenAPI schema
   - Refer to the included images added in `docs-media/download_docs1.png` and `docs-media/download_docs2.png`

## Authentication

The API uses JWT authentication. To get access tokens:

### First Time Setup

```bash
# Create a new user and get tokens
python manage.py get_token
```

This will output:
- Email
- Password
- Access Token
- Refresh Token

### Existing User

```bash
# Skip validation if user already exists
python manage.py get_token --skip_validation
```

Use this if you get an "email already exists" warning. It will either update existing user info or return tokens for the existing user.

### Using Tokens in Swagger

1. Copy the `access_token` from the terminal output
2. In Swagger UI, click the "Authorize" button
3. Enter the access token
4. You can now test the protected endpoints

## Testing

The project includes comprehensive tests using pytest with Faker for generating test data.

### Test Configuration

- `pytest.ini` contains all required pytest configurations
- Tests use Faker to generate names and emails for thousands of test entries
- 3 test cases are included with terminal logs

### Running Tests

```bash
pytest
```

## Sample Data

- `docs-media/sample_user_data.csv` - Sample CSV file included in the repository for testing file uploads
- `docs-media/success.json` - Example of successful API response structure
- `docs-media/error.json` - Example of error response structure



## API Endpoints

- `/api/schema/docs/` - Swagger documentation
- `/api/schema/` - OpenAPI schema download
- File upload endpoints (documented in Swagger)

## Key Features

- **Custom User Model**: Uses AbstractBaseUser for enhanced user management
- **JWT Authentication**: Secure token-based authentication
- **File Upload**: CSV file processing with validation
- **Comprehensive Testing**: Full test coverage with realistic data generation

## Development Notes

- The project overrides Django's default User model with AbstractBaseUser
- All routes are protected and require authentication
- Swagger UI provides interactive API testing capabilities

## Support

If you encounter any issues:
1. Ensure you're using Python 3.12.10
2. Check that all dependencies are installed correctly
3. Verify that migrations have been applied
4. Make sure you have valid access tokens for API testing

## Sample Usage

1. Start the server: `python manage.py runserver`
2. Get authentication token: `python manage.py get_token`
3. Visit Swagger docs: `http://127.0.0.1:8000/api/schema/docs/`
4. Authorize with your access token
5. Upload `docs-media/sample_user_data.csv` using the file upload endpoint
6. Check response format against `docs-media/success.json` and `docs-media/error.json` examples