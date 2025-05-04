# EthicAI – Enterprise AI Responsibility Suite

A comprehensive platform for promoting ethical AI practices across organizations. The suite includes modules for AI ethics learning, governance & compliance management, bias detection & fairness analysis, and a privacy-aware virtual assistant.

## Features

### 1. AI Ethics Learning Hub
- Interactive lessons with videos and content
- Ethical decision-making simulations
- User assessments with scoring and certificate generation (PDF)
- Role-based dashboard (Developer, Manager, HR)

### 2. Governance & Compliance Manager
- Track AI model metadata (name, version, risk level)
- Maintain audit logs and history of changes
- Display compliance status with GDPR, IEEE, etc.
- Interface to create and store custom AI policy documents

### 3. Bias Detection & Fairness Analyzer
- Upload AI models (.pkl, .h5) or connect via API
- Upload datasets (CSV, JSON) for bias auditing
- Perform real-time bias detection using:
  - scikit-learn and pandas for model and data analysis
  - AIF360 for fairness metrics calculation
  - SHAP and LIME for model explainability
  - numpy for fast numerical operations
- Visual outputs:
  - Bias heatmaps showing intersectional effects
  - Demographic parity graphs showing outcome distributions
  - ROC curves for model performance evaluation
  - Interactive charts with Chart.js
- Bias mitigation suggestions:
  - Automated recommendations for data rebalancing
  - Feature selection guidance
  - Model retraining recommendations with explainable insights
  - Fairness constraint implementation options

### 4. Privacy-Aware Virtual Assistant
- NLP processing for HR or support queries
- Respect data minimization and consent-based prompts
- Allow users to request data deletion/export
- Log all interactions in a secure way

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with JWT
- **Data Visualization**: Chart.js
- **NLP**: Basic patterns (demo version) with hooks for spaCy/Hugging Face

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ethicai.git
   cd ethicai
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Access the application at [http://localhost:5000](http://localhost:5000)

### Environment Variables

Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ethicai.db  # or your PostgreSQL connection string
```

## Project Structure

```
ethicai/
│
├── app/                        # Main application package
│   ├── __init__.py            # App initialization
│   ├── models.py              # Database models
│   ├── static/                # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/             # HTML templates
│   ├── auth/                  # Authentication module
│   ├── main/                  # Main routes 
│   └── modules/               # Feature modules
│       ├── learning_hub/
│       ├── governance/
│       ├── bias_analyzer/
│       └── virtual_assistant/
│
├── instance/                  # Instance-specific files (database)
├── migrations/                # Database migrations
├── tests/                     # Test suite
├── .gitignore
├── requirements.txt           # Dependencies
├── run.py                     # Application entry point
└── README.md
```

## Usage Examples

### Adding a New User
1. Navigate to `/auth/register`
2. Fill in the registration form with username, email, password, and role
3. Submit the form to create an account

### Uploading an AI Model for Bias Analysis
1. Log in to your account
2. Navigate to Bias Analyzer → Upload Model
3. Fill in model details and upload your model file or provide API endpoint
4. Select bias types to analyze and upload test dataset
5. Enable explainability options (SHAP, LIME) and intersectional analysis
6. View the comprehensive analysis report with:
   - Fairness metrics (disparate impact, statistical parity)
   - Interactive visualizations of bias patterns
   - Feature importance explanations
   - Actionable mitigation recommendations

### Creating a New Policy Document
1. Log in as a Manager or Admin
2. Navigate to Governance → Policies → Add Policy
3. Enter policy title, content, and version
4. Save to make it available to the organization

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For questions or issues, please open an issue on GitHub or contact the development team at support@ethicai-example.com.

## Acknowledgements
- Bootstrap team for the responsive UI framework
- Flask community for the excellent web framework
- Data visualization libraries (Chart.js) for enabling insightful reports 