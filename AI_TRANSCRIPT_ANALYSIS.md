# AI Transcript Analysis Guide

This guide is for AI assistants (like Claude) to intelligently analyze transcripts and identify speakers by name.

## The Problem

Whisper diarization outputs generic labels:
```
[00:00:05] [Speaker SPEAKER_00] Hi, I'm Alice from accounting.
[00:00:12] [Speaker SPEAKER_01] Thanks Alice, I'm Bob from IT.
[00:00:20] [Speaker SPEAKER_00] Nice to meet you, Bob.
```

We want:
```
[00:00:05] [Alice] Hi, I'm Alice from accounting.
[00:00:12] [Bob] Thanks Alice, I'm Bob from IT.
[00:00:20] [Alice] Nice to meet you, Bob.
```

## The Solution

AI assistant analyzes the transcript text to find speaker names, then maps them to speaker IDs.

## For AI Assistants: Speaker Name Detection Patterns

When analyzing a transcript, look for these patterns:

### Pattern 1: Self-Introduction
```
"Hi, I'm <NAME>"
"This is <NAME>"
"My name is <NAME>"
"<NAME> here"
"It's <NAME>"
```

**Example:**
```
[Speaker SPEAKER_00] Hi, I'm Alice from accounting.
```
→ Map SPEAKER_00 = "Alice"

### Pattern 2: Being Addressed
```
"Thanks <NAME>"
"<NAME>, can you..."
"Hey <NAME>"
"<NAME> mentioned..."
```

**Example:**
```
[Speaker SPEAKER_01] Thanks Alice, I'm Bob.
```
→ "Alice" was just SPEAKER_00 (previous speaker)
→ Map SPEAKER_01 = "Bob"

### Pattern 3: Third-Person Reference (Less Reliable)
```
"Alice said..."
"Bob's idea..."
"<NAME> thinks..."
```

**Use carefully** - might be talking about someone not in the conversation.

### Pattern 4: Context Clues
```
"Troy asked me to..."  → Troy is likely SPEAKER_00 or SPEAKER_01
"Send it to Alice"     → Alice is likely present
"Dr. Smith will..."    → Formal title
```

## Analysis Workflow for AI Assistants

### Step 1: Read the Transcript

```python
# Transcript format
lines = [
    "[00:00:05] [Speaker SPEAKER_00] Hi, I'm Alice from accounting.",
    "[00:00:12] [Speaker SPEAKER_01] Thanks Alice, I'm Bob from IT.",
    "[00:00:20] [Speaker SPEAKER_00] Nice to meet you, Bob.",
]
```

### Step 2: Extract Speaker IDs and Text

```
SPEAKER_00:
  - "Hi, I'm Alice from accounting."
  - "Nice to meet you, Bob."

SPEAKER_01:
  - "Thanks Alice, I'm Bob from IT."
```

### Step 3: Find Name Patterns

**SPEAKER_00:**
- Self-intro: "I'm Alice" → Candidate: "Alice"
- Being addressed: (none in their lines)
- High confidence: Alice

**SPEAKER_01:**
- Self-intro: "I'm Bob" → Candidate: "Bob"
- Addresses other: "Thanks Alice" → Confirms SPEAKER_00 is Alice
- High confidence: Bob

### Step 4: Build Confidence Map

```
SPEAKER_00 = "Alice" (confidence: HIGH)
  - Said "I'm Alice" (self-intro)
  - Called "Alice" by SPEAKER_01

SPEAKER_01 = "Bob" (confidence: HIGH)
  - Said "I'm Bob" (self-intro)
  - Called "Bob" by SPEAKER_00
```

### Step 5: Generate Remapped Transcript

```
[00:00:05] [Alice] Hi, I'm Alice from accounting.
[00:00:12] [Bob] Thanks Alice, I'm Bob from IT.
[00:00:20] [Alice] Nice to meet you, Bob.
```

## Example AI Prompts

### For Claude Analyzing a Transcript:

**User:** "Analyze this transcript and identify speakers"

