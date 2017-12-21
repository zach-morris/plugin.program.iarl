import os, base64, smtplib, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class iarl_share_tools():
	def gun(self):
		return base64.b64decode(self.gunn2()+self.gunn1())
	def gpsww1(self):
		return base64.b16decode(self.common3()+'768'+self.common010(4)+'3326C7'+self.common010(340462)+'626D393064')
	def common3(self):
		return '644'
	def common010(self,opt):
		if opt < 10101:
			#Why
			return '706'
			#r u here
		elif opt > 10101 and opt < 20202:
			#Yes
			return '766'
			#I know
		elif opt > 20202 and opt < 30303:
			#secu
			return '777'
			#rity
		elif opt > 30303 and opt < 40404:
			#and obsur
			return '333'
			#rity
		elif opt > 50505 and opt < 60606:
			#are
			return 'D'
			#not
		else:
			#the
			return 'A'
			#same
	def gpsw(self):
		#Even so
		return base64.b64decode(self.gpsww1()+self.gpsww2())
	def gunn2(self):
		#Im confused
		return base64.b16decode(self.common1()+'7467962484E6F59584'+self.common010(61412)+self.common010(604)+'26'+self.common010(53613))
	def common1(self):
		#Im confused
		return '615'
	def gsmtp_int(self):
		#Even so
		return 465
	def common101(self,opt):
		if opt < 10101:
			#same
			return '607'
			#the
		elif opt > 10101 and opt < 20202:
			#not
			return '667'
			#are
		elif opt > 20202 and opt < 30303:
			#rity
			return '888'
			#and obsur
		elif opt > 30303 and opt < 40404:
			#rity
			return '222'
			#secur
		elif opt > 50505 and opt < 60606:
			#I know
			return 'A'
			#Yes
		else:
			#r u here
			return 'D'
			#Why
	def gsmtp(self):
		return base64.b64decode(self.gsmtp1())
	def gto1(self):
		return base64.b16decode('4D5449774F5459355A6'+self.common010(55673)+'4E415A6D6C795'+self.common010(99889988)+'53356D6457356B5A584A7A593278315969356A6232303D')
	def gpsww2(self):
		return base64.b16decode('584A7759584E7'+self.common010(160601)+'643239795A413D3D')
	def gunn1(self):
		return base64.b16decode(self.common3()+'15A323168615'+self.common010(25613)+'7559323974')
	def gto(self):
		return base64.b64decode(self.gto1())
	def gsmtp1(self):
		return base64.b16decode('633231306343356E625746706243356'+self.common010(90909)+'6232303D')

	def share_fav(self,title,user,description,share_filename,send_the_message):
		share_tool_msg = ''
		success = False
		#Send a shared favorites list to iarl.extras
		try:
			if os.path.isfile(share_filename):
				current_time = datetime.datetime.now()
				if title is None or len(title)<1:
					title = 'Unnamed '+str(current_time.isoformat())
				if user is None or len(user)<1:
					user = 'Anonymous'
				if description is None or len(description)<1:
					description = 'None provided'
				msg = MIMEMultipart()
				msg['From'] = self.gun()
				msg['To'] = self.gto()
				msg['Subject'] = 'IARL Extra '+str(title)
				with open(share_filename, 'r') as content_file:
					file_content = content_file.read()
				attachment = MIMEText(file_content)
				attachment.add_header('Content-Disposition', 'attachment', filename=str(os.path.split(share_filename)[-1]))           
				msg.attach(attachment)
				msg.attach(MIMEText('IARL Extra from '+str(user)+', sent on '+str(current_time.isoformat())+'\n\nTitle: '+str(title)+'\n\nDescription: '+str(description),'plain'))
				if send_the_message:
					#Send to github as new issue
					server_ssl = smtplib.SMTP_SSL(self.gsmtp(), self.gsmtp_int())
					server_ssl.ehlo() #Optional
					server_ssl.login(self.gun(),self.gpsw())
					server_ssl.sendmail(self.gun(),self.gto(),msg.as_string())
					server_ssl.close()
					share_tool_msg = 'IARL:  Share sent From:  '+str(user)+', with the Title: '+str(title)
				else:
					share_tool_msg = 'IARL: Test share, no message sent:  '+msg.as_string()
				success = True
			else:
				share_tool_msg = 'IARL:  Unable to locate file to attach'
				success = False
		except Exception, (exc):
			share_tool_msg = 'IARL:  Unknown error occured:  '+str(exc)
			success = False
		return success, share_tool_msg