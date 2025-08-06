"""
Intelligent Consensus Builder Agent that facilitates agreement among all agents
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

import sys
sys.path.append('..')
from core.blackboard import blackboard, MessageType, Priority

class IntelligentConsensusBuilder:
    """
    Consensus builder that ensures all agents reach agreement on patient care
    """
    
    def __init__(self):
        self.agent_id = "ConsensusBuilder"
        self.name = "Dr. Consensus"
        
        # Subscribe to all major decisions and questions
        blackboard.subscribe(
            self.agent_id,
            ["clinical_decision_complete", "question_*", "risk_assessment_complete",
             "*_confirmed", "*_complete"],
            self.handle_event
        )
        
        self.decision_tracking = defaultdict(list)
        
    async def build_consensus(self) -> Dict[str, Any]:
        """
        Facilitate consensus building among all agents
        """
        print(f"\n[{self.name}] 🤝 Building consensus from all agent inputs...")
        
        # Collect all opinions
        all_opinions = await self._collect_all_opinions()
        
        # Identify agreements and disagreements
        analysis = await self._analyze_agreements(all_opinions)
        
        # Resolve disagreements through discussion
        if analysis['disagreements']:
            await self._facilitate_disagreement_resolution(analysis['disagreements'])
        
        # Build final consensus
        final_consensus = await self._build_final_consensus(analysis)
        
        # Communicate consensus
        await self._communicate_consensus(final_consensus)
        
        # Create action plan
        action_plan = await self._create_unified_action_plan(final_consensus)
        
        return {
            'consensus': final_consensus,
            'action_plan': action_plan,
            'confidence': self._calculate_consensus_strength(analysis)
        }
    
    async def _collect_all_opinions(self) -> Dict:
        """
        Collect opinions from all agents
        """
        opinions = {
            'diagnosis': blackboard.agent_opinions.get('primary_diagnosis', {}),
            'disposition': blackboard.agent_opinions.get('disposition_recommendation', {}),
            'treatment': blackboard.agent_opinions.get('treatment_plan', {}),
            'risk_level': {},
            'key_findings': {}
        }
        
        # Extract risk assessments
        risk_data = blackboard.get_latest_finding('risk_assessment_complete')
        if risk_data:
            opinions['risk_level']['RiskStratifier'] = {
                'opinion': risk_data.get('overall_risk'),
                'confidence': 0.85
            }
        
        # Extract key findings from each agent
        lab_data = blackboard.get_latest_finding('lab_analysis_complete')
        if lab_data:
            opinions['key_findings']['LabAnalyzer'] = lab_data.get('patterns', [])
        
        imaging_data = blackboard.get_latest_finding('xray_analysis_complete')
        if imaging_data:
            opinions['key_findings']['ImageAnalyzer'] = imaging_data.get('impression', '')
        
        print(f"[{self.name}] Collected opinions from {len(set(sum([list(v.keys()) for v in opinions.values()], [])))} agents")
        
        return opinions
    
    async def _analyze_agreements(self, opinions: Dict) -> Dict:
        """
        Analyze where agents agree and disagree
        """
        analysis = {
            'agreements': [],
            'disagreements': [],
            'partial_agreements': []
        }
        
        # Check diagnosis consensus
        diagnosis_opinions = opinions.get('diagnosis', {})
        if diagnosis_opinions:
            diagnoses = [(agent, data['opinion']) for agent, data in diagnosis_opinions.items()]
            
            # Group similar diagnoses
            diagnosis_groups = defaultdict(list)
            for agent, diagnosis in diagnoses:
                # Check for specific conditions first
                if 'pneumonia' in diagnosis.lower():
                    key = 'pneumonia'
                elif 'sepsis' in diagnosis.lower():
                    key = 'sepsis'
                elif 'heart' in diagnosis.lower():
                    key = 'heart failure'
                elif 'bronchitis' in diagnosis.lower():
                    key = diagnosis  # Keep the full diagnosis for bronchitis
                elif 'respiratory' in diagnosis.lower():
                    key = diagnosis  # Keep respiratory conditions
                elif diagnosis.lower() != 'undifferentiated illness':
                    key = diagnosis  # Keep any other specific diagnosis
                else:
                    key = 'undifferentiated'
                diagnosis_groups[key].append(agent)
            
            # Find majority
            if len(diagnosis_groups) == 1:
                analysis['agreements'].append({
                    'topic': 'diagnosis',
                    'consensus': list(diagnosis_groups.keys())[0],
                    'agents': list(diagnosis_groups.values())[0]
                })
            else:
                analysis['disagreements'].append({
                    'topic': 'diagnosis',
                    'groups': dict(diagnosis_groups)
                })
        
        # Check disposition consensus
        disposition_opinions = opinions.get('disposition', {})
        if disposition_opinions:
            dispositions = [(agent, data['opinion']) for agent, data in disposition_opinions.items()]
            
            # Check if all agree on admission vs discharge
            admit_agents = [agent for agent, disp in dispositions if 'admit' in disp.lower() or 'icu' in disp.lower()]
            discharge_agents = [agent for agent, disp in dispositions if 'discharge' in disp.lower()]
            
            if len(admit_agents) > 0 and len(discharge_agents) == 0:
                analysis['agreements'].append({
                    'topic': 'disposition',
                    'consensus': 'admit',
                    'agents': admit_agents
                })
            elif len(admit_agents) > 0 and len(discharge_agents) > 0:
                analysis['disagreements'].append({
                    'topic': 'disposition',
                    'admit_agents': admit_agents,
                    'discharge_agents': discharge_agents
                })
        
        return analysis
    
    async def _facilitate_disagreement_resolution(self, disagreements: List[Dict]):
        """
        Help agents resolve disagreements through structured discussion
        """
        for disagreement in disagreements:
            topic = disagreement.get('topic')
            
            print(f"[{self.name}] 🤔 Disagreement detected on {topic}. Facilitating resolution...")
            
            if topic == 'diagnosis':
                # Ask each group to present their evidence
                await blackboard.ask_question(
                    self.agent_id,
                    "There's disagreement on the diagnosis. Can each agent briefly state "
                    "the TOP evidence supporting their diagnosis?",
                    target_agents=None  # All agents
                )
                
                # Give agents time to respond
                await asyncio.sleep(2)
                
                # Synthesize responses
                await blackboard.post(
                    self.agent_id,
                    MessageType.FINDING,
                    "diagnosis_debate_summary",
                    {
                        'disagreement': disagreement,
                        'resolution_attempt': "Requesting evidence-based justification"
                    },
                    Priority.HIGH
                )
            
            elif topic == 'disposition':
                # Present the dilemma
                admit_count = len(disagreement.get('admit_agents', []))
                discharge_count = len(disagreement.get('discharge_agents', []))
                
                await blackboard.post(
                    self.agent_id,
                    MessageType.FINDING,
                    "disposition_disagreement",
                    {
                        'admit_votes': admit_count,
                        'discharge_votes': discharge_count,
                        'question': "Should we err on the side of caution?"
                    },
                    Priority.HIGH
                )
                
                # In healthcare, safety first
                if admit_count > 0:
                    print(f"[{self.name}] Given the disagreement, recommending admission for safety")
    
    async def _build_final_consensus(self, analysis: Dict) -> Dict:
        """
        Build the final consensus recommendation
        """
        consensus = {
            'primary_diagnosis': '',
            'confidence_level': '',
            'disposition': '',
            'key_interventions': [],
            'dissenting_opinions': [],
            'areas_of_agreement': [],
            'final_recommendation': ''
        }
        
        # Diagnosis consensus
        if analysis['agreements']:
            diagnosis_agreement = next((a for a in analysis['agreements'] if a['topic'] == 'diagnosis'), None)
            if diagnosis_agreement:
                consensus['primary_diagnosis'] = diagnosis_agreement['consensus']
                consensus['areas_of_agreement'].append("Diagnosis")
        
        # If no agreement, use the clinical decision diagnosis
        if consensus['primary_diagnosis'] == '':
            clinical_decision = blackboard.get_latest_finding('clinical_decision_complete')
            if clinical_decision and clinical_decision.get('primary_diagnosis'):
                consensus['primary_diagnosis'] = clinical_decision['primary_diagnosis']
                consensus['dissenting_opinions'].append("Using clinical decision diagnosis")
            else:
                # Use the most confident diagnosis
                diagnosis_opinions = blackboard.agent_opinions.get('primary_diagnosis', {})
                if diagnosis_opinions:
                    best_diagnosis = max(diagnosis_opinions.items(), 
                                       key=lambda x: x[1].get('confidence', 0))
                    consensus['primary_diagnosis'] = best_diagnosis[1]['opinion']
                    consensus['dissenting_opinions'].append("Diagnosis remains debated")
        
        # Disposition consensus
        clinical_decision = blackboard.get_latest_finding('clinical_decision_complete')
        if clinical_decision and clinical_decision.get('disposition'):
            # Use the Clinical Decision's disposition directly
            consensus['disposition'] = clinical_decision['disposition']
            consensus['areas_of_agreement'].append("Disposition")
        else:
            # Fallback to old logic
            disposition_agreement = next((a for a in analysis['agreements'] if a['topic'] == 'disposition'), None)
            if disposition_agreement:
                consensus['disposition'] = disposition_agreement['consensus']
                consensus['areas_of_agreement'].append("Disposition")
            else:
                # Default to safer option
                consensus['disposition'] = "Admit for observation"
                consensus['dissenting_opinions'].append("Disposition debated - defaulting to admission")
        
        # Get treatment recommendations
        clinical_decision = blackboard.get_latest_finding('clinical_decision_complete')
        if clinical_decision:
            consensus['key_interventions'] = clinical_decision.get('immediate_actions', [])
        
        # Calculate confidence
        agreement_count = len(analysis['agreements'])
        total_topics = agreement_count + len(analysis['disagreements'])
        
        if total_topics > 0:
            agreement_ratio = agreement_count / total_topics
            if agreement_ratio > 0.8:
                consensus['confidence_level'] = "HIGH - Strong consensus"
            elif agreement_ratio > 0.5:
                consensus['confidence_level'] = "MODERATE - Partial consensus"
            else:
                consensus['confidence_level'] = "LOW - Significant disagreement"
        
        # Final recommendation
        consensus['final_recommendation'] = self._generate_final_recommendation(consensus)
        
        return consensus
    
    def _generate_final_recommendation(self, consensus: Dict) -> str:
        """
        Generate a clear final recommendation
        """
        rec = f"CONSENSUS RECOMMENDATION: "
        rec += f"{consensus['primary_diagnosis']}. "
        rec += f"{consensus['disposition']}. "
        
        if consensus['key_interventions']:
            rec += f"Immediate actions: {', '.join(consensus['key_interventions'][:2])}. "
        
        if consensus['dissenting_opinions']:
            rec += f"Note: {', '.join(consensus['dissenting_opinions'])}"
        
        return rec
    
    async def _communicate_consensus(self, consensus: Dict):
        """
        Communicate final consensus to all agents
        """
        # Post consensus
        await blackboard.post(
            self.agent_id,
            MessageType.CONSENSUS,
            "FINAL_CONSENSUS",
            consensus,
            Priority.HIGH
        )
        
        print(f"\n[{self.name}] ✅ CONSENSUS REACHED:")
        print(f"  Diagnosis: {consensus['primary_diagnosis']}")
        print(f"  Disposition: {consensus['disposition']}")
        print(f"  Confidence: {consensus['confidence_level']}")
        
        # Post final opinion
        blackboard.post_opinion(
            self.agent_id,
            "final_consensus",
            consensus['final_recommendation'],
            confidence=0.9
        )
    
    async def _create_unified_action_plan(self, consensus: Dict) -> Dict:
        """
        Create a unified action plan based on consensus
        """
        action_plan = {
            'immediate_actions': [],
            'within_1_hour': [],
            'within_4_hours': [],
            'ongoing': [],
            'decision_points': []
        }
        
        # Based on consensus diagnosis and disposition
        if 'sepsis' in consensus['primary_diagnosis'].lower():
            action_plan['immediate_actions'] = [
                "Initiate sepsis protocol",
                "IV access x2",
                "Blood cultures before antibiotics"
            ]
            action_plan['within_1_hour'] = [
                "Start broad-spectrum antibiotics",
                "30mL/kg fluid bolus",
                "Lactate level"
            ]
        
        elif 'pneumonia' in consensus['primary_diagnosis'].lower():
            action_plan['immediate_actions'] = [
                "Supplemental oxygen",
                "IV access",
                "Blood cultures"
            ]
            action_plan['within_1_hour'] = [
                "Start antibiotics",
                "Chest X-ray if not done"
            ]
        
        # Add decision points
        action_plan['decision_points'] = [
            "Reassess in 6 hours - if worsening, escalate care",
            "Check response to antibiotics at 48 hours",
            "Consider discharge when afebrile 24h and improving"
        ]
        
        return action_plan
    
    def _calculate_consensus_strength(self, analysis: Dict) -> float:
        """
        Calculate how strong the consensus is
        """
        agreements = len(analysis['agreements'])
        disagreements = len(analysis['disagreements'])
        
        if agreements + disagreements == 0:
            return 0.5
        
        return agreements / (agreements + disagreements)
    
    async def handle_event(self, topic: str, message: Dict):
        """
        Handle events from other agents
        """
        # Track all decisions
        if topic.endswith('_complete'):
            agent = message.get('agent_id', 'Unknown')
            content = message.get('content', {})
            self.decision_tracking[agent].append({
                'topic': topic,
                'content': content,
                'timestamp': message.get('timestamp')
            })
        
        # React to questions about consensus
        elif topic.startswith("question_") and "consensus" in str(message.get('content', '')).lower():
            response = "I'm working on building consensus. Current status:\n"
            
            # Quick consensus check
            agreements = len([k for k, v in blackboard.consensus_topics.items() if v])
            response += f"- {agreements} topics have reached consensus\n"
            response += f"- {len(blackboard.active_alerts)} critical issues identified\n"
            response += "- Final recommendation coming shortly"
            
            await blackboard.respond_to_question(self.agent_id, topic, response)

# Create the intelligent agent
consensus_builder = IntelligentConsensusBuilder()
