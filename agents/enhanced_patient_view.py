"""
AI-Powered Patient View with Test Results Explainer Integration
Combines all AI agents including the new test results explainer
"""
from typing import Dict, Any
import json
import asyncio
from datetime import datetime

# Import the test results explainer
from agents.test_results_explainer import generate_patient_explanation

# Debate visualizer removed - create inline function
async def visualize_agent_debate(analysis_data: Dict) -> Dict:
    """Create agent debate visualization from communication data"""
    agent_comm = analysis_data.get('agent_communication', {})
    conversation_highlights = analysis_data.get('conversation_highlights', [])
    
    # Calculate consensus score based on agent agreement
    total_messages = agent_comm.get('total_messages', 0)
    consensus_topics = agent_comm.get('consensus_topics', 0)
    consensus_score = min(100, (consensus_topics / max(1, total_messages)) * 100 + 50) if total_messages > 0 else 75
    
    # Create example dialogue from highlights
    example_dialogue = []
    for highlight in conversation_highlights:  # Show ALL highlights
        if '🚨' in highlight:
            parts = highlight.split(':', 1)  # Split only on first colon
            speaker = parts[0].replace('🚨', '').strip()
            message = parts[1].strip() if len(parts) > 1 else highlight
            example_dialogue.append({
                'speaker': f'Dr. {speaker}',
                'message': message,
                'badge': 'Critical Alert',
                'badge_class': 'critical'
            })
        elif '❓' in highlight:
            # Handle the full question format
            if ' asked: ' in highlight:
                speaker = highlight.split(' asked: ')[0].replace('❓', '').strip()
                message = highlight.split(' asked: ')[1]
                # Remove the trailing '...' if present
                if message.endswith('...'):
                    message = message[:-3]
                example_dialogue.append({
                    'speaker': f'Dr. {speaker}',
                    'message': message,
                    'badge': 'Question',
                    'badge_class': 'question'
                })
        elif '🤝' in highlight:
            message = highlight.replace('🤝', '').strip()
            if 'Consensus reached on' in message:
                example_dialogue.append({
                    'speaker': 'Medical Team',
                    'message': message,
                    'badge': 'Consensus',
                    'badge_class': 'consensus'
                })
            else:
                example_dialogue.append({
                    'speaker': 'Dr. Consensus',
                    'message': message,
                    'badge': 'Agreement',
                    'badge_class': 'consensus'
                })
        else:
            # Handle other message types without icons
            if ':' in highlight:
                parts = highlight.split(':', 1)
                speaker = parts[0].strip()
                message = parts[1].strip() if len(parts) > 1 else highlight
                example_dialogue.append({
                    'speaker': f'Dr. {speaker}',
                    'message': message,
                    'badge': 'Update',
                    'badge_class': 'info'
                })
    
    # Get full conversation log from raw data if available
    full_conversation = []
    raw_conversation = analysis_data.get('raw_conversation', [])
    if raw_conversation:
        for msg in raw_conversation:
            full_conversation.append({
                'timestamp': msg.get('timestamp', 'Unknown time'),
                'agent': msg.get('agent_id', 'Unknown'),
                'type': msg.get('type', 'message'),
                'content': msg.get('content', msg.get('topic', 'No content')),
                'priority': msg.get('priority', 0)
            })
    
    return {
        'show_debate_tab': total_messages > 5,  # Show tab if meaningful discussion
        'consensus_score': int(consensus_score),
        'agreement_level': 'Strong Agreement' if consensus_score > 80 else 'Moderate Agreement' if consensus_score > 60 else 'Some Disagreement',
        'patient_translation': f'Your medical team of {agent_comm.get("total_messages", 5)} specialists discussed your case. They asked {agent_comm.get("questions_asked", 0)} clarifying questions and raised {agent_comm.get("critical_alerts", 0)} important points before reaching their recommendation.',
        'example_dialogue': example_dialogue,
        'full_conversation': full_conversation,
        'has_full_log': len(full_conversation) > 0
    }

# Import existing AI agents
try:
    from agents.fixed_ai_patient_view import generate_ai_patient_view as original_ai_view
    ai_agents_available = True
except ImportError:
    ai_agents_available = False
    print("⚠️  Original AI agents not available")

