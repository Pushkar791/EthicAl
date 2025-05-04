from flask import render_template, redirect, url_for, request, jsonify, flash, current_app
from flask_login import current_user, login_required
from app import db
from app.modules.virtual_assistant import bp
from app.models import AssistantInteraction, User, AIModel, Course, BiasReport, PolicyDocument
import json
import os
import re
import random
from datetime import datetime

# Enhanced assistant with better context handling and more sophisticated NLP
class EnhancedEthicsAssistant:
    def __init__(self):
        self.intents = {
            'greeting': [
                r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgreetings\b', 
                r'\bgood morning\b', r'\bgood afternoon\b', r'\bgood evening\b'
            ],
            'farewell': [
                r'\bbye\b', r'\bgoodbye\b', r'\bsee you\b', r'\bsee you later\b', 
                r'\bfarewell\b', r'\bthanks bye\b'
            ],
            'help': [
                r'\bhelp\b', r'\bassistance\b', r'\bsupport\b', r'\bguide\b', 
                r'\bhow to\b', r'\bwhat can you do\b', r'\bcapabilities\b'
            ],
            'policy': [
                r'\bpolicy\b', r'\bpolicies\b', r'\bguideline\b', r'\bguidelines\b', 
                r'\brules\b', r'\bcompliance\b', r'\bregulation\b', r'\bstandard\b'
            ],
            'training': [
                r'\btraining\b', r'\bcourse\b', r'\blearn\b', r'\blearning\b', 
                r'\bstudy\b', r'\beducation\b', r'\bcertificate\b', r'\blesson\b'
            ],
            'bias': [
                r'\bbias\b', r'\bfairness\b', r'\bdiscrimination\b', r'\bunfair\b', 
                r'\bequal\b', r'\bequality\b', r'\bimbalance\b', r'\bretrain\b', 
                r'\bmitigation\b'
            ],
            'governance': [
                r'\bgovernance\b', r'\baudit\b', r'\bmonitoring\b', r'\bcontrol\b', 
                r'\bmetadata\b', r'\bdocumentation\b', r'\bversioning\b'
            ],
            'data_privacy': [
                r'\bprivacy\b', r'\bpersonal data\b', r'\bgdpr\b', r'\bccpa\b', 
                r'\bdata protection\b', r'\bpii\b', r'\bsensitive data\b'
            ],
            'data_request': [
                r'\bmy data\b', r'\bpersonal data\b', r'\binformation\b', 
                r'\bexport data\b', r'\bget my data\b', r'\baccess my data\b'
            ],
            'data_deletion': [
                r'\bdelete\b', r'\bremove\b', r'\berase\b', r'\bdeletion\b', 
                r'\bforget me\b', r'\bright to be forgotten\b', r'\bremove my data\b'
            ],
            'model_risk': [
                r'\brisk\b', r'\bthreat\b', r'\bvulnerability\b', r'\bimpact\b', 
                r'\bsafety\b', r'\bsecurity\b', r'\brobustness\b'
            ],
            'explainability': [
                r'\bexplain\b', r'\bexplainability\b', r'\btransparency\b', 
                r'\bblack box\b', r'\binterpretability\b', r'\bunderstand\b'
            ],
            'ethics_principles': [
                r'\bethics\b', r'\bprinciple\b', r'\bvalue\b', r'\bresponsible ai\b', 
                r'\bhuman rights\b', r'\bhuman-centered\b', r'\btrustworthy\b'
            ]
        }
        
        self.responses = {
            'greeting': [
                "Hello! How can I assist you with AI ethics and governance today?",
                "Hi there! Welcome to EthicAI assistant. How can I help you?",
                "Greetings! I'm here to help with your AI ethics questions."
            ],
            'farewell': [
                "Goodbye! Feel free to return if you have more questions.",
                "Farewell! Have a great day. Remember that ethical AI is everyone's responsibility.",
                "See you later! If you need more assistance with AI ethics, I'll be here."
            ],
            'help': [
                "I can help with:\n• Learning about AI ethics\n• Checking model bias\n• Ensuring compliance\n• Managing AI policies\n• Understanding data privacy\n• Accessing or deleting your data\nWhat would you like to know more about?",
                "Need assistance? I can guide you through:\n• Learning modules\n• Bias detection tools\n• Governance processes\n• Policy creation\n• Privacy compliance\n• Data access requests\nWhat are you interested in?",
                "I'm here to help with all aspects of ethical AI! You can ask about:\n• Training courses\n• Model bias analysis\n• Governance frameworks\n• Data privacy\n• Ethics principles\nJust let me know what you need."
            ],
            'policy': [
                "Our AI policies cover responsible development, deployment, and maintenance. Our key policy areas include:\n• Data privacy and protection\n• Model documentation requirements\n• Testing and validation standards\n• Monitoring and auditing procedures\nWould you like to know about a specific policy area?",
                "EthicAI maintains comprehensive policy documentation on:\n• Data governance\n• Model transparency\n• Fairness requirements\n• User consent\n• Accountability measures\nWhat specific aspect are you interested in?",
                "Our policy framework includes guidelines on:\n• Model documentation\n• Testing requirements\n• Monitoring and auditing\n• Risk assessment\n• Incident response\nCan I direct you to a specific policy document?"
            ],
            'training': [
                "We offer various training modules on:\n• AI ethics fundamentals\n• Fairness in machine learning\n• Responsible AI development\n• Privacy-preserving techniques\n• Governance frameworks\nWould you like me to show you the available courses?",
                "Our learning hub contains role-based courses for:\n• Developers\n• Data scientists\n• Managers\n• HR professionals\n• Policy makers\nWhat type of training are you looking for?",
                "You can access:\n• Interactive lessons\n• Ethical simulations\n• Knowledge assessments\n• Certificate programs\n• Specialized workshops\nWould you like a link to get started?"
            ],
            'bias': [
                "Our Bias Detection & Fairness Analyzer helps identify potential biases across dimensions like:\n• Gender\n• Age\n• Race\n• Socioeconomic status\n• Geographic location\nWould you like to learn how to use it?",
                "To check your model for bias:\n1. Upload your model or connect via API\n2. Provide a test dataset\n3. Select the dimensions to analyze\n4. Review the generated bias report\n5. Implement suggested improvements\nWould you like to start this process?",
                "Addressing bias requires both technical and procedural approaches:\n• Dataset balancing\n• Feature selection review\n• Algorithm adjustment\n• Regular testing\n• Documentation of limitations\nOur platform offers tools for all these aspects."
            ],
            'governance': [
                "Our governance module helps you:\n• Track model metadata\n• Document model versions\n• Maintain audit logs\n• Monitor compliance status\n• Generate reports\nHow can I help with your governance needs?",
                "Effective AI governance includes:\n• Clear accountability structures\n• Comprehensive documentation\n• Regular auditing\n• Risk assessment\n• Incident response plans\nWhich aspect would you like to explore?",
                "The Governance & Compliance Manager allows you to:\n• Register AI models\n• Track compliance status\n• Store policy documents\n• Generate compliance reports\n• Manage audit history\nWhat specific functionality do you need?"
            ],
            'data_privacy': [
                "Our platform is designed with privacy-by-design principles:\n• Data minimization\n• Purpose limitation\n• User consent management\n• Right to access and deletion\n• Secure data handling\nWhat aspect of data privacy are you interested in?",
                "We ensure compliance with major privacy regulations including:\n• GDPR (Europe)\n• CCPA/CPRA (California)\n• HIPAA (Healthcare)\n• PIPEDA (Canada)\n• LGPD (Brazil)\nDo you need guidance on a specific regulation?",
                "Our privacy practices include:\n• Transparent data collection\n• Consent management\n• Data access and portability\n• Deletion rights\n• Privacy impact assessments\nHow can I help with your privacy concerns?"
            ],
            'data_request': [
                "You can request an export of all your personal data by:\n1. Going to your profile page\n2. Selecting 'Privacy Settings'\n3. Clicking 'Export My Data'\n4. Confirming your identity\nYou'll receive a downloadable file within 24 hours. Would you like to do this now?",
                "To access your data:\n1. Navigate to Account Settings\n2. Select 'Data & Privacy'\n3. Click 'Request Data Export'\n4. Choose the data categories\n5. Submit your request\nThe data will be provided in a machine-readable format. Would you like a direct link?",
                "I can help you export your personal data. This will include:\n• Your profile information\n• Learning progress and certificates\n• Model uploads and results\n• Interaction history\n• Account preferences\nWould you like to proceed with a data request?"
            ],
            'data_deletion': [
                "If you'd like to delete your data:\n1. Go to your account settings\n2. Select 'Privacy'\n3. Click 'Delete My Data'\n4. Choose what to delete\n5. Confirm your decision\nNote that this may remove your account and all associated information. Would you like to proceed?",
                "You have the right to request deletion of your personal data. The process is:\n1. Visit your profile page\n2. Go to 'Privacy Settings'\n3. Select 'Delete My Data'\n4. Review the consequences\n5. Confirm with your password\nWould you like help with this process?",
                "To delete your data:\n1. Navigate to your profile\n2. Choose 'Privacy'\n3. Select 'Delete My Data'\n4. Specify full or partial deletion\n5. Confirm your identity\nPlease note this action cannot be undone. Some data may be retained for legal purposes. Would you like to proceed?"
            ],
            'model_risk': [
                "We categorize AI model risk into three levels:\n• Low: Models with minimal potential for harm\n• Medium: Models that may impact decisions or processes\n• High: Models that affect critical decisions about individuals\nEach level requires appropriate governance controls. What risk level are you dealing with?",
                "Mitigating AI risk involves:\n• Thorough testing and validation\n• Ongoing monitoring\n• Clear documentation\n• Explainability mechanisms\n• Human oversight\nOur platform provides tools for each of these areas. Would you like specific guidance?",
                "Risk assessment for AI includes evaluating:\n• Technical robustness\n• Potential for bias\n• Data quality issues\n• Security vulnerabilities\n• Alignment with values\nOur governance module can help document and track these risks. How can I assist you?"
            ],
            'explainability': [
                "Explainable AI techniques we support include:\n• Feature importance analysis\n• SHAP values\n• LIME explanations\n• Decision tree extraction\n• Counterfactual explanations\nThese can help make your models more transparent and understandable. Would you like more information on any of these?",
                "Making AI systems explainable is important for:\n• Building user trust\n• Complying with regulations\n• Identifying bias\n• Debugging models\n• Facilitating human oversight\nOur platform includes tools to generate explanations for model decisions. How can I help you implement these?",
                "We recommend different explainability approaches based on model type:\n• For tabular data: SHAP values and feature importance\n• For image recognition: Saliency maps and activation visualization\n• For text models: Attention visualization and key phrase highlighting\n• For all models: User-friendly explanations of general functionality\nWhat type of model are you working with?"
            ],
            'ethics_principles': [
                "Our AI ethics framework is based on these key principles:\n• Fairness and non-discrimination\n• Transparency and explainability\n• Privacy and security\n• Human agency and oversight\n• Societal and environmental wellbeing\n• Accountability\nWhich principle would you like to explore further?",
                "Ethical AI development requires consideration of:\n• Human rights and dignity\n• Diversity, fairness, and non-discrimination\n• Transparency and explainability\n• Safety and reliability\n• Privacy and data governance\n• Accountability and responsibility\nOur learning modules cover each of these areas in depth. Would you like more information?",
                "Our approach to responsible AI is guided by:\n• Human-centered design principles\n• Collaborative development processes\n• Ongoing risk assessment\n• Inclusive testing protocols\n• Regular ethical reviews\n• Continuous improvement\nHow can I help you implement these practices in your organization?"
            ],
            'unknown': [
                "I'm not sure I understand your question about AI ethics. Could you rephrase or specify which aspect of ethical AI you're interested in?",
                "I don't have specific information on that topic. Would you like to know about our training courses, bias detection tools, governance framework, or privacy features instead?",
                "I'm still learning and don't have an answer for that specific question. Can I help you with something else related to AI ethics, such as bias detection, compliance, or ethical principles?"
            ]
        }
        
        # Context memory to track conversation
        self.conversation_context = {}
    
    def get_intent(self, query, user_id):
        query = query.lower()
        matched_intents = {}
        
        # Score each intent based on how many patterns match
        for intent, patterns in self.intents.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, query):
                    matches += 1
            if matches > 0:
                matched_intents[intent] = matches
        
        # If no matches, check if we can infer from context
        if not matched_intents and user_id in self.conversation_context:
            previous_intent = self.conversation_context[user_id].get('last_intent')
            if previous_intent:
                # Check if query seems like a follow-up
                follow_up_indicators = ['yes', 'sure', 'please', 'ok', 'okay', 'go ahead', 'tell me more', 'i would', 'show me']
                if any(indicator in query for indicator in follow_up_indicators):
                    return previous_intent
        
        # Return the intent with the most matches, or 'unknown'
        if matched_intents:
            return max(matched_intents, key=matched_intents.get)
        return 'unknown'
    
    def get_response(self, intent, query, user_id):
        # Update context
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {}
        
        self.conversation_context[user_id]['last_intent'] = intent
        
        # Customize response based on specific content in the query if needed
        if intent == 'training' and 'certificate' in query.lower():
            # Personalized response about certificates
            return "You can earn certificates by completing our ethics courses and passing the assessments. Each certificate validates your understanding of specific AI ethics topics. Would you like to see the available certificate programs?"
        
        elif intent == 'bias' and any(term in query.lower() for term in ['gender', 'race', 'age']):
            # Specific bias dimension mentioned
            for term in ['gender', 'race', 'age']:
                if term in query.lower():
                    return f"Our bias detection tools can specifically analyze {term} bias in your models. This includes statistical disparity measures, visualization of outcome differences, and recommended mitigation strategies. Would you like to learn how to run a {term} bias analysis?"
        
        elif intent == 'data_deletion' and 'all' in query.lower():
            # Complete account deletion request
            return "I understand you want to delete all your data. This will permanently remove your account, learning progress, uploaded models, and interaction history. This action cannot be undone. To proceed, please go to Account Settings > Privacy > Delete All Data and confirm with your password."
        
        # Default responses
        if intent in self.responses:
            return random.choice(self.responses[intent])
        
        return random.choice(self.responses['unknown'])
    
    def process_query(self, query, user_id, user_consent=False):
        # Apply data minimization if no consent
        if not user_consent:
            query = self.sanitize_query(query)
        
        # Determine intent
        intent = self.get_intent(query, user_id)
        
        # Generate response
        response = self.get_response(intent, query, user_id)
        
        return {
            'intent': intent,
            'response': response
        }
    
    def sanitize_query(self, query):
        # Enhanced sanitization for better privacy protection
        
        # Remove potential email addresses
        query = re.sub(r'\S+@\S+\.\S+', '[EMAIL REDACTED]', query)
        
        # Remove potential phone numbers (various formats)
        query = re.sub(r'\b(\+\d{1,3}[-.\s]?)?(\d{3}[-.\s]?)?(\d{3}[-.\s]?)(\d{4})\b', '[PHONE REDACTED]', query)
        
        # Remove potential credit card numbers
        query = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CARD REDACTED]', query)
        
        # Remove potential SSN/government IDs
        query = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[ID REDACTED]', query)
        
        # Remove potential addresses
        query = re.sub(r'\b\d+\s+[A-Za-z\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Parkway|Pkwy)\b', '[ADDRESS REDACTED]', query)
        
        # Remove potential full names (this is a simplified approach)
        query = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NAME REDACTED]', query)
        
        return query
    
    def get_db_enhanced_response(self, intent, user_id):
        """Enhance the response with data from the database if applicable"""
        try:
            if intent == 'policy':
                # Get real policies from the database
                try:
                    policies = PolicyDocument.query.limit(3).all()
                    if policies:
                        policy_list = "\n".join([f"• {policy.title} (v{policy.version})" for policy in policies])
                        return f"Here are some of our current AI policies:\n{policy_list}\n\nWould you like to view any of these policy documents?"
                except Exception as e:
                    print(f"Error fetching policy documents: {e}")
                    return None
            
            elif intent == 'bias':
                # Get information about recent bias reports for models owned by the user
                try:
                    user_models = AIModel.query.filter_by(owner_id=user_id).all()
                    if user_models:
                        model_ids = [model.id for model in user_models]
                        reports = BiasReport.query.filter(BiasReport.ai_model_id.in_(model_ids)).limit(2).all()
                        if reports:
                            return f"You have {len(reports)} recent bias reports. Would you like to view these reports or create a new bias analysis?"
                except Exception as e:
                    print(f"Error fetching bias reports: {e}")
                    return None
            
            # No database enhancement needed or available
            return None
        except Exception as e:
            print(f"Database error in enhanced response: {e}")
            # Return None instead of redirecting since this is called by another function
            return None

