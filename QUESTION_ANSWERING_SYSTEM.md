# Question Answering & Learning System

## Overview
This system automatically detects questions in lead replies, analyzes them, and learns from manual answers to improve confidence over time.

## Implementation Summary

### 1. Knowledge Base Updates ✅
**File:** `knowledge_base/brine_faq.md`
- Added **Brand Overview** section (Section 1.5)
- Added **Lead Q&A** section (Section 18) with 6 frequently asked questions

### 2. Question Detection Agent ✅
**File:** `execution/question_detector.py`
- Detects if replies contain questions
- Identifies question types: pricing, technical, capability, process, comparison, general
- Returns confidence scores for each question detected

### 3. Enhanced Learning Agent ✅
**File:** `execution/learning_agent.py`
- Added `analyze_question()` method to analyze questions and learn from manual answers
- Added `get_confidence_for_question()` method to calculate confidence scores
- Stores Q&A pairs in `knowledge_base/question_learning.json`
- Tracks confidence scores by question type

### 4. Updated Lead Maintenance ✅
**File:** `execution/maintain_leads.py`
- Integrated Question Detection Agent
- For **Interested/Neutral + Questions**:
  - Detects questions
  - Analyzes and learns (no auto-reply)
  - Categorizes in Gmail with appropriate labels
  - Updates Google Sheet status
  - Flags low confidence answers (< 85%)

### 5. Gmail Labels ✅
- **"Questions - Needs Answer"**: Questions detected, waiting for manual answer
- **"Low Confidence Answers"**: Flagged for review (confidence < 85%)

### 6. Question Learning Database ✅
**File:** `knowledge_base/question_learning.json`
- Stores Q&A pairs from manual answers
- Tracks confidence scores by question type
- Used to improve future answer confidence

## Workflow

```
Lead Replies
    ↓
Sentiment Analysis (Interested/Neutral/Not Interested/OOO)
    ↓
Question Detection (if Interested/Neutral)
    ↓
    ├─ Questions Found:
    │     ↓
    │  Analyze Questions
    │     ↓
    │  Calculate Confidence Score
    │     ↓
    │  ├─ ≥ 85% → Label: "Questions - Needs Answer"
    │  └─ < 85% → Label: "Low Confidence Answers" ⚠️
    │     ↓
    │  Learn from Question (store for future)
    │     ↓
    │  Update Sheet Status
    │     ↓
    │  NO AUTO-REPLY (manual review required)
    │
    └─ No Questions → Continue existing flow
```

## Key Features

### Question Detection
- Detects explicit questions (with "?")
- Detects implicit questions (statements asking for information)
- Categorizes by type for better learning

### Learning System
- Learns from your manual answers
- Stores Q&A pairs for future reference
- Improves confidence scores over time
- Tracks question frequency

### Confidence Scoring
- Calculates confidence based on:
  - Similar questions in database
  - Question type patterns
  - Knowledge base coverage
- Flags low confidence (< 85%) for manual review

### Gmail Organization
- Automatic labeling for easy filtering
- "Questions - Needs Answer" for questions needing responses
- "Low Confidence Answers" for flagged questions

## Usage

### When a Lead Asks Questions:
1. System detects questions automatically
2. Analyzes question type and confidence
3. Categorizes in Gmail (no auto-reply)
4. Updates Google Sheet status
5. Learns from your manual answer when you respond

### Learning from Manual Answers:
When you manually reply to a question:
- The Learning Agent analyzes your answer
- Stores the Q&A pair in the database
- Updates confidence scores
- Improves future question detection

### Viewing Questions:
- Check Gmail label: "Questions - Needs Answer"
- Check Gmail label: "Low Confidence Answers" (for flagged questions)
- Google Sheet status shows: "Questions - Interested" or "Questions - Neutral"

## Next Steps

1. **Monitor Questions**: Check Gmail labels regularly for questions needing answers
2. **Answer Manually**: Reply to questions as usual - system will learn automatically
3. **Review Low Confidence**: Check "Low Confidence Answers" label for questions that need attention
4. **Improve Knowledge Base**: Add frequently asked questions to `brine_faq.md` to improve confidence

## Files Modified/Created

1. ✅ `knowledge_base/brine_faq.md` - Added Brand Overview and Lead Q&A
2. ✅ `execution/question_detector.py` - NEW: Question detection agent
3. ✅ `execution/learning_agent.py` - Enhanced with question analysis
4. ✅ `execution/maintain_leads.py` - Integrated question detection
5. ✅ `knowledge_base/question_learning.json` - NEW: Q&A learning database

## System Status: ✅ READY

The question answering and learning system is fully implemented and ready to use!

