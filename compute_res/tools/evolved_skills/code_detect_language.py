"""Skill: code_detect_language
Category: code-analysis
Description: Detect the programming language of a code snippet.
"""

def run(**kwargs):
    code = kwargs.get('code', '')
    patterns = {'python': ['def ', 'import ', 'print(', 'elif '], 'javascript': ['const ', 'let ', '=>', 'console.log'], 'java': ['public class', 'System.out', 'void main'], 'go': ['func ', 'package ', 'fmt.', ':='], 'rust': ['fn ', 'let mut', 'impl '], 'bash': ['#!/bin/bash', 'echo ', 'fi'], 'c': ['#include', 'int main(', 'printf(']}
    scores = {lang: sum(1 for p in pats if p in code) for lang, pats in patterns.items()}
    best = max(scores, key=scores.get)
    return {'detected': best if scores[best] > 0 else 'unknown', 'scores': scores}
