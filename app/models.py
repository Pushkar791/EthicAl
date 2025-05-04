from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# User roles
ROLES = {
    'ADMIN': 'admin',
    'DEVELOPER': 'developer',
    'MANAGER': 'manager',
    'HR': 'hr',
    'USER': 'user'
}

# Association tables
user_teams = db.Table('user_teams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=ROLES['USER'])
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    certificates = db.relationship('Certificate', backref='user', lazy='dynamic')
    ai_models = db.relationship('AIModel', backref='owner', lazy='dynamic')
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic')
    assistant_interactions = db.relationship('AssistantInteraction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('User', secondary=user_teams, lazy='subquery',
                             backref=db.backref('teams', lazy=True))
    ai_models = db.relationship('AIModel', backref='team', lazy='dynamic')
    
    def __repr__(self):
        return f'<Team {self.name}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    assessments = db.relationship('Assessment', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.title}>'


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(256), nullable=True)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    
    def __repr__(self):
        return f'<Lesson {self.title}>'


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    passing_score = db.Column(db.Float, default=70.0)  # Percentage to pass
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    questions = db.relationship('Question', backref='assessment', lazy='dynamic')
    attempts = db.relationship('AssessmentAttempt', backref='assessment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Assessment {self.title}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    question_type = db.Column(db.String(20))  # multiple-choice, true-false, etc.
    points = db.Column(db.Integer, default=1)
    
    # Foreign Keys
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    
    # Relationships
    options = db.relationship('QuestionOption', backref='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<Question {self.id}>'


class QuestionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    
    def __repr__(self):
        return f'<QuestionOption {self.id}>'


class AssessmentAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='attempt', lazy='dynamic')
    
    def __repr__(self):
        return f'<AssessmentAttempt {self.id}>'


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempt.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    selected_option_id = db.Column(db.Integer, db.ForeignKey('question_option.id'))
    
    def __repr__(self):
        return f'<UserAnswer {self.id}>'


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    pdf_path = db.Column(db.String(256))
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    
    def __repr__(self):
        return f'<Certificate {self.id}>'


class AIModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    version = db.Column(db.String(64))
    description = db.Column(db.Text)
    model_type = db.Column(db.String(64))  # classification, regression, nlp, etc.
    risk_level = db.Column(db.String(20))  # low, medium, high
    file_path = db.Column(db.String(256), nullable=True)
    api_endpoint = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    
    # Relationships
    audit_logs = db.relationship('AuditLog', backref='ai_model', lazy='dynamic')
    bias_reports = db.relationship('BiasReport', backref='ai_model', lazy='dynamic')
    compliance_statuses = db.relationship('ComplianceStatus', backref='ai_model', lazy='dynamic')
    
    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>'


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(64))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<AuditLog {self.id}>'


class ComplianceFramework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    description = db.Column(db.Text)
    version = db.Column(db.String(64))
    
    # Relationships
    requirements = db.relationship('ComplianceRequirement', backref='framework', lazy='dynamic')
    
    def __repr__(self):
        return f'<ComplianceFramework {self.name}>'


class ComplianceRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    description = db.Column(db.Text)
    
    # Foreign Keys
    framework_id = db.Column(db.Integer, db.ForeignKey('compliance_framework.id'))
    
    def __repr__(self):
        return f'<ComplianceRequirement {self.code}>'


class ComplianceStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20))  # compliant, non-compliant, in-progress, not-applicable
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'))
    requirement_id = db.Column(db.Integer, db.ForeignKey('compliance_requirement.id'))
    
    def __repr__(self):
        return f'<ComplianceStatus {self.id}>'


class BiasReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(64))  # gender, age, race, etc.
    results = db.Column(db.JSON, default=lambda: "{}")
    visualizations = db.Column(db.JSON, default=lambda: "{}")  # Store chart data for visualizations
    explainability = db.Column(db.JSON, default=lambda: "{}")  # Store SHAP/LIME output images as base64
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ai_model_id = db.Column(db.Integer, db.ForeignKey('ai_model.id'))
    
    # Relationships
    recommendations = db.relationship('BiasRecommendation', backref='report', lazy='dynamic')
    
    def __repr__(self):
        return f'<BiasReport {self.id}>'


class BiasRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))  # high, medium, low
    action_items = db.Column(db.JSON, default=lambda: "[]")  # Store recommended actions as JSON array
    
    # Foreign Keys
    report_id = db.Column(db.Integer, db.ForeignKey('bias_report.id'))
    
    def __repr__(self):
        return f'<BiasRecommendation {self.id}>'


class PolicyDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    content = db.Column(db.Text)
    version = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<PolicyDocument {self.title}>'


class AssistantInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, default="")
    response = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    consent_given = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<AssistantInteraction {self.id}>' 