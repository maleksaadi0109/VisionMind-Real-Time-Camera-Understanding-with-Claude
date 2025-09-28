import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class SuspicionLevel(Enum):
    NORMAL = "normal"
    UNUSUAL = "unusual"
    SUSPICIOUS = "suspicious"

@dataclass
class VisionAnalysis:
    summary: str
    description: str
    context: str
    suspicion_level: SuspicionLevel
    highlights: List[str]

class VisionInterpreter:
    """Interprets camera vision model outputs and provides natural language analysis."""
    
    def __init__(self):
        # Common object relationships and contexts
        self.common_combinations = {
            ("person", "dog"): "walking a dog",
            ("person", "bicycle"): "cycling or with a bicycle",
            ("person", "car"): "near or entering a vehicle",
            ("person", "bag"): "carrying belongings",
            ("person", "phone"): "using a mobile device"
        }
        
        # Suspicious patterns
        self.suspicious_patterns = {
            ("person", "window", "night"): "possible intrusion attempt",
            ("person", "running", "bag"): "potential theft in progress",
            ("person", "mask", "weapon"): "armed individual",
            ("fire", "smoke"): "fire hazard detected"
        }
    
    def analyze(self, vision_input: Dict[str, Any]) -> VisionAnalysis:
        """
        Analyze vision model output and return structured analysis.
        
        Args:
            vision_input: Dictionary containing detected_objects, scene, and action
            
        Returns:
            VisionAnalysis object with complete scene interpretation
        """
        objects = vision_input.get("detected_objects", [])
        scene = vision_input.get("scene", "unknown")
        action = vision_input.get("action", "stationary")
        time_of_day = vision_input.get("time", "day")
        
        # Generate summary
        summary = self._generate_summary(objects, scene, action)
        
        # Create detailed description
        description = self._create_description(objects, scene, action)
        
        # Provide context
        context = self._analyze_context(objects, scene, action)
        
        # Check for suspicious activity
        suspicion_level, highlights = self._check_suspicious_activity(
            objects, scene, action, time_of_day
        )
        
        return VisionAnalysis(
            summary=summary,
            description=description,
            context=context,
            suspicion_level=suspicion_level,
            highlights=highlights
        )
    
    def _generate_summary(self, objects: List[str], scene: str, action: str) -> str:
        """Generate a brief summary of the scene."""
        if not objects:
            return f"Empty {scene} scene detected."
        
        main_subject = objects[0] if objects else "object"
        return f"A {main_subject} {action} in a {scene} setting."
    
    def _create_description(self, objects: List[str], scene: str, action: str) -> str:
        """Create a natural language description of the scene."""
        if not objects:
            return f"The camera shows an empty {scene} with no significant activity."
        
        # Build description based on detected elements
        desc_parts = []
        
        if "person" in objects:
            person_desc = f"A person is {action}"
            
            # Check for common combinations
            for obj in objects:
                if obj != "person":
                    for combo, activity in self.common_combinations.items():
                        if "person" in combo and obj in combo:
                            person_desc = f"A person is {activity}"
                            break
            
            desc_parts.append(person_desc)
        
        # Add other objects
        other_objects = [obj for obj in objects if obj != "person"]
        if other_objects:
            if len(other_objects) == 1:
                desc_parts.append(f"A {other_objects[0]} is also visible")
            else:
                desc_parts.append(f"Also visible: {', '.join(other_objects)}")
        
        description = ". ".join(desc_parts) + f" on a {scene}."
        return description
    
    def _analyze_context(self, objects: List[str], scene: str, action: str) -> str:
        """Provide contextual analysis of the scene."""
        contexts = []
        
        # Analyze scene type
        if scene in ["street", "sidewalk", "road"]:
            contexts.append("This appears to be a public urban area")
        elif scene in ["park", "garden", "field"]:
            contexts.append("This is an outdoor recreational area")
        elif scene in ["home", "house", "apartment"]:
            contexts.append("This is a residential setting")
        elif scene in ["store", "shop", "mall"]:
            contexts.append("This is a commercial environment")
        
        # Analyze activity level
        if action in ["running", "jogging"]:
            contexts.append("showing active movement")
        elif action in ["sitting", "standing", "waiting"]:
            contexts.append("with minimal activity")
        elif action in ["walking", "strolling"]:
            contexts.append("with normal pedestrian movement")
        
        # Analyze object combinations
        if "person" in objects and "dog" in objects:
            contexts.append("likely a pet owner during routine exercise")
        elif "person" in objects and "bicycle" in objects:
            contexts.append("suggesting eco-friendly transportation or recreation")
        
        return ". ".join(contexts) + "." if contexts else "Standard scene with typical elements."
    
    def _check_suspicious_activity(
        self, objects: List[str], scene: str, action: str, time: str
    ) -> tuple[SuspicionLevel, List[str]]:
        """Check for suspicious or unusual activity patterns."""
        highlights = []
        suspicion_level = SuspicionLevel.NORMAL
        
        # Check for suspicious patterns
        for pattern, warning in self.suspicious_patterns.items():
            if all(item in objects + [action, time] for item in pattern):
                highlights.append(f"⚠️ {warning}")
                suspicion_level = SuspicionLevel.SUSPICIOUS
        
        # Check for unusual combinations
        unusual_checks = [
            (["person", "running"] and time == "night", "Person running at night"),
            (["person"] and scene == "restricted", "Unauthorized person in restricted area"),
            (action == "climbing" and scene != "gym", "Unusual climbing activity"),
            (["crowd", "running"], "Multiple people running - possible emergency")
        ]
        
        for condition, message in unusual_checks:
            if condition:
                highlights.append(f"⚠️ {message}")
                if suspicion_level == SuspicionLevel.NORMAL:
                    suspicion_level = SuspicionLevel.UNUSUAL
        
        return suspicion_level, highlights
    
    def format_output(self, analysis: VisionAnalysis) -> str:
        """Format the analysis into a readable output."""
        output = []
        output.append("=" * 50)
        output.append("VISION ANALYSIS REPORT")
        output.append("=" * 50)
        output.append(f"\n📍 SUMMARY: {analysis.summary}")
        output.append(f"\n📝 DESCRIPTION: {analysis.description}")
        output.append(f"\n🔍 CONTEXT: {analysis.context}")
        output.append(f"\n🚨 SUSPICION LEVEL: {analysis.suspicion_level.value.upper()}")
        
        if analysis.highlights:
            output.append("\n⚠️ ALERTS:")
            for highlight in analysis.highlights:
                output.append(f"  - {highlight}")
        else:
            output.append("\n✅ No unusual activity detected")
        
        output.append("\n" + "=" * 50)
        return "\n".join(output)


# Example usage
def main():
    # Initialize the interpreter
    interpreter = VisionInterpreter()
    
    # Example vision model outputs to test
    test_cases = [
        {
            "detected_objects": ["person", "dog", "bicycle"],
            "scene": "street",
            "action": "walking"
        },
        {
            "detected_objects": ["person", "bag", "running"],
            "scene": "store",
            "action": "running",
            "time": "night"
        },
        {
            "detected_objects": ["car", "person", "smoke"],
            "scene": "parking lot",
            "action": "standing"
        },
        {
            "detected_objects": ["person", "ladder", "window"],
            "scene": "house",
            "action": "climbing",
            "time": "night"
        }
    ]
    
    # Process each test case
    for i, vision_input in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {json.dumps(vision_input, indent=2)}")
        
        # Analyze the input
        analysis = interpreter.analyze(vision_input)
        
        # Display formatted output
        print(interpreter.format_output(analysis))
        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()