# Finance Tracker - Backend Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Applications](#core-applications)
6. [Database Models & Relationships](#database-models--relationships)
7. [API Endpoints Access Flow](#api-endpoints-access-flow)
8. [External Libraries & Dependencies](#external-libraries--dependencies)
9. [Configuration Files](#configuration-files)
10. [Process/Working Flow](#processworking-flow)
11. [Entity-Relationship Diagram](#entity-relationship-diagram)

---

## Project Overview

**Finance Tracker** is a comprehensive Django-based REST API backend for personal and group expense tracking with advanced features like:
- Personal expense management and categorization
- Group expense splitting and settlement
- Budget tracking and alerts
- Voice-based transaction entry with NLP processing
- Payment processing with Razorpay integration
- Recurring payment management
- Financial insights and savings goals
- Admin dashboard for system management
- JWT-based authentication

**Framework**: Django 5.1.6 with Django REST Framework
**Database**: SQLite (Development)
**Task Queue**: Celery with Redis broker
**Authentication**: JWT (JSON Web Tokens) with SimplJWT

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)                    │
│              (expense-frontend folder)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                         │
│              (Django URL Router)                            │
│           /api/token/ /api/group-expenses/ etc.             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐   ┌──────────┐   ┌──────────────┐
   │ Users  │   │ Expense  │   │ Group        │
   │ App    │   │ Apps     │   │ Expenses     │
   └────────┘   └──────────┘   └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐   ┌──────────┐   ┌──────────────┐
   │ Django │   │ Celery   │   │ Redis        │
   │ ORM    │   │ Tasks    │   │ Broker       │
   └────────┘   └──────────┘   └──────────────┘
        │
        ▼
   ┌────────────┐
   │ SQLite DB  │
   └────────────┘
```

---

## Technology Stack

### Core Framework
- **Django 5.1.6**: Web framework
- **Django REST Framework 3.15.2**: API toolkit
- **djangorestframework-simplejwt 5.4.0**: JWT authentication

### Database & ORM
- **SQLite3**: Development database
- **Django ORM**: Database abstraction layer

### Task Queue & Caching
- **Celery 5.4.0**: Asynchronous task processing
- **Redis**: Message broker and cache (localhost:6379)
- **django-celery-beat 2.7.0**: Celery periodic tasks

### API Security & Middleware
- **django-cors-headers 4.7.0**: CORS support
- **djangorestframework-simplejwt 5.4.0**: JWT token management
- **rest-framework-simplejwt token blacklist**: Token revocation

### Payment Integration
- **Razorpay API**: Payment processing (Key ID: rzp_test_RcJak5fcO3zfR9)

### NLP & ML
- **stanza**: NLP pipeline for voice processing
- **scikit-learn**: Machine learning for transaction categorization
- **joblib**: Model serialization

### Utilities
- **django-filter 24.3**: Advanced filtering
- **django-extensions 3.2.3**: Admin utilities
- **django-timezone-field 7.1**: Timezone handling
- **emoji 2.14.1**: Emoji support

---

## Project Structure

```
CV Project/
├── manage.py                          # Django management script
├── db.sqlite3                         # SQLite database
├── celery_app.py                      # Celery configuration
├── requirements.txt                   # Python dependencies
├── categorizer_train.py               # ML model training script
├── transactions_dataset.csv           # Training data
├── transaction_classifier.pkl         # Trained classifier model
├── transaction_vectorizer.pkl         # Vectorizer model
│
├── backend/                           # Django project settings
│   ├── settings.py                    # Django configuration
│   ├── urls.py                        # URL routing
│   ├── wsgi.py                        # WSGI application
│   ├── asgi.py                        # ASGI application
│   └── __init__.py
│
├── users/                             # User authentication & profiles
│   ├── models.py                      # User, Profile, FinancialData
│   ├── views.py                       # User endpoints
│   ├── serializers.py                 # User serializers
│   ├── urls.py                        # User routes
│   ├── permissions.py                 # IsPremiumUser permission
│   ├── admin.py                       # Admin interface
│   └── migrations/                    # Database migrations
│
├── transactions/                      # Transaction management
│   ├── models.py                      # Transaction, Category, Budget, BudgetHistory, alerts
│   ├── views.py                       # Transaction endpoints (276 lines)
│   ├── serializers.py                 # TransactionSerializer, BudgetSerializer
│   ├── urls.py                        # Transaction routes
│   ├── categorizer.py                 # ML-based categorization
│   ├── nlp_processing.py              # Voice transaction processing (Stanza NLP)
│   ├── signals.py                     # Django signals
│   ├── utils.py                       # Utility functions
│   ├── admin.py                       # Admin interface
│   └── migrations/                    # Database migrations
│
├── group_expenses/                    # Group expense splitting
│   ├── models.py                      # Group, GroupMember, GroupExpense, Settlement
│   ├── views.py                       # Group endpoints
│   ├── serializers.py                 # Group serializers
│   ├── urls.py                        # Group routes
│   ├── permissions.py                 # IsGroupMember permission
│   ├── tasks.py                       # Celery tasks
│   ├── admin.py                       # Admin interface
│   └── migrations/                    # Database migrations
│
├── payments/                          # Payment processing
│   ├── models.py                      # Payment, Subscription, RecurringPayment
│   ├── views.py                       # Payment endpoints
│   ├── serializers.py                 # Payment serializers
│   ├── urls.py                        # Payment routes
│   ├── permissions.py                 # Payment permissions
│   ├── tasks.py                       # Celery payment tasks
│   ├── utils.py                       # Payment utilities (Razorpay)
│   ├── admin.py                       # Admin interface
│   └── migrations/                    # Database migrations
│
├── insights/                          # Financial analytics & recommendations
│   ├── models.py                      # BudgetInsight, SavingsGoal
│   ├── views.py                       # Insights endpoints
│   ├── serializers.py                 # Insights serializers
│   ├── urls.py                        # Insights routes
│   ├── utils.py                       # Analytics utilities
│   ├── admin.py                       # Admin interface
│   └── migrations/                    # Database migrations
│
├── notifications/                     # Notification system
│   ├── models.py                      # Notification
│   ├── views.py                       # Notification endpoints
│   ├── serializers.py                 # Notification serializers
│   ├── urls.py                        # Notification routes
│   ├── admin.py                       # Admin interface
│   └── migrations/
│       ├── 0001_initial.py
│       └── ...
│
├── analytics/                         # Activity logging & analytics
│   ├── models.py                      # ActivityLog
│   ├── views.py                       # Analytics endpoints
│   ├── serializers.py                 # Analytics serializers
│   ├── urls.py                        # Analytics routes
│   ├── admin.py                       # Admin interface
│   └── migrations/
│
├── admin_dashboard/                   # Admin panel
│   ├── models.py                      # AdminSettings
│   ├── views.py                       # Dashboard views (508 lines)
│   ├── forms.py                       # Dashboard forms
│   ├── urls.py                        # Dashboard routes
│   ├── admin.py                       # Admin interface
│   ├── templates/
│   │   └── admin_dashboard/           # HTML templates
│   └── migrations/
│
├── frontend/                          # Legacy frontend (Django templates)
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   ├── static/
│   │   └── frontend/
│   └── templates/
│       └── frontend/
│
├── expense-frontend/                  # React Vite Frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── Login.jsx
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   └── assets/
│   └── public/
│
└── Screenshots/                       # Project documentation screenshots
```

---

## Core Applications

### 1. **Users App** (`users/`)
**Purpose**: User authentication, profile management, and financial data tracking

**Key Files**:
- `models.py`: 
  - `User`: Custom user model with UUID, email authentication, roles (admin/user)
  - `Profile`: User profile with avatar, currency, occupation, annual income, financial goals
  - `FinancialData`: Tracks monthly income (salary, business, freelance), expenses (rent, bills, loans), savings (cash, stocks, crypto, real estate), and total debt

- `serializers.py`: User and profile serialization for API
- `views.py`: User registration, login, profile update endpoints
- `permissions.py`: 
  - `IsPremiumUser`: Restricts endpoints to premium users only

**Access Points**:
- User registration: `POST /api/users/register/`
- User login: `POST /api/token/`
- Profile update: `PUT /api/users/profile/`
- Token refresh: `POST /api/token/refresh/`

---

### 2. **Transactions App** (`transactions/`)
**Purpose**: Personal expense tracking, budget management, and AI-powered categorization

**Key Files**:
- `models.py`:
  - `Transaction`: Tracks individual transactions (amount, category, type, date, currency)
  - `Category`: User-specific expense categories
  - `Budget`: Monthly budget limits per category
  - `BudgetHistory`: Historical budget tracking for trend analysis
  - `alerts`: Transaction alerts for users

- `views.py` (276 lines):
  - Voice transaction processing
  - Expense CRUD operations
  - Budget management endpoints
  - Analytics and reports generation
  - CSV export functionality

- `serializers.py`:
  - `TransactionSerializer`: Includes category name resolution
  - `BudgetSerializer`: Budget management
  - `BudgetHistorySerializer`: Historical data

- `categorizer.py`: ML-based transaction categorization
  - Uses pre-trained `transaction_classifier.pkl`
  - Vectorizer: `transaction_vectorizer.pkl`
  - Supports dynamic model updates with user corrections

- `nlp_processing.py`: Stanza NLP pipeline
  - Extracts transaction details from voice input
  - Identifies amount, category, and transaction type
  - Supports multiple currencies (₹, $, €)

- `signals.py`: Django signals for automatic processing
- `utils.py`: Helper functions for calculations

**Access Points**:
- Create transaction: `POST /api/transactions/`
- Get transactions: `GET /api/transactions/`
- Voice entry: `POST /api/transactions/voice/`
- Budget management: `POST/GET /api/budgets/`
- Export CSV: `GET /api/transactions/export/`

---

### 3. **Group Expenses App** (`group_expenses/`)
**Purpose**: Group expense splitting, member management, and settlement tracking

**Key Files**:
- `models.py`:
  - `Group`: Group entity with description and creation date
  - `GroupMember`: Members of a group with join date
  - `GroupExpense`: Expense split across multiple members
  - `Settlement`: Tracks who owes whom and settlement status

- `views.py` (101 lines):
  - Group dashboard rendering
  - Expense creation with splitting logic
  - Member management
  - Settlement calculation and tracking

- `serializers.py`: Group, expense, and settlement serialization
- `permissions.py`:
  - `IsGroupMember`: Verifies user is group member
- `tasks.py`: Celery tasks for settlement calculations
- `urls.py`: Group API routes

**Access Points**:
- Create group: `POST /api/group-expenses/groups/`
- Add group member: `POST /api/group-expenses/members/`
- Add group expense: `POST /api/group-expenses/expenses/`
- Get settlements: `GET /api/group-expenses/settlements/`

---

### 4. **Payments App** (`payments/`)
**Purpose**: Payment processing, subscriptions, and recurring payments

**Key Files**:
- `models.py`:
  - `Payment`: Payment transactions with Razorpay integration
  - `Subscription`: Premium subscriptions
  - `RecurringPayment`: Recurring payment tracking (daily, weekly, monthly, yearly)

- `views.py`: 
  - Payment creation and verification
  - Subscription management
  - Webhook handlers for Razorpay

- `serializers.py`: Payment and subscription serialization
- `permissions.py`: Payment-related permissions
- `tasks.py`: Celery tasks
  - `send_payment_reminders`: Daily at 9 AM
  - Recurring payment handling
- `utils.py`: Razorpay integration utilities

**Configuration**:
```
RAZORPAY_KEY_ID = "rzp_test_RcJak5fcO3zfR9"
RAZORPAY_KEY_SECRET = "ul8MqhYAbfpeikySEmq7vr6B"
```

**Access Points**:
- Create payment: `POST /api/payments/create/`
- Verify payment: `POST /api/payments/verify/`
- Get subscriptions: `GET /api/payments/subscriptions/`
- Manage recurring: `POST/GET /api/payments/recurring/`

---

### 5. **Insights App** (`insights/`)
**Purpose**: Financial analytics, spending forecasts, and savings recommendations

**Key Files**:
- `models.py`:
  - `BudgetInsight`: Average spending, forecasts, and recommendations
  - `SavingsGoal`: Target savings with progress tracking

- `views.py`: Analytics endpoints
- `serializers.py`: Insight serialization
- `utils.py`: Complex analytics calculations
  - Spending trend analysis
  - Forecasting algorithms
  - Recommendation engine

**Features**:
- Spending pattern analysis
- Savings recommendations
- Goal progress tracking
- Savings target calculations

**Access Points**:
- Get insights: `GET /api/insights/`
- Create goal: `POST /api/insights/goals/`
- Get goal progress: `GET /api/insights/goals/<id>/`

---

### 6. **Notifications App** (`notifications/`)
**Purpose**: System-wide notifications for users

**Key Files**:
- `models.py`:
  - `Notification`: Broadcast messages to user groups (all, premium, free)

- `views.py`: Notification endpoints
- `serializers.py`: Notification serialization

**Features**:
- User segmentation (all/premium/free)
- Notification tracking (status field)
- Timestamps

**Access Points**:
- Get notifications: `GET /api/notifications/`
- Mark as read: `PUT /api/notifications/<id>/`

---

### 7. **Analytics App** (`analytics/`)
**Purpose**: Activity tracking and audit logs

**Key Files**:
- `models.py`:
  - `ActivityLog`: User action audit trail with timestamp

- `views.py`: Activity endpoints
- `serializers.py`: ActivityLog serialization

**Features**:
- User action logging
- Timestamped records
- Admin monitoring

---

### 8. **Admin Dashboard App** (`admin_dashboard/`)
**Purpose**: Administrative system management and monitoring

**Key Files**:
- `models.py`:
  - `AdminSettings`: System configuration

- `views.py` (508 lines):
  - Dashboard statistics (users, transactions, payments)
  - User management (list, filter, delete)
  - Transaction monitoring
  - Payment tracking
  - Advanced filtering (date range, user type, payment status)
  - CSV export functionality
  - Analytics visualization

- `forms.py`: Admin forms
- `admin.py`: Django admin interface

**Dashboard Features**:
- Real-time statistics
- User analytics
- Revenue tracking
- Transaction monitoring
- Payment status tracking

---

## Database Models & Relationships

### User-Related Models
```
User (Custom User Model)
├── id: UUID (Primary Key)
├── email: Email (Unique)
├── username: CharField
├── phone_no: CharField
├── is_premium: Boolean
├── role: Choice (admin/user)
└── password: Hashed

Profile (One-to-One with User)
├── user: OneToOneField → User
├── avatar: ImageField
├── preferred_currency: Choice
├── date_of_birth: DateField
├── occupation: Choice
├── annual_income: Choice
└── financial_goal: Choice

FinancialData (One-to-One with User)
├── user: OneToOneField → User
├── monthly_income_salary: DecimalField
├── monthly_income_business: DecimalField
├── monthly_income_freelance: DecimalField
├── monthly_income_other: DecimalField
├── rent: DecimalField
├── bills: DecimalField
├── loans: DecimalField
├── subscriptions: DecimalField
├── savings_cash: DecimalField
├── savings_stocks: DecimalField
├── savings_crypto: DecimalField
├── savings_real_estate: DecimalField
└── total_debt: DecimalField
```

### Transaction-Related Models
```
Transaction
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── amount: DecimalField
├── category: ForeignKey → Category (nullable)
├── category_type: Choice (income/expense)
├── description: TextField
├── date: DateField
├── currency: Choice (USD/EUR/INR)
├── created_at: DateTimeField
└── updated_at: DateTimeField

Category
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── name: CharField (unique per user)
└── created_at: DateTimeField (implicit)

Budget
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── category: CharField
├── monthly_limit: DecimalField
└── created_at: DateTimeField

BudgetHistory
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── category: CharField
├── month: IntegerField (1-12)
├── year: IntegerField
├── previous_limit: DecimalField
├── actual_spent: DecimalField
├── suggested_limit: DecimalField
└── Unique Together: (user, category, month, year)

alerts
├── id: Auto (Primary Key)
├── user: ForeignKey → User (related_name: transaction_alerts)
├── message: TextField
├── created_at: DateTimeField
└── is_read: Boolean
```

### Group Expense Models
```
Group
├── id: Auto (Primary Key)
├── name: CharField
├── description: TextField
└── created_at: DateTimeField

GroupMember
├── id: Auto (Primary Key)
├── group: ForeignKey → Group
├── user: ForeignKey → User
└── joined_at: DateTimeField

GroupExpense
├── id: Auto (Primary Key)
├── description: CharField
├── amount: DecimalField
├── category: CharField
├── date: DateField
├── paid_by: ForeignKey → GroupMember
├── split_members: ManyToManyField → GroupMember
└── split_amount: DecimalField

Settlement
├── id: Auto (Primary Key)
├── member: ForeignKey → GroupMember
├── amount: DecimalField
└── settled: Boolean
```

### Payment Models
```
Payment
├── payment_id: UUID (Primary Key)
├── user: ForeignKey → User
├── razorpay_order_id: CharField
├── razorpay_payment_id: CharField (nullable)
├── razorpay_signature: CharField (nullable)
├── amount: DecimalField
├── status: CharField (default: pending)
└── created_at: DateTimeField

Subscription
├── subscription_id: UUID (Primary Key)
├── user: ForeignKey → User
├── razorpay_subscription_id: CharField
├── plan: CharField
├── status: CharField (default: active)
├── start_date: DateTimeField
├── end_date: DateTimeField
└── created_at: DateTimeField

RecurringPayment
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── name: CharField
├── amount: DecimalField
├── category: Choice
├── frequency: Choice (daily/weekly/monthly/yearly)
├── next_payment_date: DateField
└── status: Choice (active/paused/canceled)
```

### Insights Models
```
BudgetInsight
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── category: CharField
├── average_spending: DecimalField
├── forecasted_spending: DecimalField
├── savings_recommendation: TextField
└── created_at: DateTimeField

SavingsGoal
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── goal_name: CharField
├── target_amount: DecimalField
├── saved_amount: DecimalField
├── deadline: DateField
├── status: Choice (In Progress/Completed)
└── created_at: DateTimeField
```

### Notification & Analytics Models
```
Notification
├── id: Auto (Primary Key)
├── recipients: Choice (all/premium/free)
├── title: CharField
├── message: TextField
├── status: CharField
└── timestamp: DateTimeField

ActivityLog
├── id: Auto (Primary Key)
├── user: ForeignKey → User
├── action: CharField
└── timestamp: DateTimeField
```

---

## API Endpoints Access Flow

### Authentication Flow
```
1. User Registration
   POST /api/users/register/
   Body: {email, username, password, ...}
   Response: User created

2. User Login (JWT Token Obtain)
   POST /api/token/
   Body: {email, password}
   Response: {access, refresh}

3. Token Refresh
   POST /api/token/refresh/
   Body: {refresh}
   Response: {access}

4. All Subsequent Requests
   Header: Authorization: Bearer {access_token}
```

### Transaction Flow
```
1. Add Transaction
   POST /api/transactions/
   Body: {amount, category, category_type, description, date, currency}
   Response: {transaction_id, ...}

2. Voice Entry
   POST /api/transactions/voice/
   Body: {voice_text}
   - NLP Processing (nlp_processing.py)
   - ML Categorization (categorizer.py)
   Response: {amount, category, transaction_type}

3. Confirm Voice Transaction
   POST /api/transactions/confirm/
   Body: {amount, category, transaction_type}
   Response: {transaction_id}

4. Get Transactions
   GET /api/transactions/?category=X&date_range=Y
   Response: [transaction1, transaction2, ...]

5. Export Transactions
   GET /api/transactions/export/
   Response: CSV file
```

### Budget Management Flow
```
1. Set Budget
   POST /api/budgets/
   Body: {category, monthly_limit}
   Response: {budget_id}

2. Get Budget Progress
   GET /api/budgets/{id}/
   Response: {category, monthly_limit, current_spent, percentage}

3. Get Budget History
   GET /api/budgets/history/
   Response: [budget_history_records]
```

### Group Expenses Flow
```
1. Create Group
   POST /api/group-expenses/groups/
   Body: {name, description}
   Response: {group_id}

2. Add Member
   POST /api/group-expenses/members/
   Body: {group_id, user_id}
   Response: {member_id}

3. Add Group Expense
   POST /api/group-expenses/expenses/
   Body: {group_id, description, amount, paid_by, split_members}
   - Backend calculates settlements
   - Celery tasks process splits
   Response: {expense_id}

4. Get Settlements
   GET /api/group-expenses/settlements/
   Response: {who_owes_who, amounts}
```

### Payment Flow
```
1. Create Payment Order
   POST /api/payments/create/
   Body: {amount, description}
   Response: {razorpay_order_id, amount}

2. Verify Payment (Webhook)
   POST /api/payments/verify/
   Body: {razorpay_order_id, razorpay_payment_id, razorpay_signature}
   Response: {status: success/failed}

3. Subscribe to Plan
   POST /api/payments/subscriptions/
   Body: {plan, razorpay_subscription_id}
   Response: {subscription_id}
```

### Insights Flow
```
1. Get Financial Insights
   GET /api/insights/
   - Analyzes spending patterns
   - Generates recommendations
   Response: {average_spending, forecast, recommendations}

2. Create Savings Goal
   POST /api/insights/goals/
   Body: {goal_name, target_amount, deadline}
   Response: {goal_id}

3. Track Goal Progress
   GET /api/insights/goals/{id}/
   Response: {saved_amount, percentage, status}
```

---

## External Libraries & Dependencies

### Core Django Stack
| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.1.6 | Web framework |
| djangorestframework | 3.15.2 | REST API toolkit |
| djangorestframework-simplejwt | 5.4.0 | JWT authentication |
| rest-framework-simplejwt[token_blacklist] | 5.4.0 | Token blacklist support |

### Database & ORM
| Package | Version | Purpose |
|---------|---------|---------|
| asgiref | 3.8.1 | ASGI specification |
| sqlparse | - | SQL parsing |

### Task Queue & Caching
| Package | Version | Purpose |
|---------|---------|---------|
| celery | 5.4.0 | Async task processor |
| django-celery-beat | 2.7.0 | Periodic task scheduling |
| redis | - | Message broker |
| kombu | 5.4.2 | Messaging library |
| billiard | 4.2.1 | Process pool |
| click | 8.1.8 | CLI interface |
| cron-descriptor | 1.4.5 | Cron schedule parser |

### Security & Middleware
| Package | Version | Purpose |
|---------|---------|---------|
| django-cors-headers | 4.7.0 | CORS support |
| django-timezone-field | 7.1 | Timezone handling |

### NLP & Machine Learning
| Package | Version | Purpose |
|---------|---------|---------|
| stanza | Latest | NLP processing (voice) |
| scikit-learn | Latest | ML algorithms |
| numpy | Latest | Numerical computing |
| joblib | 1.4.2 | Model serialization |
| Cython | 3.0.12 | C extensions |

### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| django-extensions | 3.2.3 | Admin utilities |
| django-filter | 24.3 | Advanced filtering |
| emoji | 2.14.1 | Emoji support |
| chardet | 5.2.0 | Encoding detection |
| requests | Latest | HTTP requests |
| Pillow | Latest | Image processing |
| MarkupSafe | 3.0.2 | Template safety |
| Jinja2 | 3.1.5 | Template engine |

---

## Configuration Files

### 1. **backend/settings.py**
Key configurations:
```python
# Security
DEBUG = True  # Change to False in production
SECRET_KEY = 'django-insecure-...'
ALLOWED_HOSTS = []

# Database
# SQLite in development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Authentication
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_celery_beat',
    'users',
    'transactions',
    'group_expenses',
    'payments',
    'insights',
    'notifications',
    'analytics',
    'admin_dashboard',
]

# Email (Console Backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'financetracker@gmail.com'

# Razorpay Keys
RAZORPAY_KEY_ID = "rzp_test_RcJak5fcO3zfR9"
RAZORPAY_KEY_SECRET = "ul8MqhYAbfpeikySEmq7vr6B"

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### 2. **backend/urls.py**
```python
urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/group-expenses/', include('group_expenses.urls')),
    path('admin/', admin.site.urls),
]
```

### 3. **celery_app.py**
```python
# Celery Broker: Redis at localhost:6379/0
# Auto-discovers tasks from all Django apps
# Beat Schedule: Periodic task execution

app.conf.beat_schedule = {
    'send-payment-reminders': {
        'task': 'payments.tasks.send_payment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

---

## Process/Working Flow

### 1. User Registration & Authentication
```
Step 1: User submits registration
  Frontend: POST /api/users/register/
  {email, username, password, phone_no}

Step 2: Backend creates user
  - Hashes password
  - Validates email uniqueness
  - Creates User record
  - Creates default Profile and FinancialData

Step 3: User logs in
  - POST /api/token/
  - Returns JWT access and refresh tokens

Step 4: Subsequent requests
  - Header: Authorization: Bearer {access_token}
  - Verified by rest_framework_simplejwt.authentication.JWTAuthentication
```

### 2. Transaction Processing Flow
```
Flow A: Manual Entry
Step 1: User creates transaction
  POST /api/transactions/
  {amount, category, category_type, description, date, currency}

Step 2: Backend validation
  - Verify user is authenticated
  - Validate amount format
  - Check currency support

Step 3: Save transaction
  - Create Transaction model instance
  - Update BudgetHistory if applicable
  - Trigger signals (if defined)

Step 4: Generate alerts
  - Check budget vs actual spending
  - Create alert if exceeded
  - Notify user via notifications app

Flow B: Voice Entry
Step 1: User sends voice
  POST /api/transactions/voice/
  {voice_text: "spent 500 rupees on groceries"}

Step 2: NLP Processing (nlp_processing.py)
  - Load Stanza NLP pipeline
  - Extract entities (MONEY, etc.)
  - Identify keywords (food → Groceries)
  - Parse amount value

Step 3: ML Categorization (categorizer.py)
  - Load pre-trained classifier
  - Vectorize description
  - Predict category
  - Return to frontend for confirmation

Step 4: User confirms
  POST /api/transactions/confirm/
  {amount, category, transaction_type}

Step 5: Save transaction
  - Create Transaction record
  - Update ML model with user feedback
  - Trigger signals and alerts
```

### 3. Budget Management Flow
```
Step 1: User sets budget
  POST /api/budgets/
  {category: "Groceries", monthly_limit: 5000}

Step 2: Backend creates budget
  - Create Budget record
  - Store monthly_limit

Step 3: Transaction impact
  - When transaction added to category
  - Calculate current month's spending
  - Update BudgetHistory

Step 4: Alert generation
  - If spending > 80%: Warning alert
  - If spending > 100%: Exceeded alert
  - Create alerts model record

Step 5: Frontend displays
  - Fetch BudgetHistory
  - Calculate percentage used
  - Show progress bars and alerts
```

### 4. Group Expense Flow
```
Step 1: Create group
  POST /api/group-expenses/groups/
  {name: "Trip to Bangkok", description: "..."}
  Response: {group_id: 1}

Step 2: Add members
  POST /api/group-expenses/members/
  {group_id: 1, user_id: "uuid"}
  - Creates GroupMember records

Step 3: Add expense
  POST /api/group-expenses/expenses/
  {
    group_id: 1,
    description: "Hotel booking",
    amount: 3000,
    paid_by: member_id,
    split_members: [member_id1, member_id2, member_id3],
    split_amount: 1000
  }

Step 4: Backend calculates settlement
  - Calculate who owes what
  - Trigger Celery task (tasks.py)
  - Create Settlement records

Step 5: Optimize settlements
  - Minimize payment transactions
  - Group similar debts
  - Return settlement details

Step 6: Frontend displays
  - Show group expenses list
  - Display balance sheet
  - Settlement instructions
```

### 5. Payment Processing Flow
```
Step 1: Initiate payment
  POST /api/payments/create/
  {amount: 999, description: "Premium subscription"}

Step 2: Create Razorpay order
  - Call Razorpay API (utils.py)
  - Create Payment record (status: pending)
  - Return razorpay_order_id

Step 3: Frontend payment widget
  - Display Razorpay payment form
  - User completes payment

Step 4: Webhook callback
  POST /api/payments/verify/
  {razorpay_order_id, razorpay_payment_id, razorpay_signature}

Step 5: Backend verification
  - Verify signature with RAZORPAY_KEY_SECRET
  - Update Payment status: success/failed
  - Update user.is_premium = True
  - Create Subscription record if applicable

Step 6: Celery task (send_payment_reminders)
  - Daily at 9 AM (crontab)
  - Check recurring payments
  - Send reminders
  - Create alerts
```

### 6. Celery Async Task Flow
```
Configuration:
- Broker: Redis (localhost:6379/0)
- Serializer: JSON
- Accepted: ['json']

Registered Tasks:
- payments.tasks.send_payment_reminders (daily 9 AM)
- group_expenses.tasks.calculate_settlements
- transactions.tasks.generate_alerts
- More in respective app tasks.py

Execution:
celery -A backend worker --loglevel=info --pool=solo
celery -A backend beat (for periodic tasks)
```

### 7. Admin Dashboard Flow
```
Step 1: Admin login
  Django admin interface
  /admin/

Step 2: View statistics
  - Total users
  - Total transactions
  - Total payments
  - Revenue metrics

Step 3: Filter and search
  - Date range filter
  - User type filter (premium/free)
  - Transaction type filter
  - Payment status filter

Step 4: Manage users
  - View user list
  - Edit user details
  - Toggle premium status
  - Delete user account

Step 5: Generate reports
  - Export as CSV
  - View charts and graphs
  - Analyze trends
```

---

## Entity-Relationship Diagram

```
                          ┌─────────────────────┐
                          │       User          │
                          │  (Custom User)      │
                          ├─────────────────────┤
                          │ * id (UUID)         │
                          │ * email (Unique)    │
                          │ * username          │
                          │ * phone_no          │
                          │ * is_premium        │
                          │ * role              │
                          └──────┬──────┬──────┬─────────────┐
                                 │      │      │             │
                   ┌─────────────┤      │      │             │
                   │             │      │      │             │
                   │      ┌──────▼─┐    │      │             │
                   │      │ Profile │    │      │             │
                   │      │ (1:1)   │    │      │             │
                   │      └─────────┘    │      │             │
                   │                     │      │             │
            ┌──────▼──────────┐   ┌──────▼─┐  │    ┌─────────▼──────┐
            │ FinancialData   │   │ Payment│  │    │ Transaction    │
            │ (1:1)           │   │ (1:N)  │  │    │ (1:N)          │
            ├─────────────────┤   └────────┘  │    ├────────────────┤
            │ * id            │               │    │ * id           │
            │ * user_id (FK)  │               │    │ * user_id (FK) │
            │ * monthly income│               │    │ * amount       │
            │ * rent, bills   │               │    │ * category_id  │
            │ * savings       │               │    │ * category_type│
            │ * total_debt    │               │    │ * description  │
            └─────────────────┘               │    │ * date         │
                                              │    │ * currency     │
                                       ┌──────▼─────────┐
                                       │ Subscription   │
                                       │ (1:N)          │
                                       └────────────────┘

                    ┌───────────────────────────────────────────┐
                    │         Category (1:N User)               │
                    │                                           │
                    │ ├─ Groceries                             │
                    │ ├─ Utilities                             │
                    │ ├─ Transport                             │
                    │ └─ Entertainment                         │
                    └────────────────▲──────────────────────────┘
                                     │
                                     │ (Foreign Key)
                         ┌───────────┴────────────┐
                         │                        │
                    ┌────┴────┐          ┌────────▼─────┐
                    │ Budget  │          │ Transaction  │
                    │ (1:N)   │          │              │
                    ├─────────┤          └──────────────┘
                    │ * id    │
                    │ * user  │
                    │ * limit │
                    └─────────┘

    ┌──────────────────────────────────────────────────────────┐
    │                    Group Expense System                  │
    └──────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼─────┐      ┌───────▼───────┐    ┌──────▼──────┐
    │ Group     │      │ GroupMember   │    │ GroupExpense│
    │ (1:N)     │      │ (1:N)         │    │ (1:N)       │
    ├───────────┤      ├───────────────┤    ├─────────────┤
    │ * id      │◄─────│ * group_id(FK)│    │ * id        │
    │ * name    │      │ * user_id (FK)│    │ * amount    │
    │ * desc    │      │ * joined_at   │    │ * paid_by   │
    └───────────┘      └───────────────┘    │ * split... │
                             │               │             │
                             │          ┌────▼─────────┐
                             │          │ Settlement   │
                             │          │ (1:N)        │
                             │          ├──────────────┤
                             │          │ * member_id  │
                             │          │ * amount     │
                             │          │ * settled    │
                             │          └──────────────┘
                             │
                    ┌────────┴────────┐
                    │ ManyToMany      │
                    │ split_members   │
                    └─────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │                  Insights System                         │
    └──────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │
    ┌────▼──────────┐    ┌────▼────────────┐
    │ BudgetInsight │    │ SavingsGoal     │
    │ (1:N)         │    │ (1:N)           │
    ├───────────────┤    ├─────────────────┤
    │ * user_id(FK) │    │ * user_id (FK)  │
    │ * category    │    │ * goal_name     │
    │ * avg_spending│    │ * target_amount │
    │ * forecast    │    │ * saved_amount  │
    │ * recommend   │    │ * deadline      │
    └───────────────┘    │ * status        │
                         └─────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │              Other Supporting Systems                    │
    └──────────────────────────────────────────────────────────┘

    ┌─────────────────┐    ┌──────────────┐    ┌────────────┐
    │ Notification    │    │ ActivityLog  │    │ RecurringPmt│
    │ (Broadcast)     │    │ (Audit)      │    │ (1:N)      │
    ├─────────────────┤    ├──────────────┤    ├────────────┤
    │ * recipients    │    │ * user_id(FK)│    │ * user_id  │
    │ * title         │    │ * action     │    │ * name     │
    │ * message       │    │ * timestamp  │    │ * amount   │
    │ * status        │    └──────────────┘    │ * frequency│
    └─────────────────┘                        │ * next_date│
                                               └────────────┘
```

### Relationship Summary

**One-to-One (1:1) Relationships**:
- User ↔ Profile
- User ↔ FinancialData

**One-to-Many (1:N) Relationships**:
- User → Transactions
- User → Categories
- User → Budgets
- User → BudgetHistory
- User → Groups
- User → Payments
- User → Subscriptions
- User → RecurringPayments
- User → BudgetInsights
- User → SavingsGoals
- User → ActivityLogs
- Category → Transactions
- Group → GroupMembers
- Group → GroupExpenses
- GroupMember → GroupExpenses (paid_by)
- GroupMember → Settlements

**Many-to-Many (M:N) Relationships**:
- GroupExpense ↔ GroupMember (split_members)

---

## Access Pattern Summary

### How to Access Each File from Frontend

1. **User Authentication**:
   - `users/views.py` → `POST /api/users/register/`, `POST /api/token/`
   - From: `expense-frontend/src/services/api.js`

2. **Transaction Management**:
   - `transactions/views.py` → REST endpoints
   - From: Dashboard, transaction entry form
   - Flow: Frontend → API → Views → Serializers → Models → DB

3. **Voice Processing**:
   - `transactions/views.py` → `process_voice_entry()`
   - Uses: `transactions/nlp_processing.py`
   - Uses: `transactions/categorizer.py`
   - From: Voice input button in frontend

4. **Budget Tracking**:
   - `transactions/views.py` → Budget endpoints
   - From: Budget dashboard page

5. **Group Expenses**:
   - `group_expenses/views.py` → Group endpoints
   - From: Group expenses page
   - Permissions: `group_expenses/permissions.py` (IsGroupMember)

6. **Payments**:
   - `payments/views.py` → Payment endpoints
   - Uses: `payments/utils.py` (Razorpay integration)
   - From: Premium upgrade page
   - Webhook: Razorpay → `/api/payments/verify/`

7. **Financial Insights**:
   - `insights/views.py` → Analytics endpoints
   - Uses: `insights/utils.py` (calculations)
   - From: Insights/Analytics page

8. **Admin Dashboard**:
   - `admin_dashboard/views.py` → Dashboard endpoints
   - From: `/admin/` Django admin interface or custom dashboard page

---

## Key Takeaways

✓ **Modular Architecture**: Each app handles a specific domain
✓ **RESTful API**: Standard HTTP methods and status codes
✓ **Async Processing**: Celery for background tasks
✓ **Security**: JWT authentication, permissions classes
✓ **Scalability**: Django ORM, indexed models, efficient queries
✓ **User-Centric**: Role-based access, premium features
✓ **ML Integration**: NLP for voice, classification for categorization
✓ **Third-Party Integration**: Razorpay for payments, Stanza for NLP

---

**Document Version**: 1.0
**Last Updated**: December 31, 2025
**Maintained by**: AI Tracking Expenses Team
