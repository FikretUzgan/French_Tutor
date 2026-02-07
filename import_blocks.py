"""
Compile-time BLOCK Importer Script
Parses all BLOCK_*.md files and populates the database with lessons
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import db


class BlockParser:
    """Parse BLOCK_*.md files and extract lesson data."""
    
    def __init__(self, block_path: Path):
        self.block_path = block_path
        self.content = block_path.read_text(encoding='utf-8')
        self.lessons = []
        self.block_num = self._extract_block_number()
        self.level = self._extract_level()
        
    def _extract_block_number(self) -> int:
        """Extract block number from filename (e.g., 'BLOCK_1' -> 1)"""
        match = re.search(r'BLOCK_(\d+)', self.block_path.name)
        return int(match.group(1)) if match else 0
    
    def _extract_level(self) -> str:
        """Extract level from first line (e.g., 'A1.1', 'A2.1', 'B2.2')"""
        match = re.search(r'\*\*Level:\*\*\s*([\w.]+)', self.content)
        return match.group(1) if match else ""
    
    def parse(self) -> List[Dict]:
        """Parse the entire BLOCK file and return list of lessons."""
        # Split by weeks
        week_pattern = r'## WEEK (\d+):\s*(.+?)\n\n\*\*Theme:\*\*\s*(.+?)\n'
        weeks = re.finditer(week_pattern, self.content)
        
        for week_match in weeks:
            week_num = int(week_match.group(1))
            week_title = week_match.group(2)
            theme = week_match.group(3)
            
            # Find the content for this week (from current week to next week or end)
            week_start = week_match.end()
            next_week = re.search(r'## WEEK \d+:', self.content[week_start:])
            week_end = week_start + next_week.start() if next_week else len(self.content)
            week_content = self.content[week_start:week_end]
            
            # Extract daily lessons
            self._extract_daily_lessons(
                week_num=week_num,
                theme=theme,
                week_content=week_content
            )
        
        return self.lessons
    
    def _extract_daily_lessons(self, week_num: int, theme: str, week_content: str) -> None:
        """Extract individual daily lessons from week content."""
        # Skip Saturday/Sunday sessions, focus on Mon-Fri
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for day_num, day_name in enumerate(days, 1):
            day_pattern = rf'### \*\*{day_name}:.+?(?=###|$)'
            day_match = re.search(day_pattern, week_content, re.DOTALL)
            
            if not day_match:
                continue
            
            day_content = day_match.group(0)
            day_title = self._extract_day_title(day_content)
            
            # Extract sections
            grammar = self._extract_section(day_content, 'Grammar', day_content.find('**Grammar'))
            vocabulary = self._extract_vocabulary(day_content)
            speaking = self._extract_section(day_content, 'Speaking', day_content.find('**Speaking'))
            quiz = self._extract_quiz(day_content)
            homework = self._extract_section(day_content, 'Homework', day_content.find('**Homework'))
            
            # Create lesson ID
            lesson_id = f"block{self.block_num}_w{week_num}_d{day_num}_{day_name.lower()}"
            
            lesson = {
                "lesson_id": lesson_id,
                "level": self.level,
                "block": self.block_num,
                "week": week_num,
                "day": day_num,
                "day_name": day_name,
                "theme": theme,
                "day_title": day_title,
                "grammar": grammar,
                "vocabulary": vocabulary,
                "speaking": speaking,
                "quiz": quiz,
                "homework": homework,
            }
            
            self.lessons.append(lesson)
    
    def _extract_day_title(self, day_content: str) -> str:
        """Extract the day's main title (e.g., 'Être (to be) conjugation')"""
        match = re.search(r'### \*\*\w+:\s*(.+?)\*\*', day_content)
        return match.group(1) if match else ""
    
    def _extract_section(self, content: str, section_name: str, start_pos: int) -> Dict:
        """Extract a section (Grammar, Speaking, etc.) from content."""
        if start_pos == -1:
            return {}
        
        # Find the section block
        section_pattern = rf'\*\*{section_name}\s*\(\d+min\):\*\*(.+?)(?=\*\*\w+\s*\(\d+min\):|\Z)'
        match = re.search(section_pattern, content[start_pos:], re.DOTALL)
        
        if not match:
            return {}
        
        section_content = match.group(1).strip()
        return {"content": section_content, "raw": section_content}
    
    def _extract_vocabulary(self, day_content: str) -> List[str]:
        """Extract vocabulary list from day content."""
        vocab_pattern = r'\*\*Vocabulary\s*\(\d+min\):\*\*(.+?)(?=\*\*\w+\s*\(\d+min\):|\Z)'
        match = re.search(vocab_pattern, day_content, re.DOTALL)
        
        if not match:
            return []
        
        vocab_section = match.group(1)
        # Extract numbered items: 1. **Word** [pronunciation] - meaning
        word_pattern = r'\d+\.\s*\*\*(.+?)\*\*(?:\s*\[[^\]]+\])?\s*-\s*(.+?)(?:\n|$)'
        words = re.findall(word_pattern, vocab_section)
        
        vocab_list = []
        for word, meaning in words:
            vocab_list.append(f"{word} ({meaning.strip()})")
        
        return vocab_list
    
    def _extract_quiz(self, day_content: str) -> List[str]:
        """Extract quiz questions from day content."""
        quiz_pattern = r'\*\*Mini Quiz\s*\(\d+min\):\*\*(.+?)(?=\*\*\w+\s*\([^)]*\):|$)'
        match = re.search(quiz_pattern, day_content, re.DOTALL)
        
        if not match:
            return []
        
        quiz_section = match.group(1)
        # Extract numbered questions
        question_pattern = r'\d+\.\s*(.+?)(?=\n\d+\.|$)'
        questions = re.findall(question_pattern, quiz_section, re.DOTALL)
        
        return [q.strip() for q in questions]