**Claude should:**
1. Read the transcript file
2. Extract all speaker IDs (SPEAKER_00, SPEAKER_01, etc.)
3. Look for name patterns in the text
4. Build confidence map
5. Suggest name mappings: "I detected: SPEAKER_00 = Alice (high confidence), SPEAKER_01 = Bob (high confidence)"
6. Offer to create remapped version

### Handling Uncertainty

**Low confidence:**
```
SPEAKER_00 = "Alice" (confidence: MEDIUM)
  - Only evidence: Called "Alice" once by another speaker
  - No self-introduction
```

**Ask user:** "I think SPEAKER_00 might be Alice, but I'm not certain. Can you confirm?"

**Multiple candidates:**
```
SPEAKER_00 mentioned both "Alice" and "Bob"
```

**Ask user:** "SPEAKER_00 mentioned Alice and Bob. Which one is SPEAKER_00?"

## Common Patterns by Context

### Business Meeting
- Look for: titles (Dr., Prof., Mr., Ms.), role mentions ("I'm the PM")
- Names often mentioned at start: "Let's get started. Alice, Bob, thanks for joining."

### Casual Conversation
- Nicknames common: "Hey Troy", "What's up Trident"
- Less formal introductions: "Troy here", "It's Bob"

### Interview
- Interviewer/Interviewee pattern
- "Thanks for having me, Alice" → Alice is interviewer

### Podcast
- Host introduction: "Welcome to the show, I'm Alice"
- Guest introduction: "Thanks for having me, I'm Bob"

## Edge Cases

### Same Name, Multiple People
```
[Speaker SPEAKER_00] Hi, I'm Mike from sales.
[Speaker SPEAKER_01] I'm Mike too, from engineering.
```

**Solution:** Use qualifiers: "Mike (sales)", "Mike (engineering)"

### Name Changes Mid-Conversation
```
[Speaker SPEAKER_00] I'm Bob, but call me Robert.
```

**Solution:** Use preferred name: "Robert", note alias

### No Names Mentioned
```
[Speaker SPEAKER_00] So the project is due next week.
[Speaker SPEAKER_01] Yeah, we should finish testing.
```

**Solution:** Keep generic labels, or ask user: "I couldn't detect names. Can you tell me who's speaking?"

## Implementation for AI Assistants

### When User Says: "Analyze the speakers in this transcript"

```python
# Pseudo-code for AI assistant
def analyze_speakers(transcript_path):
    # 1. Read transcript
    lines = read_file(transcript_path)

    # 2. Parse lines
    speakers = {}  # {SPEAKER_00: [lines...]}

    for line in lines:
        if match := re.search(r'\[Speaker (SPEAKER_\d+)\] (.+)', line):
            speaker_id, text = match.groups()
            speakers.setdefault(speaker_id, []).append(text)

    # 3. Detect names
    name_map = {}  # {SPEAKER_00: ("Alice", confidence)}

    for speaker_id, texts in speakers.items():
        for text in texts:
            # Pattern: "I'm <NAME>"
            if match := re.search(r"I'm (\w+)", text):
                name = match.group(1)
                name_map[speaker_id] = (name, "HIGH")

            # Pattern: "My name is <NAME>"
            if match := re.search(r"my name is (\w+)", text, re.I):
                name = match.group(1)
                name_map[speaker_id] = (name, "HIGH")

    # 4. Cross-reference (being addressed)
    for speaker_id, texts in speakers.items():
        for text in texts:
            # Pattern: "Thanks <NAME>"
            if match := re.search(r"(?:Thanks|Hey|Hi) (\w+)", text):
                addressed_name = match.group(1)
                # Find which speaker has this name
                for other_id, (name, _) in name_map.items():
                    if name == addressed_name:
                        # Boost confidence
                        name_map[other_id] = (name, "HIGH")

    # 5. Present findings
    print("Detected speakers:")
    for speaker_id, (name, conf) in name_map.items():
        print(f"  {speaker_id} = {name} (confidence: {conf})")

    # 6. Offer to remap
    if confirm("Create remapped transcript?"):
        remap_transcript(lines, name_map)
```

### When User Says: "Who was speaking in this transcript?"

**AI should:**
1. Analyze as above
2. Summarize: "I detected 2 speakers: Alice and Bob"
3. Optionally: "Alice spoke first and mentioned accounting. Bob spoke second and mentioned IT."

