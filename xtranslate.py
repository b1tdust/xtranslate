#!/usr/bin/python

import subprocess
import webbrowser
from urllib.parse import quote
import argparse
import gi
import os

gi.require_version('Notify', '0.7')
from gi.repository import GLib, Notify, GdkPixbuf

__author__ = 'Brian Mayo'

config = {
	'translate': 'en:es',
	'timeout': 5000,
	'params': ['-b']
}


def get_text():
	# get primary selection
	proc = subprocess.Popen(['xsel', '-p'], stdout=subprocess.PIPE, universal_newlines=True)
	text = proc.stdout.read()
	if not text:
		# get from clipboard
		proc = subprocess.Popen(['xsel', '-b'], stdout=subprocess.PIPE, universal_newlines=True)
		text = proc.stdout.read()
	return text


def open_gtranslate(nt, action_name, data):
	global config
	langs = config['translate'].split(":")
	webbrowser.open('https://translate.google.com/#{}/{}/'.format(langs[0] if langs[0] else 'auto', langs[1]) + quote(data))
	nt.close()
	close()
		
	
def close():
	Notify.uninit()
	exit(1)


def main():
	text = get_text()
	if not text:
		return 

	parser = argparse.ArgumentParser(description='xtranslate - show translations as notifications using translate shell')
	parser.add_argument('-tr', '--translate',
											help='Translate source and destination language. e.g es:en; :es (for auto detection)',
											required=False)
	parser.add_argument('-t', '--timeout', help='Notification timeout', required=False)
	parser.add_argument('-p', '--params',
											help='Coma separated Translate shell params. e.g d,sp. Please read translate shell docs',
											required=False)
	args = parser.parse_args()
	if args.translate:
		config['translate'] = args.translate
	if args.timeout:
		config['timeout'] = int(args.timeout)
	if args.params:
		params = args.params.split(',')
		config['params'] = ["-{}".format(x) for x in params]

	cmd = ['trans'] + config['params'] + [config['translate']]	
	cmd.append(text)
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
	p.wait()
	translated = p.stdout.read()
	dir = os.path.dirname(__file__)	
	image = GdkPixbuf.Pixbuf.new_from_file(os.path.join(dir, "gt_icon.png")) 
	Notify.init("xTranslate")
	notification = Notify.Notification.new("xtranslate", translated)
	notification.set_icon_from_pixbuf(image)
	notification.set_image_from_pixbuf(image)
	notification.set_timeout(config['timeout'])
	notification.add_action('clicked', 'open in browser', open_gtranslate, text)
	notification.show()
	GLib.timeout_add_seconds(config['timeout'] / 1000 + 1, close) # wait timeout + 1 second before exit
	

if __name__ == "__main__":
	main()
	GLib.MainLoop().run()
