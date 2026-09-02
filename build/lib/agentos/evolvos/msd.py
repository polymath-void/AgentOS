class MissingSkillDetector:
    def __init__(self):
        self.known_skills = set(["db_read", "file_write"])

    def check_intent(self, intent: str) -> bool:
        # Detect if an intent requires a skill that is not currently loaded
        return intent not in self.known_skills
