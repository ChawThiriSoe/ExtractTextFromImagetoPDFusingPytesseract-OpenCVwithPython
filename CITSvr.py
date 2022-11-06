from flask import Flask,render_template,request
from PIL import Image
import cv2
import pytesseract
import imutils
import os
import numpy
import pyperclip	# for copy to clipboard function
import getpass 		# for getting username of PC
import docx 		# for making document file
from fpdf import FPDF	# for making PDF file

import nltk
from nltk.corpus import wordnet as WN
from nltk.corpus import stopwords
from spellchecker import SpellChecker	# for post processing

from datetime import datetime 		# for record run time

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

app = Flask(__name__)
app.SECRET_KEY = 'textrecong'

# This is the dir path for saving input images
path = os.getcwd()
images_folder = os.path.join(path, r"static/images/savedImg/")
if not os.path.isdir(images_folder):
	os.mkdir(images_folder)
app.config['images_folder'] = images_folder

# This is the starting point of the system
# From this, the image which are wanted to process OCR can be submitted
@app.route('/index')
def index():
	return render_template('index.html')

# The submitted image will be undertaken in this pre_processing function firstly.
# The function resized, binarized, dilated and eroded the noises from the image as a pre processing of OCR.
def  pre_processing(get_img):
	try:
		open_img = Image.open(get_img)				# open image
		img_file = images_folder + get_img.filename
		open_img.save(img_file)						# save that image in "images" folder

		img = cv2.imread(img_file)						# read the image
		
		img = imutils.resize(img, width=2000)			# resize image
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)		# binarize image
		img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 11)
		img = cv2.GaussianBlur(img,(5,5),1)
		kernel = numpy.ones((3,3), numpy.uint8)
		img = cv2.dilate(img, kernel, iterations=1)		# apply dilation to remove some noise
		img = cv2.erode(img, kernel, iterations=1)		# apply erosion to remove some noise
		img = cv2.bilateralFilter(img, 11, 17, 17)		# smooth the image and remove noises
		
		img_file = "../static/images/savedImg/" + get_img.filename 	# resign img_file for src in html
		return img, img_file

	except Exception as e:
		print(e)
		msg = "Sorry, something goes wrong! Try Again!!"
		return render_template('index.html', msg=msg)

# The preprocessed image will be contined to this function to extract the text from it.
def text_recognition(lgselect,img):
	try:
		myconfig = r"-l " + lgselect + " --psm 6 --oem 3"
		text = pytesseract.image_to_string(img, config=myconfig)	# recognize text from image

		msg = "Your image is successfully converted !!!"
		return text, msg

	except Exception as e:
		print(e)
		msg = "Sorry, something goes wrong! Try Again!!"
		return render_template('index.html', msg=msg)

# The extracted text will be undertaken to process this function for checking the spelling.
# Note: only text in English and Spanish languages can be proceeded effectively. Others will be resulted as same as extracted text.
def post_processing(text,lgselect):
	try:
		post_text = ""

		if 'eng' in lgselect:
			stop_words = set(stopwords.words('english'))
			spell = SpellChecker(language='en')
		elif 'spa' in lgselect:
			stop_words = set(stopwords.words('spanish'))
			spell = SpellChecker(language='es')
		elif 'deu' in lgselect:
			stop_words = set(stopwords.words('german'))
			spell = SpellChecker(language='de')
		elif 'por' in lgselect:
			stop_words = set(stopwords.words('portuguese'))
			spell = SpellChecker(language='pt')

		for word in nltk.word_tokenize(text.lower()):
			strip = word.rstrip()
			if not WN.synsets(strip):
				if strip in stop_words:
					post_text += strip + " "
				else:
					post_text += spell.correction(strip) + " "
			else:
				post_text += word + " "
		return post_text

	except Exception as e:
		print(e)
		msg = "Sorry, something goes wrong! Try Again!!"
		return render_template('index.html', msg=msg)

