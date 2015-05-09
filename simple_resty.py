#!/usr/bin/python

from twilio.rest import TwilioRestClient
from flask import Flask
from flask import request
import flask
import boto.ses
import boto
import logging
from logging.handlers import RotatingFileHandler
import json
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(['creds.ini', '~/creds.ini', '/home/pi/creds.ini'])
 
client = TwilioRestClient(
  config.get('twilio', 'account_sid'),
  config.get('twilio', 'auth_token')
)

app = Flask(__name__)

@app.route('/')
def home():
  return 'nope.'

@app.route('/health')
def health():
  return 'true'

@app.route('/twilio/sms-to-email', methods=['GET', 'POST'])
def sms_to_email():
  email_addr = config.get('basic', 'email')
  account_sid = config.get('twilio', 'account_sid')

  msg = request.values.to_dict()

  if msg.get('account_sid') != account_sid:
    return 'no soup for you.'

  subject = 'twilio sms from ' + msg.get('From', '')
  body = "%s\n\n--\ndump of all request shit: %s" % (msg.get('Body', ''), json.dumps(msg, indent=2))

  conn = boto.connect_ses(profile_name='pjnet')
  send_resp = conn.send_email(email_addr, subject, body, [email_addr])
  app.logger.info('sent email. response: ' + str(send_resp))
  return flask.Response('<Response></Response>', mimetype='text/xml')

@app.route('/twilio/no-phone-calls-please')
def no_phone_calls():
  extra = request.get('extra', '')

  xml = '<?xml version="1.0" encoding="UTF-8"?><Response>'
  for x in range(2):
    xml += '<Say voice="woman">Sorry, this number only accepts SMS text messages.</Say>'
    if extra == 'de':
      xml += '<Say voice="man" language="de">Sorry, akzeptiert nur diese Zahl Kurznachrichtendienst.</Say>'

  xml += '</Response>'
  return flask.Response(xml, mimetype='text/xml')

def stash():
  message = client.messages.create(body='', to='', from_=config.get('twilio', 'de_phone'))
  print message.sid 

if __name__ == '__main__':
  handler = RotatingFileHandler('/home/pi/flask.log', maxBytes=100*1024*1024, backupCount=5)
  handler.setLevel(logging.INFO)
  app.logger.addHandler(handler)
  app.run(host='0.0.0.0')
