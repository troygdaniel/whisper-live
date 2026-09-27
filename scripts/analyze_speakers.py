#!/usr/bin/env python3
"""
Analyze transcript to detect speaker names and create remapped version.

Usage:
    python scripts/analyze_speakers.py transcript.txt
    python scripts/analyze_speakers.py transcript.txt --output named.txt
    python scripts/analyze_speakers.py transcript.txt --interactive
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


class SpeakerAnalyzer:
    """Analyzes transcripts to detect and map speaker names."""

    # Patterns for detecting self-introductions
    SELF_INTRO_PATTERNS = [
        r"(?:I'm|I am|This is|My name is|It's)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+)\s+(?:here|speaking)",
    ]

    # Patterns for detecting when someone is being addressed
    ADDRESSED_PATTERNS = [
        r"(?:Thanks|Thank you|Hey|Hi|Hello)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+),?\s+(?:can you|could you|would you|do you)",
        r"(?:Nice to meet you|Good to see you),?\s+([A-Z][a-z]+)",
    ]

    def __init__(self):
        self.speaker_lines = defaultdict(list)
        self.speaker_names = {}  # {SPEAKER_00: (name, confidence)}
        self.name_evidence = defaultdict(list)  # {SPEAKER_00: [evidence...]}

    def parse_transcript(self, transcript_path):
        """Parse transcript file and extract speaker lines."""
        with open(transcript_path, 'r') as f:
            for line in f:
                # Match format: [00:00:05] [Speaker SPEAKER_00] Text here
                match = re.search(r'\[Speaker (SPEAKER_\d+)\]\s*(.+)', line)
                if match:
                    speaker_id, text = match.groups()
                    self.speaker_lines[speaker_id].append(text.strip())

    def detect_self_introductions(self):
        """Detect names from self-introductions."""
        for speaker_id, lines in self.speaker_lines.items():
            for line in lines:
                for pattern in self.SELF_INTRO_PATTERNS:
                    if match := re.search(pattern, line, re.IGNORECASE):
                        name = match.group(1)
                        # Capitalize properly
                        name = name.capitalize()
                        self.name_evidence[speaker_id].append({
                            'type': 'self_intro',
                            'name': name,
                            'evidence': line,
                            'confidence': 'HIGH'
                        })

    def detect_addressed_names(self):
        """Detect names from being addressed by others."""
        all_lines = []
        for speaker_id in self.speaker_lines:
            for line in self.speaker_lines[speaker_id]:
                all_lines.append((speaker_id, line))

        # Look for names being addressed
        for i, (speaker_id, line) in enumerate(all_lines):
            for pattern in self.ADDRESSED_PATTERNS:
                if match := re.search(pattern, line, re.IGNORECASE):
                    addressed_name = match.group(1).capitalize()

                    # The addressed person is likely the previous speaker
                    if i > 0:
                        prev_speaker_id, _ = all_lines[i-1]
                        self.name_evidence[prev_speaker_id].append({
                            'type': 'addressed',
                            'name': addressed_name,
                            'evidence': f'Called "{addressed_name}" by {speaker_id}',
                            'confidence': 'MEDIUM'
                        })

    def build_name_map(self):
        """Build final speaker name mapping with confidence scores."""
        for speaker_id, evidence_list in self.name_evidence.items():
            if not evidence_list:
                continue

            # Count name occurrences
            name_counts = defaultdict(int)
            highest_confidence = 'LOW'

            for evidence in evidence_list:
                name = evidence['name']
                name_counts[name] += 1

                # Update confidence
                if evidence['confidence'] == 'HIGH':
                    highest_confidence = 'HIGH'
                elif evidence['confidence'] == 'MEDIUM' and highest_confidence != 'HIGH':
                    highest_confidence = 'MEDIUM'

            # Pick most common name
            if name_counts:
                most_common_name = max(name_counts, key=name_counts.get)
                self.speaker_names[speaker_id] = (most_common_name, highest_confidence)

    def analyze(self, transcript_path):
        """Run full analysis pipeline."""
        self.parse_transcript(transcript_path)
        self.detect_self_introductions()
        self.detect_addressed_names()
        self.build_name_map()

    def print_analysis(self):
        """Print analysis results."""
        print("\n" + "=" * 60)
        print("Speaker Analysis Results")
        print("=" * 60)

        if not self.speaker_names:
            print("\n⚠ No speaker names detected.")
            print("\nPossible reasons:")
            print("  - No self-introductions (\"I'm Alice\")")
            print("  - No names mentioned in conversation")
            print("  - Names not capitalized in transcript")
            return

        for speaker_id in sorted(self.speaker_lines.keys()):
            line_count = len(self.speaker_lines[speaker_id])
            print(f"\n{speaker_id} ({line_count} lines)")

            if speaker_id in self.speaker_names:
                name, confidence = self.speaker_names[speaker_id]
                print(f"  → Name: {name} (confidence: {confidence})")

                # Show evidence
                if speaker_id in self.name_evidence:
                    print("  Evidence:")
                    for ev in self.name_evidence[speaker_id][:3]:  # Show max 3
                        print(f"    - {ev['type']}: \"{ev['evidence']}\"")
            else:
                print("  → Name: Unknown")
                print("  Evidence: None found")

        print("\n" + "=" * 60)

    def remap_transcript(self, input_path, output_path=None):
        """Create remapped transcript with speaker names."""
        if output_path is None:
            output_path = Path(input_path).stem + "_named.txt"

        with open(input_path, 'r') as fin, open(output_path, 'w') as fout:
            for line in fin:
                new_line = line

                # Replace speaker IDs with names
                for speaker_id, (name, _) in self.speaker_names.items():
                    # Match [Speaker SPEAKER_00] and replace with [Name]
                    new_line = re.sub(
                        rf'\[Speaker {speaker_id}\]',
                        f'[{name}]',
                        new_line
                    )

                fout.write(new_line)

        print(f"\n✓ Remapped transcript saved to: {output_path}")
        return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_speakers.py <transcript_file>")
        print("       python scripts/analyze_speakers.py <transcript_file> --output <output_file>")
        sys.exit(1)

    transcript_path = sys.argv[1]

    if not Path(transcript_path).exists():
        print(f"Error: File not found: {transcript_path}")
        sys.exit(1)

    # Parse options
    output_path = None
    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        if output_idx + 1 < len(sys.argv):
            output_path = sys.argv[output_idx + 1]

    # Analyze
    analyzer = SpeakerAnalyzer()
    print(f"Analyzing: {transcript_path}")
    analyzer.analyze(transcript_path)
    analyzer.print_analysis()

    # Remap if names were detected
    if analyzer.speaker_names:
        print("\nWould you like to create a remapped transcript? (y/n): ", end="")
        response = input().strip().lower()

        if response == 'y':
            analyzer.remap_transcript(transcript_path, output_path)
    else:
        print("\n💡 Tip: Make sure speakers introduce themselves or address each other by name.")


if __name__ == '__main__':
    main()
