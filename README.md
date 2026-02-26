# Secure Multi-Language Flask Application

A production-ready web application featuring user authentication with browser/device-based access rules, multilingual support with OTP verification, and comprehensive login history tracking.

## Features

### Authentication System
- **User Registration**: Secure account creation with password hashing (bcrypt)
- **User Login**: Session-based authentication with device detection
- **Password Security**: All passwords are hashed using bcrypt before storage
- **Session Management**: Secure server-side sessions using Flask-Session

### Browser & Device-Based Access Rules
| Browser/Device | Access Rule |
|---------------|-------------|
| Google Chrome | Email OTP verification required before login |
| Microsoft Edge | Direct access allowed (no OTP needed) |
| Mobile Devices | Access restricted to 10:00 AM - 1:00 PM only |
| Other Browsers | Direct access allowed |

### Login History Tracking
On every login, the system automatically detects and stores:
- IP Address
- Browser Name & Version
- Operating System
- Device Type (desktop/mobile)
- Login Timestamp

### Multilingual Support
Supports 6 languages with OTP verification for switching:
- English (en)
- Hindi (hi) - हिन्दी
- Spanish (es) - Español
- Portuguese (pt) - Português
- Chinese (zh) - 中文
- French (fr) - Français

**Language Change Rules:**
- **French**: Requires email OTP verification
- **All other languages**: Requires mobile OTP verification (simulated)

### OTP System
- 6-digit OTP codes
- Session-based storage with 5-minute expiry
- Email OTP via Flask-Mail (Gmail SMTP)
- Mobile OTP simulated (logged to console)

## Project Structure

```
secure_multilang_app/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.example             # Sample environment variables
├── schema.sql               # Database schema
├── README.md                # This documentation
├── models/
│   ├── __init__.py          # Database utilities
│   ├── user.py              # User model
│   ├── login_history.py     # Login history model
│   └── language_log.py      # Language log model
├── routes/
│   ├── __init__.py
│   ├── auth.py              # Authentication routes
│   ├── dashboard.py         # Dashboard routes
│   ├── otp.py               # OTP routes
│   └── language.py          # Language routes
├── services/
│   ├── __init__.py
│   ├── otp_service.py       # OTP generation/validation
│   ├── email_service.py     # Email sending
│   ├── device_service.py    # Device detection
│   └── access_rules.py      # Access rule enforcement
├── translations/
│   ├── en.json              # English
│   ├── hi.json              # Hindi
│   ├── es.json              # Spanish
│   ├── pt.json              # Portuguese
│   ├── zh.json              # Chinese
│   └── fr.json              # French
├── static/
│   ├── css/
│   │   └── styles.css       # Application styles
│   └── js/
│       └── app.js           # React application
└── templates/
    └── index.html           # Main HTML template
```

## Database Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | VARCHAR(100) | User's full name |
| email | VARCHAR(255) | Unique email address |
| password | VARCHAR(255) | Bcrypt hashed password |
| mobile | VARCHAR(20) | Mobile number |
| created_at | TIMESTAMP | Account creation time |

### login_history
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| user_id | INTEGER | Foreign key to users |
| ip_address | VARCHAR(45) | Client IP address |
| browser | VARCHAR(100) | Browser name and version |
| os | VARCHAR(100) | Operating system |
| device_type | VARCHAR(20) | 'desktop' or 'mobile' |
| login_time | TIMESTAMP | Login timestamp |

### language_logs
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| user_id | INTEGER | Foreign key to users |
| language | VARCHAR(10) | Language code |
| verified_by | VARCHAR(10) | 'email' or 'mobile' |
| change_time | TIMESTAMP | Change timestamp |

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 1. Easy One-Click Start (Windows)
Simply double-click the `run_app.bat` file! 

This script will automatically:
- Create a virtual environment if needed
- Install all dependencies
- Start the application

### 2. Manual Setup (Alternative)
If you prefer manual setup:

