# Compliance checker

This repo has logic to get compliance policies from an endpoint, store it and use it to check compliance of a website which is provided in a GET request.

## Methodology 
It uses map reduce like scheme to break down large policies to smaller policies to which the website will be compared with.
Then from the individual results, we summarize them to a single output list of actions.
These actions are to correct the website for compliance reasons.

## Running the application
1. Add OPEN API key to vars_example.py and rename it vars.py
2. Install dependencies - pip install -r requirements.txt 
3. Run application using - python main.py 