# Initialize enhanced assistant
assistant = EnhancedEthicsAssistant()

@bp.route('/')
@login_required
def index():
    """Virtual Assistant home page"""
    try:
        recent_interactions = AssistantInteraction.query.filter_by(
            user_id=current_user.id
        ).order_by(AssistantInteraction.timestamp.desc()).limit(5).all()
        
        return render_template(
            'virtual_assistant/index.html',
            title='Privacy-Aware Virtual Assistant',
            recent_interactions=recent_interactions,
            now=datetime.now(),
            datetime=datetime
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """Chat with the virtual assistant"""
    try:
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            query = data.get('query', '')
            consent_given = data.get('consent_given', 'false') == 'true'
            
            if not query:
                if request.is_json:
                    return jsonify({'error': 'No query provided'}), 400
                flash('Please enter a question or command')
                return redirect(url_for('virtual_assistant.chat'))
            
            try:
                # Process query with enhanced assistant
                result = assistant.process_query(query, current_user.id, consent_given)
                
                # Try to enhance response with database information
                try:
                    db_enhanced = assistant.get_db_enhanced_response(result['intent'], current_user.id)
                    if db_enhanced:
                        result['response'] = db_enhanced
                except Exception as e:
                    print(f"Error enhancing response with DB data: {e}")
                    # Continue with the standard response
                
                # Save interaction to database
                try:
                    interaction = AssistantInteraction(
                        query=query,
                        response=result['response'],
                        consent_given=consent_given,
                        user_id=current_user.id
                    )
                    
                    db.session.add(interaction)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving interaction to database: {e}")
                    db.session.rollback()
                    # Continue processing without saving to DB
                
                if request.is_json:
                    return jsonify({
                        'response': result['response'],
                        'intent': result['intent']
                    })
                
                return render_template(
                    'virtual_assistant/chat.html',
                    title='Chat with Assistant',
                    query=query,
                    response=result['response']
                )
            except Exception as e:
                print(f"Error processing chat: {e}")
                db.session.rollback()
                if request.is_json:
                    return jsonify({'error': 'An error occurred while processing your request', 'details': str(e)}), 500
                flash("An error occurred while processing your request. Please try again.", "error")
                return render_template('virtual_assistant/chat.html', title='Chat with Assistant')
        
        return render_template(
            'virtual_assistant/chat.html',
            title='Chat with Assistant'
        )
    except Exception as e:
        print(f"Error loading chat interface: {e}")
        flash("An error occurred while loading the chat interface. Please try again later.", "error")
        return redirect(url_for('virtual_assistant.index'))

@bp.route('/history')
@login_required
def history():
    """View interaction history"""
    try:
        page = request.args.get('page', 1, type=int)
        interactions = AssistantInteraction.query.filter_by(
            user_id=current_user.id
        ).order_by(AssistantInteraction.timestamp.desc()).paginate(
            page=page, per_page=10
        )
        
        return render_template(
            'virtual_assistant/history.html',
            title='Interaction History',
            interactions=interactions,
            now=datetime.now(),
            datetime=datetime
        )
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('virtual_assistant.index'))

