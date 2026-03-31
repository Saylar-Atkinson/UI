# D3LTA UI -- Closed Testing Survey

> **Instructions for testers:** Please fill in this survey during or after testing D3LTA UI. Answer every question honestly -- there are no wrong answers. Your feedback will directly shape the next version of the tool. The survey takes approximately 15--20 minutes.
>
> **Instructions for form administrators:** Each section below maps to a section in Google Forms. Question types are indicated in square brackets. Options/scales are listed as bullet points. Conditional logic (skip/branch) is noted where applicable.

---

## Section 1: About You

*This section helps us understand who is testing and interpret feedback in context.*

### 1.1 What is your name or tester identifier?
[Short text -- required]

### 1.2 What is your role or job function?
[Multiple choice -- required]
- Analyst / Investigator
- Data scientist / Machine-learning engineer
- Software developer / Engineer
- Researcher / Academic
- Manager / Team lead
- Other (please specify) [Short text]

### 1.3 How would you describe your technical proficiency?
[Multiple choice -- required]
- Non-technical (I rarely use command-line tools or write code)
- Somewhat technical (I use spreadsheets and basic data tools regularly)
- Technical (I write code or scripts and work with data pipelines)
- Highly technical (I build or maintain software systems professionally)

### 1.4 Before this test, how familiar were you with the D3lta library?
[Multiple choice -- required]
- Not familiar at all -- this is my first time hearing about it
- I have heard of it but never used it
- I have used it via the command line or Python API
- I have contributed to or developed with D3lta extensively

### 1.5 What browser and operating system did you use for testing?
[Short text -- required]
*Example: Firefox 128 on Windows 11, Chrome 126 on macOS Sonoma*

### 1.6 Did you test on a mobile device or tablet at any point?
[Multiple choice -- required]
- No, desktop/laptop only
- Yes, mobile phone
- Yes, tablet
- Yes, both mobile and tablet

---

## Section 2: First Impressions

*Think back to when you first opened D3LTA UI.*

### 2.1 When you first loaded the Home page, was the purpose of the application immediately clear?
[Linear scale 1--5 -- required]
1 = Not at all clear ... 5 = Perfectly clear

### 2.2 How visually appealing did you find the interface on first impression?
[Linear scale 1--5 -- required]
1 = Very unappealing ... 5 = Very appealing

### 2.3 Was the top navigation bar (Upload CSV / Task Status / Help) easy to understand and use?
[Linear scale 1--5 -- required]
1 = Very confusing ... 5 = Very easy

### 2.4 Did you notice and try the "Help" link (PDF) in the navigation?
[Multiple choice -- required]
- Yes, I opened and read the Help PDF
- Yes, I opened it but did not read it thoroughly
- I noticed it but did not open it
- I did not notice it

### 2.5 If you opened the Help PDF, how useful was it?
[Linear scale 1--5 -- optional]
1 = Not useful at all ... 5 = Very useful

*Show this question only if answer to 2.4 includes "Yes".*

---

## Section 3: Uploading a CSV File

*This section covers the "Upload CSV" page and the upload process.*

### 3.1 How many times did you upload a CSV file during testing?
[Multiple choice -- required]
- 0 (I did not upload any file)
- 1
- 2--3
- 4--5
- More than 5

*If 0, skip to Section 4.*

### 3.2 Were the Processing Parameters (thresholds, minimum text size, truncate text, use N rows) clear and easy to understand?
[Linear scale 1--5 -- required]
1 = Very confusing ... 5 = Perfectly clear

### 3.3 Did you use the "Help?" links next to the processing parameter fields?
[Multiple choice -- required]
- Yes, and the explanations were helpful
- Yes, but the explanations were not sufficient
- No, I did not need them
- No, I did not notice them

### 3.4 Were the default parameter values (Grapheme: 0.693, Language: 0.715, Semantic: 0.85, Min Text Size: 10) appropriate for your use case?
[Multiple choice -- required]
- Yes, the defaults worked well
- I had to adjust them but the defaults were a reasonable starting point
- The defaults did not work for my data and I was unsure what to change
- I am not sure / I did not change them

### 3.5 After selecting a CSV file, did the file preview (column headers, first rows, line count) appear correctly?
[Multiple choice -- required]
- Yes, it loaded quickly and looked correct
- Yes, but it was slow to load
- The preview appeared but had issues (please describe below)
- The preview did not appear at all
- I did not pay attention to the preview

