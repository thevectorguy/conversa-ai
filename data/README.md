# Data Directory

Place your dataset file here:

## Required File
- `BiztelAI_DS_Dataset_V1.json` - The main dataset containing chat transcripts

## Dataset Structure Expected
The JSON file should contain chat transcripts with the following structure:

```json
{
  "transcript_id_1": {
    "article_url": "https://www.washingtonpost.com/...",
    "config": "A",
    "content": [
      {
        "message": "Text of the message",
        "agent": "agent_1",
        "sentiment": "Neutral",
        "knowledge_source": ["FS1", "FS2"],
        "turn_rating": "Good"
      }
    ]
  }
}
```

## Notes
- The application will automatically load and process this file on startup
- Make sure the file is properly formatted JSON
- The file will be processed to extract insights about agent conversations and article discussions