# This function performs saving the text file in which the extracted text included, in the 'Downloads' folder as the 'txtfile.txt'
def txtdownload(text):
	path = "C:/Users/" + getpass.getuser() + "/Downloads/txtfile_" + str(datetime.now().strftime("%f")) + ".txt"

	with open(path, 'w', encoding="utf-16") as f:
		for item in text:
			f.write(item)
		f.close()
	msg = "Txt File is downloaded successfully !!"
	return msg

# This function performs saving document file in which the extracted text included, in the 'Downloads' folder as the 'wordfile.docx'
def docxdownload(text):
	path = "C:/Users/" + getpass.getuser() + "/Downloads/wordfile_" + str(datetime.now().strftime("%f")) + ".docx"
	doc = docx.Document()
	doc.add_paragraph(text)
	doc.save(path)

	msg = "Word File is downloaded successfully !!"
	return msg

# This function performs saving pdf file in which the extracted text included, in the 'Downloads' folder as the 'pdffile.pdf'
def pdfdownload(text,lgselect):
	path = "C:/Users/" + getpass.getuser() + "/Downloads/pdfFile_" + str(datetime.now().strftime("%f")) + ".pdf"
	pdf = FPDF(format='A4')
	pdf.add_page()

	pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
	pdf.set_font('DejaVu', '', 14)

	for txt in text.split('\n'):
	    pdf.write(8, txt)
	    pdf.ln(8)

	pdf.output(path, 'F')

	msg = "PDF File is downloaded successfully !!"
	return msg

@app.route('/output', methods=['POST'])
# This is the main function in which all the above functions are called relevantly. 
def output():
	try:
		# Image acquisition Process
		if 'Upload' in request.form:
			lgselect = request.form['lgselect']
			get_img = request.files['img']

			# Image validation
			if Image.open(get_img).format.lower() in ['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp', 'pnm', 'jfif']:
				# start recording time for processing OCR
				start_time = datetime.now()

				# Preprocessing Process
				img, img_file = pre_processing(get_img)

				# Text Extracting Process
				text, msg = text_recognition(lgselect, img)

				# Post Processing Process
				post_text = post_processing(text,lgselect)

				# end recording time
				end_time = datetime.now()

				# Output OCR processing time
				print('OCR Run Time: {} seconds'.format(end_time - start_time))

				return render_template('output.html', img_file=img_file, extracted_text=text, post_text=post_text, lg_select=lgselect, msg=msg)
			else:
				msg = "Image must be a PNG, JPG or JPEG file!  Please Try Again!!!"
				return render_template('index.html', msg=msg)

		else:
			# Copying or Downloading The Extracted Text Process
			extracted_text = request.form['extractext']
			post_text = request.form['posttext']
			img_file = request.form['img']
			lgselect = request.form['lgselect']

			# For Reults Before Post Processing Process
			if 'copytxtbe' in request.form:
				pyperclip.copy(extracted_text)
				msg = "Extracted Text is copied !!"

			elif 'txtdownloadbe' in request.form:
				msg = txtdownload(extracted_text)

			elif 'docxdownloadbe' in request.form:
				msg = docxdownload(extracted_text)

			elif 'pdfdownloadbe' in request.form:
				msg = pdfdownload(extracted_text,lgselect)

			# For Reults After Post Processing Process
			elif 'copytxtaf' in request.form:
				pyperclip.copy(post_text)
				msg = "Extracted Text is copied !!"

			elif 'txtdownloadaf' in request.form:
				msg = txtdownload(post_text)

			elif 'docxdownloadaf' in request.form:
				msg = docxdownload(post_text)

			elif 'pdfdownloadaf' in request.form:
				msg = pdfdownload(post_text,lgselect)

			else:
				msg = "Please Try Again!!!"

			return render_template('output.html', img_file=img_file, extracted_text=extracted_text, post_text=post_text, lg_select=lgselect, msg=msg)
	except Exception as e:
		print(e)
		msg = "Sorry, something goes wrong! Try Again!!"
		return render_template('index.html', msg=msg)

if __name__ == "__main__":
	app.run(debug=True)