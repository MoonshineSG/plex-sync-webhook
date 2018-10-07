#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json, yaml
from datetime import datetime
from flask import Flask, abort, request 
from plexapi.server import PlexServer

config_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], "config.yaml")
config = yaml.load(open(config_file))

group = config['group']['name']
group_server = PlexServer(config['server'], config['group']['token'])

members = {}
for name in config['members']:
	members[name] = PlexServer( config['server'], config['members'][name] )

def log(message):
	print("%s > %s"%(datetime.now().isoformat(' '), message), file=sys.stdout)
	sys.stdout.flush()
	
def mark_show_group(section, show, season = -1, episode = -1):
	watched = True
	for server in members.values():
		if not server.library.section(section).get(show).episode(season=season, episode=episode).isWatched:
			watched = False
	if watched:
		log("'%s' S%sE%s watched by all, mark as watched on group"%(show, season, episode) )
		group_server.library.section(section).get(show).episode(season=season, episode=episode).markWatched()
	else:
		log("'%s' S%sE%s not watched by all members. Skip."%(show, season, episode) )
		
def mark_show_managed(section, show, season, episode):
	log("'%s' S%sE%s watched on group, mark as watched on managed members"%(show, season, episode) )
	for server in members.values():
		server.library.section(section).get(show).episode(season=season, episode=episode).markWatched()

def mark_movie_group(section, name):
	watched = True
	for server in members.values():
		if not server.library.section(section).get(name).isWatched:
			watched = False
	if watched:
		log("'%s' watched by all, mark as watched on group"%name)
		group_server.library.section(section).get(name).markWatched()
	else:
		log("'%s' not watched by all members. Skip."%name)
		
def mark_movie_managed(section, name):
	log("'%s' watched on group, mark as watched on managed members"%name)
	for server in members.values():
		server.library.section(section).get(name).markWatched()

app = Flask(__name__)
	
@app.route('/webhook', methods=['POST']) 
def webhook():
	if not request.form:
		abort(400)

	data = json.loads(request.form['payload'])
	user = data['Account']['title']

	#log("%s -> %s" %( user, data['event']) )
		
	if data['event'] in ["media.stop", ]:
		if ( user != group ) and ( user not in members ):
			#log("Ignore. '%s' not part of a group."%user)			
			return "OK"
		else:
			log("%s -> %s" %( user, data['event']) )
		if user == group:
			isGroup = True
			server = group_server
		else:
			isGroup = False
			server = members[user]
			
		sectionTitle = data['Metadata']['librarySectionTitle']

		if data['Metadata']['type'] == "episode":
			title = data['Metadata']['grandparentTitle']
			show = server.library.section(sectionTitle).get(title)
			
			season = data['Metadata']['parentIndex']
			episode = data['Metadata']['index']
			
			media = show.episode(season=season, episode=episode)
			
			if media.isWatched:
				if isGroup:
					mark_show_managed(sectionTitle, title, season, episode)
				else:
					mark_show_group(sectionTitle, title, season, episode)
			else:
				log("Not finished watching '%s' S%sE%s"%(title, season, episode) )
				

		if data['Metadata']['type'] == "movie":
			title = data['Metadata']['title']
			media = server.library.section(sectionTitle).get(title)
			if media.isWatched:
				if isGroup:
					mark_movie_managed(sectionTitle, title)
				else:
					mark_movie_group(sectionTitle, title)
			else:
				log("Not finished watching '%s'"%(title) )

	return "OK"

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5005, debug=False)
	