### When User Says: "Replace speaker labels with names"

**AI should:**
1. Analyze transcript
2. Build name map
3. Create new file with names replacing SPEAKER_00, etc.
4. Save as `transcript_named.txt`

## Tools AI Can Create

### Auto-Remap Script

```bash
# User runs at work
whisper-live analyze-speakers transcript.txt

# Output:
# Detected speakers:
#   SPEAKER_00 = Alice (high confidence)
#   SPEAKER_01 = Bob (medium confidence)
#
# Remap transcript? (y/n): y
# Saved to: transcript_named.txt
```

### Interactive Mode

```bash
whisper-live name-speakers transcript.txt

# Output:
# SPEAKER_00 says: "Hi, I'm Alice"
# Is SPEAKER_00 named Alice? (y/n): y
#
# SPEAKER_01 says: "Thanks Alice, I'm Bob"
# Is SPEAKER_01 named Bob? (y/n): y
#
# Saving remapped transcript...
```

## Best Practices for AI Assistants

1. **Always show confidence levels** - Don't guess quietly
2. **Ask when uncertain** - Better to confirm than be wrong
3. **Preserve original** - Create new file, don't overwrite
4. **Handle edge cases gracefully** - Same names, nicknames, etc.
5. **Context matters** - Business meeting ≠ casual chat
6. **Update incrementally** - Can re-analyze if more context appears later

## Example AI Interaction

**User:** "Can you analyze the speakers in my transcript?"

**Claude:**
```
I'll analyze the transcript for speaker names.

Reading transcript.txt...

Found 2 speakers across 12 lines.

Speaker Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEAKER_00 (6 lines)
  - Self-intro: "Hi, I'm Alice from accounting"
  - Addressed as: "Alice" (by SPEAKER_01)
  → Name: Alice (HIGH confidence)

SPEAKER_01 (6 lines)
  - Self-intro: "I'm Bob from IT"
  - Addressed as: "Bob" (by SPEAKER_00)
  → Name: Bob (HIGH confidence)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like me to create a remapped version with names instead of speaker IDs?
```

**User:** "Yes"

**Claude:**
```
Created transcript_named.txt with speaker names.

Before:
[00:00:05] [Speaker SPEAKER_00] Hi, I'm Alice from accounting.

After:
[00:00:05] [Alice] Hi, I'm Alice from accounting.

Summary:
- SPEAKER_00 → Alice (6 lines)
- SPEAKER_01 → Bob (6 lines)
```

## Limitations

1. **Whisper errors** - If Whisper mishears "I'm Alice" as "I'm Ellis", analysis will map wrong name
2. **No self-introduction** - If speakers never introduce themselves, can't detect
3. **Third parties** - Might mention people not in the conversation
4. **Ambiguity** - Multiple people with same name
5. **Nicknames** - "Bob" vs "Robert" vs "Bobby"

## Future Enhancements

- ML model trained on name detection
- Integration with contact lists (Troy's calendar → likely speakers)
- Voice recognition to map speaker IDs across sessions
- Confidence scoring algorithm
- Support for non-English names

## For Developers: Adding to Whisper Live

To add this as a feature:

```python
# whisper_live/analysis/speaker_names.py
class SpeakerNameDetector:
    def analyze(self, transcript_file):
        # Implement analysis logic
        pass

    def remap_transcript(self, transcript_file, name_map):
        # Create remapped version
        pass
```

```bash
# New CLI command
whisper-live analyze-speakers transcript.txt
whisper-live remap-speakers transcript.txt --map "SPEAKER_00=Alice,SPEAKER_01=Bob"
```

## Summary for AI Assistants

**You can:**
- Analyze transcripts for speaker names
- Map SPEAKER_00, SPEAKER_01 to real names
- Create remapped transcripts
- Handle uncertainty gracefully

**You should:**
- Show confidence levels
- Ask when unsure
- Preserve originals
- Explain reasoning

**You shouldn't:**
- Guess wildly
- Overwrite files
- Ignore context
- Assume all names are speakers

This makes diarization much more useful for users!