@bp.route('/delete_history', methods=['POST'])
@login_required
def delete_history():
    """Delete interaction history"""
    try:
        # Check if specific interaction ID is provided
        interaction_id = request.form.get('interaction_id')
        
        if interaction_id:
            # Delete specific interaction
            try:
                interaction = AssistantInteraction.query.filter_by(
                    id=interaction_id, user_id=current_user.id
                ).first_or_404()
                
                db.session.delete(interaction)
                db.session.commit()
                
                if request.is_json:
                    return jsonify({'message': 'Interaction deleted successfully'})
                
                flash('Interaction deleted successfully')
            except Exception as e:
                print(f"Error deleting interaction: {e}")
                flash("Failed to delete the interaction. Please try again.")
                db.session.rollback()
        else:
            # Delete all interaction history
            try:
                AssistantInteraction.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                
                if request.is_json:
                    return jsonify({'message': 'Interaction history deleted successfully'})
                
                flash('Interaction history deleted successfully')
            except Exception as e:
                print(f"Error deleting interaction history: {e}")
                flash("Failed to delete interaction history. Please try again.")
                db.session.rollback()
        
        return redirect(url_for('virtual_assistant.history'))
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index'))

@bp.route('/export_data', methods=['GET'])
@login_required
def export_data():
    """Export user's assistant interaction data"""
    try:
        interactions = AssistantInteraction.query.filter_by(
            user_id=current_user.id
        ).order_by(AssistantInteraction.timestamp.desc()).all()
        
        # Format data for export
        exported_data = {
            'user_id': current_user.id,
            'username': current_user.username,
            'export_date': datetime.utcnow().isoformat(),
            'interactions': [
                {
                    'query': interaction.query or "",
                    'response': interaction.response or "",
                    'timestamp': interaction.timestamp.isoformat(),
                    'consent_given': interaction.consent_given
                }
                for interaction in interactions
            ]
        }
        
        return jsonify(exported_data)
    except Exception as e:
        print(f"Database error: {e}")
        flash("An error occurred while processing your request. Please try again later.", "error")
        return redirect(url_for('main.index')) 