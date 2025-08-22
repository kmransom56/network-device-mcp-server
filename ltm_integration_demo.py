#!/usr/bin/env python3
"""
LTM Integration Demonstration Script
Shows the complete Long-Term Memory system integration with voice interface
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ltm_core import (
    LTMMemorySystem, NetworkEvent, create_network_event,
    PatternRecognitionEngine, create_pattern_engine,
    PredictiveAnalyticsEngine, create_predictive_engine,
    NetworkGraphIntelligence, create_graph_intelligence,
    VoiceLearningEngine, CommandIntent, create_voice_learning_engine
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ltm_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LTMIntegrationDemo:
    """Demonstration of LTM system integration"""
    
    def __init__(self):
        """Initialize the LTM demonstration system"""
        logger.info("🧠 Initializing LTM Integration Demo...")
        
        # Initialize LTM components
        self.ltm_memory = LTMMemorySystem(
            config={
                'pattern_confidence_threshold': 0.6,
                'min_pattern_frequency': 2,
                'max_memory_age_days': 180
            }
        )
        
        self.pattern_engine = create_pattern_engine(self.ltm_memory)
        self.predictive_engine = create_predictive_engine(self.ltm_memory, self.pattern_engine)
        self.graph_intelligence = create_graph_intelligence()
        self.voice_engine = create_voice_learning_engine(self.ltm_memory)
        
        logger.info("✅ LTM Integration Demo initialized successfully")
    
    def run_complete_demo(self):
        """Run the complete LTM integration demonstration"""
        print("\n" + "="*80)
        print("🧠 LTM NETWORK INTELLIGENCE PLATFORM DEMONSTRATION")
        print("Hybrid AI + Voice-Enabled Network Management System")
        print("="*80 + "\n")
        
        # Step 1: Generate sample network events
        print("📊 Step 1: Generating Sample Network Events...")
        self._generate_sample_events()
        
        # Step 2: Demonstrate pattern recognition
        print("\n🔍 Step 2: Advanced Pattern Recognition...")
        self._demonstrate_pattern_recognition()
        
        # Step 3: Show predictive analytics
        print("\n🔮 Step 3: Predictive Analytics...")
        self._demonstrate_predictive_analytics()
        
        # Step 4: Graph intelligence analysis
        print("\n🕸️ Step 4: Network Graph Intelligence...")
        self._demonstrate_graph_intelligence()
        
        # Step 5: Voice learning capabilities
        print("\n🎤 Step 5: Voice Learning Engine...")
        self._demonstrate_voice_learning()
        
        # Step 6: Integration showcase
        print("\n🔗 Step 6: Integrated Intelligence...")
        self._demonstrate_integration()
        
        # Step 7: Memory system statistics
        print("\n📈 Step 7: LTM Memory Statistics...")
        self._show_memory_statistics()
        
        print("\n" + "="*80)
        print("🎉 LTM Integration Demo Complete!")
        print("Your voice-enabled AI network management system is ready!")
        print("="*80 + "\n")
    
    def _generate_sample_events(self):
        """Generate sample network events for demonstration"""
        sample_events = [
            # BWW Security Incidents
            {
                'event_type': 'security_incident',
                'brand': 'BWW',
                'store_id': '155',
                'device_name': 'FortiGate-01',
                'severity': 'high',
                'description': 'SQL injection attempt blocked by WAF',
                'resolution': 'Blocked malicious requests, updated WAF rules',
                'resolution_time': 15,
                'tags': ['sql_injection', 'web_attack', 'blocked']
            },
            {
                'event_type': 'security_incident', 
                'brand': 'BWW',
                'store_id': '234',
                'device_name': 'FortiGate-01',
                'severity': 'critical',
                'description': 'Malware detected on POS system',
                'resolution': 'Isolated system, malware removed, system reimaged',
                'resolution_time': 120,
                'tags': ['malware', 'pos_system', 'contained']
            },
            # Arby's Performance Issues
            {
                'event_type': 'performance_issue',
                'brand': 'ARBYS',
                'store_id': '789',
                'device_name': 'Switch-01',
                'severity': 'medium',
                'description': 'High network latency affecting POS operations',
                'resolution': 'Bandwidth optimization applied',
                'resolution_time': 45,
                'tags': ['latency', 'pos_impact', 'resolved']
            },
            # Sonic Configuration Changes
            {
                'event_type': 'configuration_change',
                'brand': 'SONIC',
                'store_id': '456',
                'device_name': 'FortiGate-01',
                'severity': 'low',
                'description': 'Updated firewall rules for new application',
                'resolution': 'Configuration applied successfully',
                'resolution_time': 10,
                'tags': ['firewall_rules', 'application_update', 'success']
            },
            # More BWW incidents for pattern detection
            {
                'event_type': 'security_incident',
                'brand': 'BWW', 
                'store_id': '155',
                'device_name': 'FortiGate-01',
                'severity': 'high',
                'description': 'Brute force attack on management interface',
                'resolution': 'Account locked, IP blocked, MFA enabled',
                'resolution_time': 30,
                'tags': ['brute_force', 'management_interface', 'blocked']
            }
        ]
        
        stored_count = 0
        for event_data in sample_events:
            event = create_network_event(**event_data)
            if self.ltm_memory.record_event(event):
                stored_count += 1
        
        print(f"   ✅ Generated and stored {stored_count} sample network events")
    
    def _demonstrate_pattern_recognition(self):
        """Demonstrate pattern recognition capabilities"""
        # Analyze patterns in stored events
        patterns = self.pattern_engine.analyze_patterns(time_window_hours=24)
        
        print(f"   🔍 Detected {len(patterns)} patterns:")
        
        for i, pattern in enumerate(patterns[:3], 1):  # Show top 3
            print(f"\n   📋 Pattern {i}: {pattern.description}")
            print(f"      • Type: {pattern.pattern_type.value}")
            print(f"      • Confidence: {pattern.confidence:.2f}")
            print(f"      • Affected: {', '.join(pattern.affected_entities)}")
            print(f"      • Recommendations: {len(pattern.recommendations)} actions")
            
            if pattern.recommendations:
                print(f"        - {pattern.recommendations[0]}")
    
    def _demonstrate_predictive_analytics(self):
        """Demonstrate predictive analytics capabilities"""
        # Generate predictions
        predictions = self.predictive_engine.generate_predictions(
            time_horizon_days=7
        )
        
        print(f"   🔮 Generated {len(predictions)} predictions for next 7 days:")
        
        for i, prediction in enumerate(predictions[:3], 1):  # Show top 3
            print(f"\n   📊 Prediction {i}: {prediction.description}")
            print(f"      • Type: {prediction.prediction_type.value}")
            print(f"      • Confidence: {prediction.confidence:.2f}")
            print(f"      • Probability: {prediction.probability:.2f}")
            print(f"      • Severity: {prediction.severity}")
            print(f"      • Entity: {prediction.affected_entity}")
            print(f"      • Business Impact: {prediction.business_impact}")
            
            if prediction.reasoning:
                print(f"      • Reasoning: {prediction.reasoning[0]}")
    
    def _demonstrate_graph_intelligence(self):
        """Demonstrate graph intelligence capabilities"""
        # Analyze attack paths
        attack_paths = self.graph_intelligence.analyze_attack_paths()
        
        print(f"   🕸️ Analyzed {len(attack_paths)} potential attack paths:")
        
        for i, path in enumerate(attack_paths[:2], 1):  # Show top 2
            print(f"\n   🎯 Attack Path {i}:")
            print(f"      • From: {path.source_node}")
            print(f"      • To: {path.target_node}")
            print(f"      • Risk Score: {path.risk_score:.2f}")
            print(f"      • Path Length: {path.shortest_path_length} hops")
            print(f"      • Summary: {path.analysis_summary}")
        
        # Demonstrate impact propagation
        print(f"\n   📡 Impact Propagation Analysis:")
        test_entity = "device_BWW_155_FortiGate-01"
        propagation = self.graph_intelligence.analyze_impact_propagation(test_entity)
        
        if propagation:
            print(f"      • Source: {propagation['source_entity']}")
            print(f"      • Total Affected: {propagation['total_affected_entities']}")
            print(f"      • Stores Affected: {propagation['stores_affected']}")
            print(f"      • High Risk Entities: {propagation['high_risk_entities']}")
            print(f"      • Max Distance: {propagation['max_propagation_distance']} hops")
    
    def _demonstrate_voice_learning(self):
        """Demonstrate voice learning capabilities"""
        # Test voice commands
        test_commands = [
            "investigate BWW store 155",
            "check security status for Arby's store 789", 
            "predict security issues for Sonic next week",
            "show patterns in recent security events",
            "analyze correlation between BWW incidents"
        ]
        
        print(f"   🎤 Processing {len(test_commands)} voice commands:")
        
        for i, command_text in enumerate(test_commands, 1):
            command = self.voice_engine.process_voice_command(command_text)
            
            print(f"\n   🗣️ Command {i}: '{command_text}'")
            print(f"      • Intent: {command.intent.value}")
            print(f"      • Confidence: {command.confidence:.2f}")
            print(f"      • Entities: {command.entities}")
            print(f"      • Parameters: {command.parameters}")
            
            # Simulate successful execution
            execution_result = {
                'success': True,
                'response_time': 0.8,
                'user_feedback': 'positive'
            }
            
            self.voice_engine.learn_from_interaction(command, execution_result)
        
        # Show voice suggestions
        suggestions = self.voice_engine.suggest_voice_commands({'current_section': 'investigation'})
        print(f"\n   💡 Voice Command Suggestions:")
        for suggestion in suggestions[:3]:
            print(f"      • \"{suggestion['command']}\" - {suggestion['description']}")
    
    def _demonstrate_integration(self):
        """Demonstrate integrated intelligence capabilities"""
        print("   🔗 Hybrid Intelligence Integration:")
        
        # 1. Voice command triggers pattern analysis
        voice_command = self.voice_engine.process_voice_command(
            "analyze security patterns for BWW and predict future incidents"
        )
        
        print(f"\n   🎤 Voice Command Processed:")
        print(f"      Intent: {voice_command.intent.value}")
        print(f"      Entities: {voice_command.entities}")
        
        # 2. Pattern engine analyzes events
        if voice_command.entities.get('brand') == 'BWW':
            patterns = self.pattern_engine.analyze_patterns()
            bww_patterns = [p for p in patterns if 'BWW' in str(p.affected_entities)]
            
            print(f"\n   🔍 Pattern Analysis Results:")
            print(f"      Found {len(bww_patterns)} BWW-specific patterns")
            
            # 3. Predictive engine generates forecasts
            predictions = self.predictive_engine.generate_predictions(
                entities=['BWW_155', 'BWW_234'], 
                time_horizon_days=14
            )
            
            print(f"\n   🔮 Predictive Analytics:")
            print(f"      Generated {len(predictions)} predictions for BWW stores")
            
            # 4. Graph intelligence shows relationships
            influence_score = self.graph_intelligence.get_entity_influence_score("brand_BWW")
            print(f"\n   🕸️ Graph Intelligence:")
            print(f"      BWW brand influence score: {influence_score:.2f}")
        
        print("\n   ✨ Integration Benefits:")
        print("      • Voice commands trigger intelligent analysis")
        print("      • Historical learning improves predictions") 
        print("      • Graph relationships show impact propagation")
        print("      • Pattern recognition identifies emerging threats")
        print("      • All systems learn and adapt continuously")
    
    def _show_memory_statistics(self):
        """Show LTM memory system statistics"""
        stats = self.ltm_memory.get_memory_stats()
        
        print("   📊 LTM Memory System Statistics:")
        print(f"      • Total Events: {stats.get('total_events', 0)}")
        print(f"      • Total Patterns: {stats.get('total_patterns', 0)}")
        print(f"      • Voice Interactions: {stats.get('total_voice_interactions', 0)}")
        print(f"      • Average Pattern Confidence: {stats.get('avg_pattern_confidence', 0):.2f}")
        print(f"      • Voice Success Rate: {stats.get('voice_success_rate', 0):.2%}")
        
        events_by_type = stats.get('events_by_type', {})
        if events_by_type:
            print(f"      • Events by Type:")
            for event_type, count in events_by_type.items():
                print(f"        - {event_type}: {count}")
        
        # Show database file size
        db_path = self.ltm_memory.db_path
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            print(f"      • Database Size: {db_size:.1f} KB")
    
    def interactive_demo(self):
        """Run interactive demonstration"""
        print("\n🎤 Interactive Voice Command Demo")
        print("Enter voice commands to test the system (or 'quit' to exit):")
        print("Examples:")
        print("  - investigate BWW store 155")
        print("  - predict security issues for Sonic")
        print("  - show patterns in recent events")
        
        while True:
            try:
                command_text = input("\n🗣️  Voice Command: ").strip()
                
                if command_text.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not command_text:
                    continue
                
                # Process the command
                print("   Processing...")
                command = self.voice_engine.process_voice_command(command_text)
                
                print(f"   ✅ Intent: {command.intent.value}")
                print(f"   📋 Entities: {command.entities}")
                print(f"   ⚙️ Parameters: {command.parameters}")
                print(f"   🎯 Confidence: {command.confidence:.2f}")
                
                # Show what the system would do
                if command.intent == CommandIntent.INVESTIGATION:
                    brand = command.entities.get('brand', 'unknown')
                    store_id = command.entities.get('store_id', 'unknown')
                    print(f"   🔍 Would investigate {brand} store {store_id}")
                    
                elif command.intent == CommandIntent.PREDICTION_REQUEST:
                    brand = command.entities.get('brand', 'all brands')
                    print(f"   🔮 Would generate predictions for {brand}")
                    
                elif command.intent == CommandIntent.PATTERN_ANALYSIS:
                    print(f"   🔍 Would analyze patterns in network events")
                
                # Simulate learning from the interaction
                execution_result = {'success': True, 'response_time': 0.5}
                self.voice_engine.learn_from_interaction(command, execution_result)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n👋 Interactive demo ended.")

def main():
    """Main demonstration function"""
    try:
        demo = LTMIntegrationDemo()
        
        # Run the complete demo
        demo.run_complete_demo()
        
        # Ask if user wants interactive demo
        response = input("\n🎤 Would you like to try the interactive voice demo? (y/n): ")
        if response.lower().startswith('y'):
            demo.interactive_demo()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())