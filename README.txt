Text Detection & Recognition System
------------------------------
This system is for detecting text from the image and coverting it to ediable text. The images can be taken from printed document images or some natural sences which does not have the special font style of text. This system aims to be easy the process of changing manual documents to digital files. Tesseract, one of OCR algorithm and openCV with Python programming language are used to developed this system.

Installation
----------
Firstly, tesseract-ocr is needed to install in your OS. Tesseract path is needed to add in your system environment.
Noted: It needs to be default path to install it. That makes to add the tesseract path to system environment.

After that, traineddata files which are used to different languages in pytesseract are needed to import in "C:\Program Files\Tesseract-OCR\tessdata".
The traineddata files are attached with this file.

In addition, following python libraries are needed to install in order to run the system.
	- Flask
	- Pytesseract
	- OpenCV
	- PIL
	- Imutils
	- Numpy
	- Os
	- Getpass
	- Pyperclip
	- Docx
	- FPDF
	- NLTK
	- SpellChecker
	- Datetime

Usage
-----
The system can be run with 'CITSvr.py' python file.
	" py CITSvr.py "

Following step can be done after running python file.
1. Open in the browser with 'localhost:5000/index'
2. Upload the image
3. Select one of the listed languages
4. Click 'Submit' buttom
5. See the extracted text in 'localhost:5000/ouput'
	- First result is not passed the post processing process
	- Second result is passed the post processing process
6. Continue download processes
	1) Can copy both results once per time
	2) Can download as txt file
	3) Can download as docx file
	4) Can download as pdf file