### 3.6 If the file preview had issues, please describe them.
[Long text -- optional]

### 3.7 Was the "Text Column Name" dropdown straightforward to use? Did it correctly list the columns from your file?
[Linear scale 1--5 -- required]
1 = Did not work / very confusing ... 5 = Worked perfectly

### 3.8 Did you need to change the "Column Separator" setting?
[Multiple choice -- required]
- No, "Auto" worked correctly
- Yes, I had to change it and it then worked correctly
- Yes, I had to change it but it still did not work correctly
- I did not notice this option

### 3.9 How was the upload experience after pressing Submit (progress bar, redirect to task status)?
[Linear scale 1--5 -- required]
1 = Very poor / confusing ... 5 = Smooth and clear

### 3.10 Did you encounter any upload failures?
[Multiple choice -- required]
- No
- Yes, due to an invalid file or parameters (the error message was clear)
- Yes, due to an invalid file or parameters (the error message was unclear)
- Yes, due to a server or network error

### 3.11 If you encountered upload failures, please describe what happened.
[Long text -- optional]

---

## Section 4: Task Status and Results

*This section covers the "Task Status" page, job lookup, and viewing results.*

### 4.1 Did you use the "Task Status" page to look up a previously submitted job by its Task ID?
[Multiple choice -- required]
- Yes
- No

### 4.2 Was it clear that you need to save/copy the Task ID to retrieve results later?
[Linear scale 1--5 -- required]
1 = Not clear at all ... 5 = Perfectly clear

### 4.3 Did the "Copy" button for the Task ID work correctly?
[Multiple choice -- required]
- Yes
- No, it did not copy the ID
- I did not try the Copy button
- I did not see a Copy button

### 4.4 While your job was pending or processing, was the status information (status message, auto-refresh) adequate?
[Linear scale 1--5 -- required]
1 = Very inadequate / confusing ... 5 = Very clear and informative

### 4.5 Approximately how long did you wait for processing to complete?
[Multiple choice -- required]
- Less than 30 seconds
- 30 seconds to 2 minutes
- 2 to 5 minutes
- 5 to 15 minutes
- More than 15 minutes
- Processing never completed (failed or still running)

### 4.6 Once processing was complete (status: Done), were the results clearly presented?
[Linear scale 1--5 -- required]
1 = Very unclear ... 5 = Very clear

### 4.7 Was the Matches preview table (first 10 rows) useful for understanding the results?
[Linear scale 1--5 -- required]
1 = Not useful at all ... 5 = Very useful

### 4.8 Were you able to download the full Matches CSV file without issues?
[Multiple choice -- required]
- Yes, the download worked correctly
- The download link was broken or did not work
- I did not try to download the file

### 4.9 Did you interact with the Clusters section (cluster dropdown, cluster preview, per-cluster downloads)?
[Multiple choice -- required]
- Yes, and everything worked as expected
- Yes, but I encountered issues (please describe below)
- No, I did not explore the Clusters section
- I did not see a Clusters section

### 4.10 If you encountered issues with the Clusters section, please describe them.
[Long text -- optional]

### 4.11 Did you encounter any jobs that failed (status: Failed)? If so, was the error information (message, "Error Details" section) helpful?
[Multiple choice -- required]
- I did not encounter any failures
- Yes, and the error information helped me understand what went wrong
- Yes, but the error information was unclear or unhelpful

### 4.12 Did you encounter any expired jobs? Was the expiration message clear?
[Multiple choice -- required]
- I did not encounter any expired jobs
- Yes, and the message was clear
- Yes, but the message was confusing

---

## Section 5: Usability

*Please rate your overall experience with D3LTA UI. Answer based on your impression during testing.*

### 5.1 I found D3LTA UI easy to use.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.2 I was able to complete my tasks without external help or documentation.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.3 The different pages and features of D3LTA UI felt consistent with each other.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.4 I felt confident using the application at all times.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.5 I would feel comfortable recommending D3LTA UI to a colleague.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.6 The terminology and labels used throughout the interface were clear and understandable.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.7 When something went wrong (error, failure, unexpected state), the application guided me on what to do next.
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