async def generate_enhanced_patient_view(analysis_data: Dict) -> Dict:
    """
    Generate comprehensive patient view with test results explanation
    """
    try:
        # Get the original AI patient view if available
        if ai_agents_available:
            base_view = await original_ai_view(analysis_data)
        else:
            # Create basic structure
            base_view = {
                'success': True,
                'alert': {'show_alert': False, 'severity': 'low'},
                'admission': {'needs_admission': False},
                'cost': {'total_estimated': 5000},
                'options': {'recommended_action': 'Follow up with your doctor'}
            }
        
        # Generate the comprehensive test explanation
        test_explanation = await generate_patient_explanation(analysis_data)
        
        # Generate debate visualization inline
        debate_summary = await visualize_agent_debate(analysis_data)
        
        # Enhance the base view with detailed explanations
        enhanced_view = {
            **base_view,
            'test_results_explanation': {
                'greeting': test_explanation.get('greeting', ''),
                'executive_summary': test_explanation.get('summary', ''),
                'sections': {
                    'lab_results': {
                        'title': '🔬 Your Blood Test Results',
                        'content': test_explanation.get('lab_explanation', ''),
                        'icon': 'flask'
                    },
                    'imaging': {
                        'title': '🩻 Your X-Ray Results', 
                        'content': test_explanation.get('imaging_explanation', ''),
                        'icon': 'x-ray'
                    },
                    'risk_assessment': {
                        'title': '📊 Your Risk Assessment',
                        'content': test_explanation.get('risk_explanation', ''),
                        'icon': 'chart-line'
                    },
                    'diagnosis': {
                        'title': '🏥 Your Diagnosis',
                        'content': test_explanation.get('diagnosis_explanation', ''),
                        'icon': 'stethoscope'
                    },
                    'treatment': {
                        'title': '💊 Your Treatment Plan',
                        'content': test_explanation.get('treatment_rationale', ''),
                        'icon': 'pills'
                    },
                    'timeline': {
                        'title': '📅 What to Expect',
                        'content': test_explanation.get('what_to_expect', ''),
                        'icon': 'calendar'
                    }
                },
                'medical_team_note': test_explanation.get('consensus_note', ''),
                'reassurance': test_explanation.get('reassurance', ''),
                'complete_narrative': test_explanation.get('personalized_narrative', '')
            }
        }
        
        # Add conversation-style summary to alert if needed
        if enhanced_view['alert'].get('show_alert', False):
            enhanced_view['alert']['patient_friendly_message'] = test_explanation.get('summary', '')
        
        # Add explanation to admission section
        if enhanced_view['admission'].get('needs_admission', False):
            enhanced_view['admission']['patient_explanation'] = (
                test_explanation.get('treatment_rationale', '') + "\n\n" +
                test_explanation.get('what_to_expect', '')
            )
        
        # Add narrative to options
        enhanced_view['options']['detailed_explanation'] = test_explanation.get('personalized_narrative', '')
        
        # Add debate visualization
        enhanced_view['medical_team_discussion'] = debate_summary
        enhanced_view['show_debate_tab'] = debate_summary.get('show_debate_tab', False)
        
        # Add metadata
        enhanced_view['generated_at'] = datetime.now().isoformat()
        enhanced_view['explanation_version'] = '2.0'
        
        return enhanced_view
        
    except Exception as e:
        print(f"❌ Error in enhanced patient view: {e}")
        import traceback
        traceback.print_exc()
        
        # Return minimal safe response
        return {
            'success': True,
            'alert': {
                'show_alert': False,
                'severity': 'low',
                'message': 'Please consult with your healthcare provider'
            },
            'admission': {
                'needs_admission': False,
                'reason': 'To be determined by your doctor'
            },
            'cost': {
                'total_estimated': 0,
                'message': 'Cost information unavailable'
            },
            'options': {
                'recommended_action': 'Please see your healthcare provider for a complete evaluation'
            },
            'test_results_explanation': {
                'greeting': 'Hello! Your test results are being processed.',
                'executive_summary': 'Please speak with your healthcare provider for a detailed explanation of your results.'
            },
            'error': str(e)
        }

# For backward compatibility
async def generate_ai_patient_view(analysis_data: Dict) -> Dict:
    """
    Wrapper for backward compatibility
    """
    return await generate_enhanced_patient_view(analysis_data)
