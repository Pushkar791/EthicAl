from flask import render_template, redirect, url_for, request, jsonify, send_file, current_app, flash
from flask_login import current_user, login_required
from app import db
from app.modules.learning_hub import bp
from app.models import Course, Lesson, Assessment, AssessmentAttempt, Question, QuestionOption, UserAnswer, Certificate
import io
from datetime import datetime
import os

@bp.route('/')
@login_required
def index():
    """Learning hub home page showing available courses"""
    try:
        courses = Course.query.all()
        return render_template('learning_hub/index.html', title='Learning Hub', courses=courses)
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/courses')
@login_required
def courses():
    """List all available courses"""
    try:
        courses = Course.query.all()
        return render_template('learning_hub/courses.html', title='Courses', courses=courses)
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/course/<int:course_id>')
@login_required
def course(course_id):
    """View a specific course and its lessons"""
    try:
        course = Course.query.get_or_404(course_id)
        lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
        assessments = Assessment.query.filter_by(course_id=course_id).all()
        return render_template(
            'learning_hub/course.html', 
            title=course.title, 
            course=course, 
            lessons=lessons, 
            assessments=assessments
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """View a specific lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        next_lesson = Lesson.query.filter_by(
            course_id=lesson.course_id, 
            order=lesson.order + 1
        ).first()
        return render_template(
            'learning_hub/lesson.html', 
            title=lesson.title, 
            lesson=lesson,
            next_lesson=next_lesson
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/assessment/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def assessment(assessment_id):
    """Take an assessment"""
    try:
        assessment = Assessment.query.get_or_404(assessment_id)
        
        # Check if user has already passed this assessment
        existing_attempt = AssessmentAttempt.query.filter_by(
            user_id=current_user.id,
            assessment_id=assessment_id,
            passed=True
        ).first()
        
        if existing_attempt:
            return redirect(url_for('learning_hub.assessment_result', attempt_id=existing_attempt.id))
        
        if request.method == 'POST':
            # Create a new attempt
            attempt = AssessmentAttempt(
                user_id=current_user.id,
                assessment_id=assessment_id
            )
            db.session.add(attempt)
            
            # Process user answers
            total_points = 0
            earned_points = 0
            
            for question in assessment.questions:
                total_points += question.points
                
                # Get the user's selected option for this question
                selected_option_id = request.form.get(f'question_{question.id}')
                if selected_option_id:
                    selected_option = QuestionOption.query.get(selected_option_id)
                    
                    # Create user answer record
                    user_answer = UserAnswer(
                        attempt_id=attempt.id,
                        question_id=question.id,
                        selected_option_id=selected_option_id
                    )
                    db.session.add(user_answer)
                    
                    # Check if answer is correct
                    if selected_option and selected_option.is_correct:
                        earned_points += question.points
            
            # Calculate score and check if passed
            if total_points > 0:
                score = (earned_points / total_points) * 100
            else:
                score = 0
                
            attempt.score = score
            attempt.passed = score >= assessment.passing_score
            attempt.completed_at = datetime.utcnow()
            
            # If passed, create a certificate
            if attempt.passed:
                certificate = Certificate(
                    title=f"Certificate of Completion - {assessment.course.title}",
                    pdf_path=f"certificates/{current_user.id}_{assessment.id}.pdf",  # Will be generated later
                    user_id=current_user.id,
                    course_id=assessment.course_id
                )
                db.session.add(certificate)
                
            db.session.commit()
            return redirect(url_for('learning_hub.assessment_result', attempt_id=attempt.id))
        
        questions = Question.query.filter_by(assessment_id=assessment_id).all()
        return render_template(
            'learning_hub/assessment.html',
            title=assessment.title,
            assessment=assessment,
            questions=questions
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/assessment_result/<int:attempt_id>')
@login_required
def assessment_result(attempt_id):
    """View assessment results"""
    try:
        attempt = AssessmentAttempt.query.get_or_404(attempt_id)
        
        # Make sure the attempt belongs to the current user
        if attempt.user_id != current_user.id:
            return redirect(url_for('learning_hub.index'))
        
        return render_template(
            'learning_hub/assessment_result.html',
            title='Assessment Result',
            attempt=attempt
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/certificates')
@login_required
def certificates():
    """View user's earned certificates"""
    try:
        certificates = Certificate.query.filter_by(user_id=current_user.id).all()
        return render_template(
            'learning_hub/certificates.html',
            title='My Certificates',
            certificates=certificates
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/certificate/<int:certificate_id>')
@login_required
def view_certificate(certificate_id):
    """View a specific certificate"""
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        
        # Make sure the certificate belongs to the current user
        if certificate.user_id != current_user.id and not current_user.role == 'admin':
            return redirect(url_for('learning_hub.certificates'))
        
        return render_template(
            'learning_hub/certificate.html',
            title='Certificate',
            certificate=certificate
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/certificate/<int:certificate_id>/download')
@login_required
def download_certificate(certificate_id):
    """Download a certificate PDF"""
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        
        # Make sure the certificate belongs to the current user
        if certificate.user_id != current_user.id and not current_user.role == 'admin':
            return redirect(url_for('learning_hub.certificates'))
        
        # Generate PDF if it doesn't exist yet
        pdf_path = os.path.join(current_app.static_folder, certificate.pdf_path)
        
        # For demonstration, just return a simple PDF
        if not os.path.exists(os.path.dirname(pdf_path)):
            os.makedirs(os.path.dirname(pdf_path))
            
        # Return the certificate PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Certificate-{certificate.id}.pdf"
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/plan_schedule', methods=['GET', 'POST'])
@login_required
def plan_schedule():
    """Create a learning schedule plan"""
    try:
        courses = Course.query.all()
        
        if request.method == 'POST':
            # Process the schedule form
            selected_courses = request.form.getlist('selected_courses')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            days_per_week = request.form.get('days_per_week')
            hours_per_day = request.form.get('hours_per_day')
            
            # Flash success message for demo
            flash("Your learning schedule has been created successfully!", "success")
            return redirect(url_for('learning_hub.index'))
        
        return render_template(
            'learning_hub/plan_schedule.html',
            title='Plan Your Learning Schedule',
            courses=courses
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/skill_assessment')
@login_required
def skill_assessment():
    """Take a skill assessment to find suitable courses"""
    try:
        return render_template(
            'learning_hub/skill_assessment.html',
            title='Skill Assessment'
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/add_demo_content')
@login_required
def add_demo_content():
    """Add demo courses, lessons, assessments and certificates"""
    try:
        # Check if demo content already exists
        if Course.query.filter_by(title="AI Ethics Fundamentals").first():
            flash("Demo content already exists", "info")
            return redirect(url_for('learning_hub.index'))
            
        # Create demo courses
        ai_ethics_course = Course(
            title="AI Ethics Fundamentals",
            description="Learn the fundamental principles of ethical AI development"
        )
        db.session.add(ai_ethics_course)
        
        ai_governance_course = Course(
            title="AI Governance for Professionals",
            description="Master AI governance frameworks and compliance requirements"
        )
        db.session.add(ai_governance_course)
        
        db.session.commit()
        
        # Add lessons to the first course
        lessons = [
            Lesson(title="Introduction to AI Ethics", 
                  content="<p>This introductory lesson covers the basic principles of AI ethics and why they matter.</p><h3>Learning Objectives</h3><ul><li>Understand the importance of ethics in AI</li><li>Identify key ethical challenges in AI systems</li><li>Recognize different ethical frameworks</li></ul>", 
                  order=1, course_id=ai_ethics_course.id),
            Lesson(title="Fairness in Machine Learning", 
                  content="<p>This lesson explores various definitions of fairness and techniques to achieve fair AI systems.</p><h3>Learning Objectives</h3><ul><li>Define different types of fairness metrics</li><li>Implement techniques to mitigate bias</li><li>Evaluate AI systems for fairness</li></ul>", 
                  order=2, course_id=ai_ethics_course.id),
            Lesson(title="Transparency and Explainability", 
                  content="<p>This lesson covers methods to make AI systems more transparent and explainable to users.</p><h3>Learning Objectives</h3><ul><li>Understand the importance of explainable AI</li><li>Explore techniques for model interpretability</li><li>Implement user-friendly explanations</li></ul>", 
                  order=3, course_id=ai_ethics_course.id)
        ]
        db.session.add_all(lessons)
        
        # Add lessons to the second course
        governance_lessons = [
            Lesson(title="AI Governance Frameworks", 
                  content="<p>This lesson introduces major AI governance frameworks worldwide.</p><h3>Learning Objectives</h3><ul><li>Compare global AI governance approaches</li><li>Analyze regulatory requirements</li><li>Implement governance structures</li></ul>", 
                  order=1, course_id=ai_governance_course.id),
            Lesson(title="Risk Management for AI", 
                  content="<p>This lesson covers risk assessment and mitigation strategies for AI systems.</p><h3>Learning Objectives</h3><ul><li>Conduct risk assessments for AI systems</li><li>Develop mitigation strategies</li><li>Implement ongoing monitoring processes</li></ul>", 
                  order=2, course_id=ai_governance_course.id)
        ]
        db.session.add_all(governance_lessons)
        
        # Create assessment for AI Ethics course
        ethics_assessment = Assessment(
            title="AI Ethics Assessment",
            description="Test your knowledge of AI ethics principles",
            passing_score=70.0,
            course_id=ai_ethics_course.id
        )
        db.session.add(ethics_assessment)
        db.session.commit()
        
        # Add questions to the assessment
        q1 = Question(
            text="Which of the following is a key principle of ethical AI?",
            question_type="multiple_choice",
            points=1,
            assessment_id=ethics_assessment.id
        )
        db.session.add(q1)
        db.session.commit()
        
        # Add options to the question
        options = [
            QuestionOption(text="Maximizing profit at all costs", is_correct=False, question_id=q1.id),
            QuestionOption(text="Fairness and non-discrimination", is_correct=True, question_id=q1.id),
            QuestionOption(text="Always using the most complex model", is_correct=False, question_id=q1.id),
            QuestionOption(text="Collecting as much user data as possible", is_correct=False, question_id=q1.id)
        ]
        db.session.add_all(options)
        
        q2 = Question(
            text="What does 'explainability' refer to in AI ethics?",
            question_type="multiple_choice",
            points=1,
            assessment_id=ethics_assessment.id
        )
        db.session.add(q2)
        db.session.commit()
        
        # Add options to the second question
        options2 = [
            QuestionOption(text="Making AI systems work faster", is_correct=False, question_id=q2.id),
            QuestionOption(text="Ability to understand and trust how AI makes decisions", is_correct=True, question_id=q2.id),
            QuestionOption(text="Explaining why AI is better than humans", is_correct=False, question_id=q2.id),
            QuestionOption(text="Making AI code open source", is_correct=False, question_id=q2.id)
        ]
        db.session.add_all(options2)
        
        # Create a demo certificate
        demo_certificate = Certificate(
            title=f"Certificate of Completion - {ai_ethics_course.title}",
            pdf_path=f"certificates/demo_certificate.pdf",
            user_id=current_user.id,
            course_id=ai_ethics_course.id
        )
        db.session.add(demo_certificate)
        
        db.session.commit()
        flash("Demo content has been added successfully!", "success")
        return redirect(url_for('learning_hub.index'))
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while adding demo content. Please try again later.", "error")
        return redirect(url_for('main.index')) 