### 5.8 The application responded quickly enough for my needs (page loads, file parsing, status updates).
[Linear scale 1--5 -- required]
1 = Strongly disagree ... 5 = Strongly agree

---

## Section 6: Feature-Specific Feedback

### 6.1 Which feature did you find most useful?
[Multiple choice -- required]
- Uploading and analysing a CSV with custom parameters
- File preview before upload
- Help dialogs explaining each parameter
- Task Status lookup by Task ID
- Auto-refresh while processing
- Matches preview table and download
- Cluster browsing, preview, and per-cluster download
- Other (please specify) [Short text]

### 6.2 Which feature did you find least useful or most confusing?
[Multiple choice -- required]
- Processing parameter controls (thresholds, text sizes)
- File preview before upload
- Help dialogs explaining each parameter
- Task Status lookup by Task ID
- Auto-refresh while processing
- Matches preview table and download
- Cluster browsing, preview, and per-cluster download
- None -- everything was clear and useful
- Other (please specify) [Short text]

### 6.3 Is there any feature or functionality you expected but was missing?
[Long text -- optional]

### 6.4 How useful would the following potential features be to you? Rate each from 1 (not useful) to 5 (very useful).

#### 6.4a Visual graph or chart of clusters
[Linear scale 1--5 -- required]

#### 6.4b Ability to save and re-use parameter presets
[Linear scale 1--5 -- required]

#### 6.4c A history page listing your past uploads and their results
[Linear scale 1--5 -- required]

#### 6.4d User accounts and access control
[Linear scale 1--5 -- required]

#### 6.4e Email or notification when processing is complete
[Linear scale 1--5 -- required]

#### 6.4f Ability to preview more than 10 rows of results in the browser
[Linear scale 1--5 -- required]

#### 6.4g Side-by-side comparison of results from different parameter settings
[Linear scale 1--5 -- required]

#### 6.4h Dark mode / light mode toggle
[Linear scale 1--5 -- required]

---

## Section 7: Bugs and Issues

*Please report any bugs, glitches, or unexpected behaviour you noticed.*

### 7.1 Did you encounter any bugs during testing?
[Multiple choice -- required]
- No
- Yes, minor issues (cosmetic, non-blocking)
- Yes, major issues (blocked my workflow or caused data loss)
- Yes, both minor and major issues

*If "No", skip to Section 8.*

### 7.2 Bug report 1
*Describe one bug you encountered. Copy this block if you need to report more.*

#### What were you trying to do?
[Long text -- required]

#### What did you expect to happen?
[Long text -- required]

#### What actually happened?
[Long text -- required]

#### On which page did this occur?
[Multiple choice -- required]
- Home page
- Upload CSV page
- Task Status (search) page
- Task Status (results) page
- Help PDF
- Other (please specify) [Short text]

#### How severe was this bug?
[Multiple choice -- required]
- Cosmetic (visual glitch, typo, minor layout issue)
- Minor (inconvenient but I could work around it)
- Major (prevented me from completing a task)
- Critical (crashed the app or caused data loss)

#### Can you reproduce this bug consistently?
[Multiple choice -- required]
- Yes, every time
- Sometimes
- Only happened once
- I did not try to reproduce it

### 7.3 Bug report 2 (optional -- repeat the same fields as 7.2)
[Same structure as 7.2 -- all fields optional]

### 7.4 Bug report 3 (optional -- repeat the same fields as 7.2)
[Same structure as 7.2 -- all fields optional]

---

## Section 8: Overall Assessment

### 8.1 Overall, how satisfied are you with D3LTA UI?
[Linear scale 1--10 -- required]
1 = Very dissatisfied ... 10 = Very satisfied

### 8.2 Compared to using D3lta directly via Python or the command line, how would you rate the UI experience?
[Multiple choice -- required]
- Much better -- the UI makes it significantly easier
- Somewhat better -- the UI adds convenience
- About the same
- Worse -- I prefer the command line
- Not applicable -- I have never used D3lta outside the UI

### 8.3 What are the top 1--3 things you liked most about D3LTA UI?
[Long text -- required]

### 8.4 What are the top 1--3 things you would most like to see improved?
[Long text -- required]

### 8.5 Any other comments, suggestions, or feedback?
[Long text -- optional]

---

*Thank you for taking the time to test D3LTA UI and complete this survey. Your feedback is invaluable.*
