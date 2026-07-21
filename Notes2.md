Step 1 - Determine if we're doing a drag or roll race

- For now, check manually and hard code value

Step 2 - Determine starting point
Is this a drag race?

- Yes
  - Set starting time when the speedometer value increases (use box method) - 1 second
- No, roll race
  - Set starting time when the audio has a big increase and stays loud for a few seconds

Step 3 - Determine ending point
Option 1

- Check where the speedometer has a big decrease in its value
  Option 2
- Check where the audio has a big decrease
