# public-speaking-platform

The front-end is developed using html5, bootstrap, and javascript, and the back-end is developed using the flask framework and the web template engine used is Jinja2

Libraries used -
1. [my-voice-analysis](https://github.com/Shahabks/my-voice-analysis)
2. [gaze tracking](https://github.com/antoinelame/GazeTracking)
3. CV2 library
4. Speech Recognition python library

[Click here to access the live project](http://monami.coach:5000/home)

How to locally run the project for development:
1. Create and activate a virtual environment 
2. ensure the virtual env is on Python 3.8.3 (some of the packages aren't compatible with any other version)
3. Use the pip install -r requirements.txt command to install all of the Python modules and packages required for the project.
4. Once the requirements are done installing use the flask run command to run the project loacally.
5. If running locally the variables in report.html file will have to be hardcoded, this is in the reportVariables_localTesting file, copy paste it at the top of report.html
6. The better option is to have a development server running and push code there for testing.
7. All the variables pushed to frontend using Jinja2 are present at the end of app.py with the routes.
8. for creating a new page i've created a template base.html which has all the standard code, Extend it using {% extends 'base.html' %} and then use Jinja blocks for the rest of the page.
9. A lot of the old code is commented out, any commented out code has either been updated with new functionality of is aesthetic/design parts.
10. The initial html template that was used for the project is [here](https://templatemo.com/tm-568-digimedia), you can use it for any new frontend development while maintaining css.

How to use the public speaking platform:

- Step 1. Click on Start Practicing Now.
- Step 2. Click on Turn On Camera to start the camera.
- Step 3. Click on Record to record the audio.
- Step 4. Click on Start Recording to start the video recording.
- Step 5. Click on Stop Recording to stop the video recording.
- Step 6. Click on Save Recording to save the video recording.
- Step 7. Click on Stop to stop audio recording.
- Step 8. Click on Upload next to the audio recording to upload it to the server for processing.
- Step 9. Click on Done to get to the next stage, once done with recording.
- Step 10. Once the video finishes processing click on Get Report to get a detailed report.
