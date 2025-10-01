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
            # YHWH (Tetragrammaton) - appears 6,500+ times in Hebrew Bible
            # English translations typically use "LORD" (all caps) to represent YHWH
            {
                'english_forms': [r'\bLORD\b'],
                'hebrew_original': 'YHWH',
                'scholarly_pronunciation': 'Yahweh',
                'replacement': 'YHWH'  # Use the actual Hebrew letters in English
            },
            
            # YHWH + Elohim combinations (compound names)
            {
                'english_forms': [
                    r'\bLORD\s+God\b',
                    r'\bLord\s+GOD\b', 
                    r'\bthe\s+LORD\s+God\b',
                    r'\bLORD\s+thy\s+God\b',
                    r'\bLORD\s+your\s+God\b',
                    r'\bLORD\s+our\s+God\b'
                ],
                'hebrew_original': 'YHWH Elohim',
                'replacement': 'YHWH Elohim'
            },
            
            # Adonai (my Lord) - reverence substitute for YHWH since 2nd century BCE
            # Some English translations use "Lord" (title case) for Adonai
            {
                'english_forms': [r'\bLord\b(?!\s+(?:God|GOD))'],
                'hebrew_original': 'Adonai', 
                'scholarly_note': 'Reverence substitute for YHWH',
                'replacement': 'YHUH'  # Alternative rendering respecting the substitute tradition
            },
            
            # Elohim (God/Gods) - plural of majesty, remains as is
            # This is correctly translated as "God" and should not be changed
            {
                'english_forms': [r'\bGod\b'],
                'hebrew_original': 'Elohim',
                'replacement': 'God',  # Keep as God - this is correct for Elohim
                'preserve': True  # Flag to indicate this should remain unchanged
            },
            
            # El (God/Mighty One) - singular form
            {
                'english_forms': [r'\bGOD\b(?!\s+(?:of|Lord))'],
                'hebrew_original': 'El',
                'replacement': 'El'
            },
            
            # Shortened forms in names and expressions
            {
                'english_forms': [r'\b(Hallelu)jah\b', r'\b([A-Z][a-z]*i)ah\b'],
                'hebrew_original': 'Yah (shortened YHWH)',
                'replacement': r'\1YAH'  # Preserve the Yah ending in names like Elijah -> EliYAH
            }
        ]
    
    def apply_replacements(self, text: str, preserve_elohim: bool = True) -> Dict[str, any]:
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