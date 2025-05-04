from flask import render_template, redirect, url_for, request, jsonify, flash, current_app
from flask_login import current_user, login_required
from app import db
from app.modules.governance import bp
from app.models import AIModel, AuditLog, ComplianceFramework, ComplianceRequirement
from app.models import ComplianceStatus, PolicyDocument, Team
from datetime import datetime
import json
import os
import re

@bp.route('/')
@login_required
def index():
    """Governance & Compliance Manager home page"""
    try:
        ai_models = AIModel.query.filter_by(owner_id=current_user.id).all()
        
        # Also include models owned by teams the user belongs to
        for team in current_user.teams:
            team_models = AIModel.query.filter_by(team_id=team.id).all()
            for model in team_models:
                if model not in ai_models:
                    ai_models.append(model)
        
        policy_docs = PolicyDocument.query.order_by(PolicyDocument.updated_at.desc()).limit(5).all()
        frameworks = ComplianceFramework.query.all()
        
        return render_template(
            'governance/index.html',
            title='Governance & Compliance Manager',
            ai_models=ai_models,
            policy_docs=policy_docs,
            frameworks=frameworks,
            now=datetime.now(),
            datetime=datetime
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/ai_models')
@login_required
def ai_models():
    """List all AI models"""
    try:
        ai_models = AIModel.query.filter_by(owner_id=current_user.id).all()
        
        # Also include models owned by teams the user belongs to
        for team in current_user.teams:
            team_models = AIModel.query.filter_by(team_id=team.id).all()
            for model in team_models:
                if model not in ai_models:
                    ai_models.append(model)
        
        return render_template(
            'governance/ai_models.html',
            title='AI Models',
            ai_models=ai_models
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/ai_model/<int:model_id>')
@login_required
def ai_model(model_id):
    """View a specific AI model's details"""
    try:
        model = AIModel.query.get_or_404(model_id)
        
        # Check if user has access to this model
        if model.owner_id != current_user.id:
            has_access = False
            for team in current_user.teams:
                if model.team_id == team.id:
                    has_access = True
                    break
            if not has_access:
                flash('You do not have access to this AI model')
                return redirect(url_for('governance.ai_models'))
        
        audit_logs = AuditLog.query.filter_by(ai_model_id=model_id).order_by(AuditLog.timestamp.desc()).all()
        
        # Get compliance status
        compliance_statuses = {}
        for framework in ComplianceFramework.query.all():
            framework_statuses = ComplianceStatus.query.join(
                ComplianceRequirement, 
                ComplianceStatus.requirement_id == ComplianceRequirement.id
            ).filter(
                ComplianceStatus.ai_model_id == model_id,
                ComplianceRequirement.framework_id == framework.id
            ).all()
            
            if framework_statuses:
                # Calculate compliance percentage
                compliant_count = sum(1 for status in framework_statuses if status.status == 'compliant')
                total_count = len(framework_statuses)
                compliance_percentage = (compliant_count / total_count) * 100 if total_count > 0 else 0
                
                compliance_statuses[framework.name] = {
                    'percentage': compliance_percentage,
                    'statuses': framework_statuses
                }
        
        return render_template(
            'governance/ai_model_details.html',
            title=f'Model: {model.name}',
            model=model,
            audit_logs=audit_logs,
            compliance_statuses=compliance_statuses
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/ai_model/add', methods=['GET', 'POST'])
@login_required
def add_ai_model():
    """Add a new AI model"""
    try:
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            # Create new AI model
            model = AIModel(
                name=data.get('name'),
                version=data.get('version'),
                description=data.get('description'),
                model_type=data.get('model_type'),
                risk_level=data.get('risk_level'),
                api_endpoint=data.get('api_endpoint'),
                owner_id=current_user.id
            )
            
            # Handle team assignment if provided
            team_id = data.get('team_id')
            if team_id:
                model.team_id = team_id
            
            db.session.add(model)
            db.session.flush()  # Get the model ID
            
            # Create audit log entry
            audit_log = AuditLog(
                action='create',
                details=f'Created model {model.name} v{model.version}',
                user_id=current_user.id,
                ai_model_id=model.id
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'message': 'AI model added successfully',
                    'model_id': model.id
                }), 201
            
            flash('AI model added successfully')
            return redirect(url_for('governance.ai_model', model_id=model.id))
        
        teams = current_user.teams
        
        return render_template(
            'governance/add_ai_model.html',
            title='Add AI Model',
            teams=teams
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/ai_model/<int:model_id>/update', methods=['GET', 'POST'])
@login_required
def update_ai_model(model_id):
    """Update an existing AI model"""
    try:
        model = AIModel.query.get_or_404(model_id)
        
        # Check if user has permission to edit this model
        if model.owner_id != current_user.id:
            has_access = False
            for team in current_user.teams:
                if model.team_id == team.id:
                    has_access = True
                    break
            if not has_access:
                flash('You do not have permission to edit this AI model')
                return redirect(url_for('governance.ai_model', model_id=model_id))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            old_data = {
                'name': model.name,
                'version': model.version,
                'description': model.description,
                'model_type': model.model_type,
                'risk_level': model.risk_level,
                'api_endpoint': model.api_endpoint,
                'team_id': model.team_id
            }
            
            # Update model fields
            model.name = data.get('name', model.name)
            model.version = data.get('version', model.version)
            model.description = data.get('description', model.description)
            model.model_type = data.get('model_type', model.model_type)
            model.risk_level = data.get('risk_level', model.risk_level)
            model.api_endpoint = data.get('api_endpoint', model.api_endpoint)
            
            # Handle team assignment if provided
            team_id = data.get('team_id')
            if team_id:
                model.team_id = team_id
            
            # Create audit log for the update
            changes = []
            for key, old_value in old_data.items():
                new_value = getattr(model, key)
                if old_value != new_value:
                    changes.append(f'{key}: {old_value} -> {new_value}')
            
            if changes:
                audit_log = AuditLog(
                    action='update',
                    details=f'Updated model {model.name}: {", ".join(changes)}',
                    ai_model_id=model.id,
                    user_id=current_user.id
                )
                db.session.add(audit_log)
            
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': 'AI model updated successfully'}), 200
            
            flash('AI model updated successfully')
            return redirect(url_for('governance.ai_model', model_id=model_id))
        
        teams = current_user.teams
        
        return render_template(
            'governance/update_ai_model.html',
            title='Update AI Model',
            model=model,
            teams=teams
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/compliance')
@login_required
def compliance_frameworks():
    """List all compliance frameworks"""
    try:
        frameworks = ComplianceFramework.query.all()
        return render_template(
            'governance/compliance_frameworks.html',
            title='Compliance Frameworks',
            frameworks=frameworks
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/compliance/<int:framework_id>')
@login_required
def compliance_framework(framework_id):
    """View a specific compliance framework"""
    try:
        framework = ComplianceFramework.query.get_or_404(framework_id)
        requirements = framework.requirements.all()
        return render_template(
            'governance/compliance_framework.html',
            title=framework.name,
            framework=framework,
            requirements=requirements
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/ai_model/<int:model_id>/compliance/<int:framework_id>', methods=['GET', 'POST'])
@login_required
def model_compliance(model_id, framework_id):
    """Manage compliance status for a model against a framework"""
    try:
        model = AIModel.query.get_or_404(model_id)
        framework = ComplianceFramework.query.get_or_404(framework_id)
        
        # Check if user has permission
        if model.owner_id != current_user.id:
            has_access = False
            for team in current_user.teams:
                if model.team_id == team.id:
                    has_access = True
                    break
            if not has_access:
                flash('You do not have permission to manage compliance for this model')
                return redirect(url_for('governance.ai_model', model_id=model_id))
        
        requirements = ComplianceRequirement.query.filter_by(framework_id=framework_id).all()
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            for requirement in requirements:
                status_key = f'status_{requirement.id}'
                notes_key = f'notes_{requirement.id}'
                
                if status_key in data:
                    # Check if status already exists
                    status = ComplianceStatus.query.filter_by(
                        ai_model_id=model_id,
                        requirement_id=requirement.id
                    ).first()
                    
                    if status:
                        # Update existing status
                        status.status = data.get(status_key)
                        status.notes = data.get(notes_key, '')
                    else:
                        # Create new status
                        status = ComplianceStatus(
                            ai_model_id=model_id,
                            requirement_id=requirement.id,
                            status=data.get(status_key),
                            notes=data.get(notes_key, '')
                        )
                        db.session.add(status)
            
            # Add audit log entry
            audit_log = AuditLog(
                action='compliance_update',
                details=f'Updated compliance status for {framework.name}',
                ai_model_id=model_id,
                user_id=current_user.id
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash('Compliance status updated successfully')
            return redirect(url_for('governance.ai_model', model_id=model_id))
        
        # Get existing compliance statuses
        statuses = {}
        for requirement in requirements:
            status = ComplianceStatus.query.filter_by(
                ai_model_id=model_id,
                requirement_id=requirement.id
            ).first()
            
            statuses[requirement.id] = status
        
        return render_template(
            'governance/model_compliance.html',
            title=f'Compliance: {model.name} - {framework.name}',
            model=model,
            framework=framework,
            requirements=requirements,
            statuses=statuses
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/policies')
@login_required
def policies():
    """List all policy documents"""
    try:
        policies = PolicyDocument.query.order_by(PolicyDocument.updated_at.desc()).all()
        return render_template(
            'governance/policies.html',
            title='Policy Documents',
            policies=policies
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/policy/<int:policy_id>')
@login_required
def policy(policy_id):
    """View a specific policy document"""
    try:
        policy = PolicyDocument.query.get_or_404(policy_id)
        return render_template(
            'governance/policy.html',
            title=policy.title,
            policy=policy
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/policy/add', methods=['GET', 'POST'])
@login_required
def add_policy():
    """Add a new policy document"""
    # Only admin users can add policies
    if current_user.role != 'admin':
        flash('You do not have permission to add policy documents')
        return redirect(url_for('governance.policies'))
    
    try:
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            policy = PolicyDocument(
                title=data.get('title'),
                content=data.get('content'),
                version='1.0',
                created_by=current_user.id
            )
            
            db.session.add(policy)
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': 'Policy document added successfully'}), 201
            
            flash('Policy document added successfully')
            return redirect(url_for('governance.policy', policy_id=policy.id))
        
        return render_template(
            'governance/add_policy.html',
            title='Add Policy Document'
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/policy/<int:policy_id>/update', methods=['GET', 'POST'])
@login_required
def update_policy(policy_id):
    """Update an existing policy document"""
    try:
        policy = PolicyDocument.query.get_or_404(policy_id)
        if policy.created_by != current_user.id and current_user.role != 'admin':
            flash('You do not have permission to edit this policy document')
            return redirect(url_for('governance.policy', policy_id=policy_id))
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            # Update policy fields
            policy.title = data.get('title', policy.title)
            policy.content = data.get('content', policy.content)
            policy.version = data.get('version', policy.version)
            
            db.session.commit()
            
            if request.is_json:
                return jsonify({'message': 'Policy document updated successfully'}), 200
            
            flash('Policy document updated successfully')
            return redirect(url_for('governance.policy', policy_id=policy_id))
        
        return render_template(
            'governance/update_policy.html',
            title='Update Policy Document',
            policy=policy
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/approve_request', methods=['POST'])
@login_required
def approve_request():
    """Approve a model request"""
    try:
        # Check if user is a manager
        if current_user.role != 'manager':
            return jsonify({'error': 'Unauthorized access'}), 403
            
        data = request.get_json()
        model_name = data.get('model_name')
        requestor = data.get('requestor')
        
        if not model_name or not requestor:
            return jsonify({'error': 'Missing required data'}), 400
            
        # Try to find the model record
        model = AIModel.query.filter_by(name=model_name).first()
        
        if model:
            # Update model status
            model.status = 'approved'
            model.approved_by = current_user.id
            model.approved_at = datetime.now()
            
            # Create audit log
            audit_log = AuditLog(
                action='approve',
                details=f'Approved model {model_name} requested by {requestor}',
                user_id=current_user.id,
                ai_model_id=model.id
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Request approved successfully'}), 200
        else:
            # For demo data that might not be in the database
            return jsonify({'success': True, 'message': 'Request approved (demo mode)'}), 200
            
    except Exception as e:
        print(f"Error approving request: {e}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@bp.route('/reject_request', methods=['POST'])
@login_required
def reject_request():
    """Reject a model request"""
    try:
        # Check if user is a manager
        if current_user.role != 'manager':
            return jsonify({'error': 'Unauthorized access'}), 403
            
        data = request.get_json()
        model_name = data.get('model_name')
        requestor = data.get('requestor')
        reason = data.get('reason', 'No reason provided')
        
        if not model_name or not requestor:
            return jsonify({'error': 'Missing required data'}), 400
            
        # Try to find the model record
        model = AIModel.query.filter_by(name=model_name).first()
        
        if model:
            # Update model status
            model.status = 'rejected'
            model.rejection_reason = reason
            model.rejected_by = current_user.id
            model.rejected_at = datetime.now()
            
            # Create audit log
            audit_log = AuditLog(
                action='reject',
                details=f'Rejected model {model_name} requested by {requestor}. Reason: {reason}',
                user_id=current_user.id,
                ai_model_id=model.id
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Request rejected successfully'}), 200
        else:
            # For demo data that might not be in the database
            return jsonify({'success': True, 'message': 'Request rejected (demo mode)'}), 200
            
    except Exception as e:
        print(f"Error rejecting request: {e}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@bp.route('/review_request')
@login_required
def review_request():
    """Review a model request"""
    try:
        model_name = request.args.get('model')
        if not model_name:
            flash('Model name is required')
            return redirect(url_for('main.dashboard'))
            
        # Try to find the model record
        model = AIModel.query.filter_by(name=model_name).first()
        
        if model:
            return render_template(
                'governance/review_request.html',
                title=f'Review Request: {model_name}',
                model=model
            )
        else:
            # For demo data, show a template with hardcoded values
            dummy_model = {
                'name': model_name,
                'version': '1.0',
                'description': 'Demo model for review',
                'model_type': 'classification',
                'risk_level': 'medium',
                'created_at': datetime.now(),
                'owner': {'username': 'Unknown'},
            }
            return render_template(
                'governance/review_request.html',
                title=f'Review Request: {model_name}',
                model=dummy_model,
                is_demo=True
            )
            
    except Exception as e:
        print(f"Error reviewing request: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.dashboard')) 