class BlockImporter:
    """Import all BLOCK files into the database."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.blocks = []
        self.lessons = []
    
    def load_all_blocks(self) -> None:
        """Discover and load all BLOCK_*.md files."""
        block_files = sorted(self.project_root.glob("BLOCK_*.md"))
        
        for block_file in block_files:
            print(f"[*] Parsing {block_file.name}...")
            parser = BlockParser(block_file)
            lessons = parser.parse()
            self.lessons.extend(lessons)
            self.blocks.append({
                "file": block_file.name,
                "block_num": parser.block_num,
                "level": parser.level,
                "lesson_count": len(lessons)
            })
    
    def populate_database(self) -> None:
        """Save parsed lessons to database."""
        db.init_db()
        
        for lesson in self.lessons:
            # Convert grammar/vocabulary/quiz to JSON strings
            grammar_json = json.dumps(lesson.get("grammar", {}), ensure_ascii=False)
            vocabulary_json = json.dumps(lesson.get("vocabulary", []), ensure_ascii=False)
            speaking_json = json.dumps(lesson.get("speaking", {}), ensure_ascii=False)
            quiz_json = json.dumps(lesson.get("quiz", []), ensure_ascii=False)
            homework_text = lesson.get("homework", {}).get("content", "")
            
            db.save_lesson(
                lesson_id=lesson["lesson_id"],
                level=lesson["level"],
                theme=lesson["theme"],
                week_number=lesson["week"],
                grammar_explanation=grammar_json,
                vocabulary=vocabulary_json,
                speaking_prompt=speaking_json,
                homework_prompt=homework_text,
                quiz_questions=quiz_json
            )
            
            # Initialize progress tracking
            db.init_lesson_progress(lesson["lesson_id"])
        
        # Mark last block for future flexibility
        self._mark_last_block_flexible()
        
        print(f"\n[OK] Imported {len(self.lessons)} lessons from {len(self.blocks)} blocks")
    
    def _mark_last_block_flexible(self) -> None:
        """Mark Block 9 as the final block with notes for future flexibility."""
        # Add metadata to track that BLOCK_9 is the final block
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Create or check for metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS curriculum_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute(
            "INSERT OR REPLACE INTO curriculum_metadata (key, value) VALUES (?, ?)",
            ("last_block_number", "9")
        )
        
        cursor.execute(
            "INSERT OR REPLACE INTO curriculum_metadata (key, value) VALUES (?, ?)",
            ("curriculum_status", "COMPLETE_A1_A2_B1_B2")
        )
        
        cursor.execute(
            "INSERT OR REPLACE INTO curriculum_metadata (key, value) VALUES (?, ?)",
            ("flexibility_notes", "Block 9 is marked as final. Future enhancements can extend beyond BLOCK_9 without affecting existing progression.")
        )
        
        conn.commit()
        conn.close()
        
        print("[+] Marked BLOCK_9 as final block with flexibility for future extensions")
    
    def report_summary(self) -> None:
        """Print import summary."""
        print("\n" + "="*60)
        print("BLOCK IMPORT SUMMARY")
        print("="*60)
        
        for block_info in self.blocks:
            print(f"\n{block_info['file']}")
            print(f"  Level: {block_info['level']}")
            print(f"  Lessons: {block_info['lesson_count']}")
        
        print(f"\nTotal Lessons Imported: {len(self.lessons)}")
        print("="*60 + "\n")


def import_curriculum():
    """Main entry point for curriculum import."""
    project_root = Path(__file__).parent
    importer = BlockImporter(project_root)
    
    print("\n[*] Starting BLOCK Curriculum Import...\n")
    importer.load_all_blocks()
    importer.populate_database()
    importer.report_summary()
    
    print("[OK] Curriculum import completed successfully!")


if __name__ == "__main__":
    import_curriculum()
