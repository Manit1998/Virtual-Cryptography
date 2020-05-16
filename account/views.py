from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import authenticate
from account.models import data

from django.views.decorators.csrf import csrf_exempt
import hashlib

from django.views.decorators.csrf import ensure_csrf_cookie
from PIL import Image, ImageDraw, ImageFont
import os
from dental import settings
from random import SystemRandom
random = SystemRandom()
from django.http import HttpResponse,HttpResponseRedirect
import requests
from django.shortcuts import render,redirect
from django.urls import reverse
from django.conf import settings
import csv
from django.contrib import messages
from django.http import FileResponse



def login(request):
	dat={}
	#Post request handling
	if request.method == 'GET':
		return render(request, "index.html", dat)
	try:
		# print("hello")
		share_file = request.FILES["share_file"]
		username=request.POST.get("username")
		print(username)
		print(share_file)


		a=decrypt(username,share_file)
		messages.success(request,str(a))
	except Exception as e:
	# logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
		messages.error(request,"Unable to upload file. "+repr(e))

	return HttpResponseRedirect("/account/login/")
		


def encrypt(username):
	img = Image.open('account/images/image.png')
	out_filename_A = "share_1.png"
	name= hashlib.sha1(username.encode())
	hex_dig = name.hexdigest()
	print(type(hex_dig))
	file_name_B=hex_dig+".png"
	

	img = img.convert('1')
	width = img.size[0]*2
	height = img.size[1]*2
	out_image_A = Image.new('1', (width, height))
	out_image_B = Image.new('1', (width, height))
	draw_A = ImageDraw.Draw(out_image_A)
	draw_B = ImageDraw.Draw(out_image_B)
	patterns = ((1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1),
	            (0, 1, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1))
	for x in range(0, int(width/2)):
	    for y in range(0, int(height/2)):
	        pixel = img.getpixel((x, y))
	        pat = random.choice(patterns)
	        draw_A.point((x*2, y*2), pat[0])
	        draw_A.point((x*2+1, y*2), pat[1])
	        draw_A.point((x*2, y*2+1), pat[2])
	        draw_A.point((x*2+1, y*2+1), pat[3])
	        if pixel == 0:
	            draw_B.point((x*2, y*2), 1-pat[0])
	            draw_B.point((x*2+1, y*2), 1-pat[1])
	            draw_B.point((x*2, y*2+1), 1-pat[2])
	            draw_B.point((x*2+1, y*2+1), 1-pat[3])
	        else:
	            draw_B.point((x*2, y*2), pat[0])
	            draw_B.point((x*2+1, y*2), pat[1])
	            draw_B.point((x*2, y*2+1), pat[2])
	            draw_B.point((x*2+1, y*2+1), pat[3])

	b=out_image_A.save("share/share1.png")
	out_image_B.save("share/{}".format(file_name_B))
	d=data(share_name=file_name_B)
	d.save()
	return b

# encrypt("monty@123")

def decrypt(username,share11):
	import cv2
	from PIL import Image
	import PIL.ImageOps
	from pytesseract import image_to_string

	name= hashlib.sha1(username.encode())
	hex_dig = name.hexdigest()
	# print(type(hex_dig))
	file_name_B=hex_dig+".png"
	share=data.objects.filter(share_name=file_name_B)
	# print(share)
	if (len(share))>0:
		file=share[0].share_name
		print(file)
		print(type(share11))
		imageeee=Image.open(share11)
		print(imageeee)
		imageeee.save("share2.png")

		img1 = cv2.imread('share2.png', 1)  
		img2 = cv2.imread('share/{}'.format(file), 1)
		img = cv2.add(img1, img2) 
		final = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		cv2.imwrite('results/decrypted_image.png', final)
		dst = cv2.GaussianBlur(final, (5,5), cv2.BORDER_DEFAULT)
		cv2.imwrite('results/decrypted_gassuian.png', dst)
		ret3,th3 = cv2.threshold(dst,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		cv2.imwrite('results/decrypted_otsu.png', th3)
		image = Image.open('results/decrypted_otsu.png')
		inverted_image = PIL.ImageOps.invert(image)
		inverted_image.save('results/inverted.png')

		decrypt_result=image_to_string(Image.open('results/inverted.png'))
		print("hello",decrypt_result)
		os.remove('share2.png')
		if(decrypt_result==username):
			return ("Login Successfully")
		else:
			return ("Username and Share not Match")
	else:
		return ("Username and Share not Match")


# print(decrypt("monty@123","aa"))

def init(username):
	image = Image.open('account/images/background.png')
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype('account/Roboto-Bold.ttf', size = 75)
	(x, y) = (200, 100)
	#(x, y) = (50, 50)
	color = 'rgb(0, 0, 0)'
	message = username
	draw.text((x, y), message, fill = color, font = font)
	image.save('account/images/image.png')

# init("monty@123")


	

@csrf_exempt
def signup(request):
	if request.method == 'GET':
		dat={}
		return render(request, "signup.html", dat)
	
	if request.method == 'POST':
		try:
			print("hello")
			username=request.POST.get("username")
			print(username)
			init(username)
			encrypt(username)
			image = Image.open('share/share1.png')
			msg="Sign Up Successfully"
			messages.success(request,"Sign Up Successfully")
			response = HttpResponse(content_type='image/png')
			response['Content-Disposition'] = 'attachment; filename=share1.png'
			
			image.save(response,'png')
			os.remove("share/share1.png")
			return response
		
		except Exception as e:
			messages.error(request,"Unable to upload file. "+repr(e))
	return HttpResponseRedirect("/account/signup/")
	




