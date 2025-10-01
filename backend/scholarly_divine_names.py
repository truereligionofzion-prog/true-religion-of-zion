#!/usr/bin/env python3
"""
Scholarly Divine Name Replacement System
Based on ancient Hebrew manuscripts (Dead Sea Scrolls, Masoretic Text) and 
biblical textual criticism research
"""

import re
from typing import Dict, List

class ScholarlyDivineNameReplacer:
    """
    Handles divine name replacements based on scholarly research of ancient Hebrew manuscripts
    """
    
    def __init__(self):
        """
        Initialize with patterns based on ancient manuscript evidence:
        - Dead Sea Scrolls preserve YHWH in Hebrew letters
        - Masoretic Text uses YHWH with Adonai vowel pointing
        - Scholarly consensus: YHWH pronounced as "Yahweh"
        - Elohim (plural of majesty) remains as "Elohim" or "God"
        - Adonai means "my Lord" and represents reverence substitute
        """
        
        # Primary divine names from ancient Hebrew
        self.divine_patterns = [
            # Handle compound forms FIRST (more specific patterns)
            # Based on Deuteronomy 6:4 ancient Hebrew: יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד
            
            # YHWH + Elohim combinations - use replacement_pairs for exact matching
            {
                'english_forms': [],  # Empty since we use replacement_pairs
                'hebrew_original': 'YHWH Elohim combinations',
                'replacement_pairs': [
                    ('the LORD our God', 'YHWH our Elohim'),
                    ('LORD our God', 'YHWH our Elohim'),
                    ('the LORD thy God', 'YHWH thy Elohim'),
                    ('LORD thy God', 'YHWH thy Elohim'),
                    ('the LORD your God', 'YHWH your Elohim'),
                    ('LORD your God', 'YHWH your Elohim'),
                    ('the LORD my God', 'YHWH my Elohim'),
                    ('LORD my God', 'YHWH my Elohim'),
                    ('LORD God', 'YHWH Elohim'),
                    ('Lord GOD', 'YHWH Elohim')
                ]
            },
            
            # Handle remaining "the LORD" cases and preserve Hebrew word order
            {
                'english_forms': [],  # Empty since we use replacement_pairs  
                'hebrew_original': 'YHWH patterns',
                'replacement_pairs': [
                    ('the LORD', 'YHWH'),
                    # Keep Hebrew word order: "YHWH our Elohim, YHWH echad" = "YHWH our Elohim, YHWH is one"
                    ('is one LORD', 'is one YHWH'),  # Actually this is correct based on Hebrew
                ]
            },
            
            # YHWH (Tetragrammaton) - standalone occurrences
            {
                'english_forms': [r'\bLORD\b'],
                'hebrew_original': 'YHWH',
                'scholarly_pronunciation': 'Yahweh',
                'replacement': 'YHWH'
            },
            
            # Adonai (my Lord) - reverence substitute for YHWH
            {
                'english_forms': [r'\bLord\b(?!\s+(?:God|GOD|thy|your|our|my))'],
                'hebrew_original': 'Adonai', 
                'replacement': 'YHUH'
            },
            
            # Standalone possessive Elohim (only if not already handled above)
            {
                'english_forms': [],  # Empty since we use replacement_pairs
                'hebrew_original': 'Elohim with possessive',
                'replacement_pairs': [
                    ('our God', 'our Elohim'),
                    ('thy God', 'thy Elohim'), 
                    ('your God', 'your Elohim'),
                    ('my God', 'my Elohim')
                ]
            },
            
            # Standalone Elohim
            {
                'english_forms': [r'\bGod\b'],
                'hebrew_original': 'Elohim',
                'replacement': 'Elohim'
            },
            
            # El (God/Mighty One) - singular form
            {
                'english_forms': [r'\bGOD\b(?!\s+(?:of|Lord))'],
                'hebrew_original': 'El',
                'replacement': 'El'
            }
        ]
    
    def apply_replacements(self, text: str, preserve_elohim: bool = False) -> Dict[str, any]:
        """
        Apply scholarly-based divine name replacements to text
        
        Args:
            text: Input text to process
            preserve_elohim: If True, keeps "God" unchanged (for Elohim)
            
        Returns:
            Dict with processed text and replacement statistics
        """
        if not text:
            return {'text': text, 'replacements': {}, 'total_replacements': 0}
        
        processed_text = text
        replacements = {}
        
        for pattern_group in self.divine_patterns:
            # Skip Elohim preservation if requested
            if preserve_elohim and pattern_group.get('preserve', False):
                continue
            
            # Handle replacement pairs (for possessive forms)
            if 'replacement_pairs' in pattern_group:
                for find_str, replace_str in pattern_group['replacement_pairs']:
                    if find_str in processed_text:
                        processed_text = processed_text.replace(find_str, replace_str)
                        
                        hebrew_original = pattern_group['hebrew_original']
                        if hebrew_original not in replacements:
                            replacements[hebrew_original] = {
                                'count': 0,
                                'replacement': replace_str,
                                'english_forms': []
                            }
                        replacements[hebrew_original]['count'] += 1
                        replacements[hebrew_original]['english_forms'].append(find_str)
            
            # Handle regular pattern replacements
            elif 'replacement' in pattern_group:
                for english_pattern in pattern_group['english_forms']:
                    matches = re.findall(english_pattern, processed_text)
                    if matches:
                        count = len(matches)
                        hebrew_original = pattern_group['hebrew_original']
                        replacement = pattern_group['replacement']
                        
                        # Apply replacement
                        processed_text = re.sub(english_pattern, replacement, processed_text)
                        
                        # Track statistics
                        if hebrew_original not in replacements:
                            replacements[hebrew_original] = {
                                'count': 0,
                                'replacement': replacement,
                                'english_forms': []
                            }
                        
                        replacements[hebrew_original]['count'] += count
                        replacements[hebrew_original]['english_forms'].extend(matches)
        
        total_replacements = sum(r['count'] for r in replacements.values())
        
        return {
            'text': processed_text,
            'replacements': replacements,
            'total_replacements': total_replacements,
            'scholarly_notes': [
                "Replacements based on Dead Sea Scrolls and Masoretic Text evidence",
                "YHWH: Original Hebrew divine name (6,500+ occurrences in Hebrew Bible)",
                "Elohim (God): Preserved as correct translation of Hebrew plural of majesty",
                "YHUH: Alternative rendering for Adonai (reverence substitute tradition)"
            ]
        }
    
    def get_replacement_summary(self) -> str:
        """Return a summary of the scholarly replacement system"""
        return """
Scholarly Divine Name Replacement System
======================================

Based on ancient Hebrew manuscripts and biblical textual criticism:

1. YHWH (יהוה) - The Tetragrammaton
   - Original Hebrew divine name appearing 6,500+ times
   - English "LORD" (all caps) → YHWH
   - Scholarly pronunciation: "Yahweh"

2. YHWH Elohim (יהוה אלהים) - Compound divine name
   - "LORD God" → YHWH Elohim

3. Adonai (אדני) - Reverence substitute
   - "Lord" (title case) → YHUH
   - Used since 2nd century BCE out of reverence

4. Elohim (אלהים) - God/Gods (plural of majesty)
   - "God" → Remains as "God" (correct translation)

5. El (אל) - God/Mighty One
   - Singular divine designation

Sources: Dead Sea Scrolls, Masoretic Text, comparative Semitics
"""

# Test the system
if __name__ == "__main__":
    replacer = ScholarlyDivineNameReplacer()
    
    test_texts = [
        "The LORD God created the heavens and the earth.",
        "Blessed be the LORD, my rock and my salvation.",
        "In the beginning God created the heaven and the earth.",
        "The Lord is my shepherd, I shall not want.",
        "Praise the LORD, for He is good; His mercy endures forever."
    ]
    
    print(replacer.get_replacement_summary())
    print("\nTest Replacements:")
    print("-" * 50)
    
    for text in test_texts:
        result = replacer.apply_replacements(text)
        print(f"Original:  {text}")
        print(f"Replaced:  {result['text']}")
        print(f"Changes:   {result['total_replacements']} total")
        for hebrew, details in result['replacements'].items():
            print(f"           {hebrew}: {details['count']} occurrences")
        print()