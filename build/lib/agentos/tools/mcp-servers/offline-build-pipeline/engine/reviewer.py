"""
Phase 4: Reviewer module
Interfaces with native-ai-engine-bridge to request local AI review.
"""
import json
import urllib.request
import urllib.error

# Assuming the bridge might be available via HTTP if exposed, or we can just 
# formulate the prompt for the orchestrator to pass to the bridge.

def format_review_prompt(diff: str, validation_report: dict) -> str:
    """
    Format a highly compact prompt for the local phi-3-mini model.
    """
    prompt = f"""
[CODE REVIEW TASK]
Validation Status: {json.dumps(validation_report)}

Diff:
{diff}

Does this code contain logic errors or security flaws? 
Reply strictly with 'APPROVE' or 'REFINE: <reason>'.
"""
    return prompt.strip()

def review_code(diff: str, validation_report: dict) -> dict:
    """
    Mock implementation that just approves if validation passed.
    In real usage, this would call the execute_prompt tool of native-ai-engine-bridge.
    """
    prompt = format_review_prompt(diff, validation_report)
    
    if validation_report.get("valid", False):
        return {"decision": "APPROVE", "prompt_used": prompt}
    else:
        return {"decision": "REFINE", "reason": "Failed offline validation", "prompt_used": prompt}