### Clone or Download the Project
```bash
cd secure_multilang_app
```

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and configure it:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` and set your values:
```env
SECRET_KEY=your-super-secret-key-change-this
DEBUG=True
DATABASE_PATH=app.db

# Gmail SMTP Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Gmail App Password Setup:**
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate a new app password
4. Use the generated password in `MAIL_PASSWORD`

### 5. Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/verify-login-otp` | Verify login OTP |
| POST | `/api/auth/resend-otp` | Resend login OTP |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | Get dashboard summary |
| GET | `/api/dashboard/login-history` | Get login history |
| GET | `/api/dashboard/language-history` | Get language history |
| GET | `/api/dashboard/profile` | Get user profile |

### Language
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/language/translations/{code}` | Get translations |
| GET | `/api/language/available` | Get available languages |
| GET | `/api/language/current` | Get current language |
| POST | `/api/language/change` | Initiate language change |
| POST | `/api/language/verify-change` | Verify language OTP |
| POST | `/api/language/resend-otp` | Resend language OTP |
| POST | `/api/language/cancel-change` | Cancel language change |

### OTP
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/otp/status/{purpose}` | Get OTP status |
| POST | `/api/otp/validate` | Validate OTP |
| POST | `/api/otp/clear/{purpose}` | Clear OTP |

## Testing the Application

### Test Registration
1. Open the application in your browser
2. Click "Register" and fill in the form
3. After registration, login with your credentials

### Test Browser-Based Access Rules
- **Chrome Browser**: Login will require email OTP verification
- **Edge Browser**: Login will be direct without OTP
- **Mobile Device**: Access only between 10:00 AM and 1:00 PM

### Test Language Switching
1. Login to your account
2. Click on the language dropdown in the navbar
3. Select a language:
   - French: Will require email OTP
   - Others: Will require mobile OTP (check console for OTP)

### Test Login History
1. Login to the dashboard
2. View the "Login History" tab to see all recorded logins

## Technologies Used

### Backend
- **Flask**: Web framework
- **Flask-Mail**: Email support
- **Flask-Session**: Server-side sessions
- **Flask-Cors**: Cross-origin resource sharing
- **bcrypt**: Password hashing
- **user-agents**: Browser/device detection
- **SQLite**: Database
- **pytz**: Timezone support

### Frontend
- **React 18**: UI library (via CDN)
- **Babel**: JSX transpilation (via CDN)
- **Custom CSS**: ReactBits-inspired animations
- **Responsive Design**: Mobile-first approach

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **Session Security**: Server-side sessions with secure cookies
3. **OTP Verification**: Time-limited OTP with expiry validation
4. **Input Validation**: Server-side validation for all inputs
5. **CORS Protection**: Configured for same-origin requests
6. **SQL Injection Prevention**: Parameterized queries

## Customization

### Adding New Languages
1. Create a new JSON file in `translations/` (e.g., `de.json`)
2. Add the language code to `SUPPORTED_LANGUAGES` in `config.py`
3. Update the `LANGUAGES` array in `static/js/app.js`

### Modifying Access Rules
Edit `services/access_rules.py` to change:
- Browser-specific rules
- Mobile access time restrictions
- Language change OTP requirements

### Changing OTP Settings
Edit `config.py`:
- `OTP_LENGTH`: Length of OTP (default: 6)
- `OTP_EXPIRY_MINUTES`: OTP validity period (default: 5)

## Troubleshooting

### Email Not Sending
1. Check SMTP credentials in `.env`
2. Ensure Gmail App Password is correct
3. Check console for OTP (simulated if email fails)

### Database Errors
1. Delete `app.db` and restart the application
2. The database will be recreated automatically

### Session Issues
1. Delete the `flask_session` folder
2. Clear browser cookies
3. Restart the application

## License
MIT License

## Author
Created for internship evaluation submission.

---

**Note**: This application is designed for educational and demonstration purposes. For production use, additional security measures and testing should be implemented.
