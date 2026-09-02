import random
import re
from typing import List

class PromptMutator:
    """
    Logic for programmatically evolving and mutating agent prompts.
    """
    
    def __init__(self, mutation_rate: float = 0.1):
        """
        Initialize the PromptMutator with a given mutation rate.
        """
        self.mutation_rate = mutation_rate
        self.synonyms = {
            "think": ["reason", "analyze", "consider", "ponder"],
            "create": ["build", "generate", "develop", "construct"],
            "solve": ["resolve", "address", "fix", "handle"],
            "fast": ["quick", "rapid", "speedy", "swift"],
            "accurate": ["precise", "exact", "correct", "flawless"],
            "important": ["crucial", "essential", "vital", "critical"],
            "always": ["consistently", "constantly", "continually", "unfailingly"],
            "never": ["rarely", "seldom", "infrequently", "hardly"]
        }
        
    def mutate_prompt(self, prompt: str) -> str:
        """
        Mutates a given prompt by replacing specific words with synonyms
        based on the mutation_rate.
        """
        if not prompt:
            return prompt
            
        words = re.findall(r'\b\w+\b|[^\w\s]', prompt)
        mutated_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in self.synonyms and random.random() < self.mutation_rate:
                new_word = random.choice(self.synonyms[word_lower])
                if word.istitle():
                    new_word = new_word.title()
                elif word.isupper():
                    new_word = new_word.upper()
                mutated_words.append(new_word)
            else:
                mutated_words.append(word)
                
        # Simple reconstruction to handle spacing around punctuation roughly
        result = " ".join(mutated_words)
        result = re.sub(r' ([.,!?;:])', r'\1', result)
        return result
        
    def crossover_prompts(self, prompt1: str, prompt2: str) -> str:
        """
        Combines two prompts into a new one by splitting at sentences.
        """
        if not prompt1: return prompt2
        if not prompt2: return prompt1
        
        sentences1 = re.split(r'(?<=[.!?]) +', prompt1)
        sentences2 = re.split(r'(?<=[.!?]) +', prompt2)
        
        if not sentences1 or not sentences2:
            return prompt1
            
        crossover_point1 = random.randint(0, len(sentences1))
        crossover_point2 = random.randint(0, len(sentences2))
        
        child_sentences = sentences1[:crossover_point1] + sentences2[crossover_point2:]
        
        # Ensure we don't return an empty string if both are empty slices
        if not child_sentences:
            child_sentences = sentences1
            
        return " ".join(child_sentences)

    def evolve_population(self, prompts: List[str]) -> List[str]:
        """
        Evolves a population of prompts using mutation and crossover.
        """
        if not prompts:
            return []
            
        new_population = []
        for p in prompts:
            # 50% chance to mutate, 50% chance to crossover
            if random.random() < 0.5:
                new_population.append(self.mutate_prompt(p))
            else:
                partner = random.choice(prompts)
                new_population.append(self.crossover_prompts(p, partner))
                
        return new_population
