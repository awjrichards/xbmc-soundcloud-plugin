# -*- coding: utf-8 -*-
'''
Created on Sep 9, 2010
@author: Zsolt Török

Copyright (C) 2010 Zsolt Török
 
This file is part of XBMC SoundCloud Plugin.

XBMC SoundCloud Plugin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

XBMC SoundCloud Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with XBMC SoundCloud Plugin.  If not, see <http://www.gnu.org/licenses/>.
'''
import httplib2
import urllib
import simplejson as json

# SoundCloud application consumer key.
CONSUMER_KEY = "hijuflqxoOqzLdtr6W4NA"

# SoundCloud OAuth 2
CLIENT_ID_VALUE = CONSUMER_KEY
CLIENT_SECRET_VALUE = "R2yWd6rMqvkoCWIgsJ8187kqt5WPusKib0nKXbx1MI"
GRANT_TYPE_PASSWORD_VALUE = u'password'
GRANT_TYPE_REFRESH_TOKEN_VALUE = u'refresh_token'
OAUTH_TOKEN = "0000000pVsNXj5kEEuyFlf48mJQug25h"
CLIENT_ID_KEY = u'client_id'
CLIENT_SECRET_KEY = u'client_secret'
GRANT_TYPE_KEY = u'grant_type'
USERNAME_KEY = u'username'
PASSWORD_KEY = u'password'
REFRESH_TOKEN_KEY = u'refresh_token'

# SoundCloud constants
USER_AVATAR_URL = u'avatar_url'
USER_PERMALINK = u'permalink'
USER_ID = u'id'
USER_NAME = u'username'
USER_PERMALINK_URL = u'permalink_url'
TRACK_USER = u'user'
TRACK_TITLE = u'title'
TRACK_ARTWORK_URL = u'artwork_url'
TRACK_WAVEFORM_URL = u'waveform_url'
TRACK_STREAM_URL = u'stream_url'
TRACK_STREAMABLE = u'streamable'
TRACK_GENRE = u'genre'
TRACK_ID = u'id'
TRACK_PERMALINK = u'permalink'
GROUP_ARTWORK_URL = u'artwork_url'
GROUP_NAME = u'name'
GROUP_ID = u'id'
GROUP_CREATOR = u'creator'
GROUP_PERMALINK_URL = u'permalink_url'
GROUP_PERMALINK = u'permalink'
QUERY_CONSUMER_KEY = u'consumer_key'
QUERY_FILTER = u'filter'
QUERY_OFFSET = u'offset'
QUERY_LIMIT = u'limit'
QUERY_Q = u'q'
QUERY_ORDER = u'order'
QUERY_OAUTH_TOKEN = u'oauth_token'

class SoundCloudClient(object):
    ''' SoundCloud client to handle all communication with the SoundCloud REST API. '''

    def __init__(self, login=False, username='', password='', oauth_token='', oauth_refresh_token=''):
        '''
        Constructor
        '''
        self.login = login
        self.username = username
        self.password = password
        if login:
            if oauth_token and oauth_refresh_token:
                self.oauth_token = oauth_token
                self.oauth_refresh_token = oauth_refresh_token
            else:
                self.oauth_token, self.refresh_oauth_token = self._get_oauth_tokens()
        
    def _get_oauth_tokens(self):
        ''' Authenticates with SoundCloud using the given credentials and returns an OAuth access token and a refresh token.'''
        url = 'https://api.soundcloud.com/oauth2/token?' + urllib.urlencode({CLIENT_ID_KEY : CLIENT_ID_VALUE, CLIENT_SECRET_KEY : CLIENT_SECRET_VALUE, GRANT_TYPE_KEY : GRANT_TYPE_PASSWORD_VALUE, USERNAME_KEY : self.username, PASSWORD_KEY : self.password})
        h = httplib2.Http()
        resp, content = h.request(url, 'POST')
        json_content = json.loads(content)
        oauth_access_token = json_content.get('access_token')
        oauth_refresh_token = json_content.get('refresh_token')
        return oauth_access_token, oauth_refresh_token
        
    def _refresh_oauth_tokens(self, oauth_refresh_token):
        ''' Uses a refresh token to get a new OAuth access and refresh token from the SoundCloud server.''' 
        url = 'https://api.soundcloud.com/oauth2/token?' + urllib.urlencode({CLIENT_ID_KEY : CLIENT_ID_VALUE, CLIENT_SECRET_KEY : CLIENT_SECRET_VALUE, GRANT_TYPE_KEY : GRANT_TYPE_REFRESH_TOKEN_VALUE, REFRESH_TOKEN_KEY : oauth_refresh_token})
        h = httplib2.Http()
        resp, content = h.request(url, 'POST')
        json_content = json.loads(content)
        oauth_access_token = json_content.get('access_token')
        oauth_refresh_token = json_content.get('refresh_token')
        return oauth_access_token, oauth_refresh_token

    def get_tracks(self, offset, limit, mode, plugin_url, query=""):
        ''' Return a list of tracks from SoundCloud, based on the parameters. '''
        url = self._build_query_url(resource_type="tracks", parameters={ QUERY_CONSUMER_KEY: CONSUMER_KEY, QUERY_FILTER: TRACK_STREAMABLE, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_Q: query, QUERY_ORDER: "hotness"})
        print "URL: " + url
        return self._get_tracks(url)

    def _get_tracks(self, url):
        json_content = self._http_get_json(url)
        tracks = []
        for json_entry in json_content:
            if TRACK_ARTWORK_URL in json_entry and json_entry[TRACK_ARTWORK_URL]:
                thumbnail_url = json_entry[TRACK_ARTWORK_URL]
            else:
                thumbnail_url = json_entry[TRACK_USER].get(USER_AVATAR_URL)
            tracks.append({ TRACK_TITLE: json_entry[TRACK_TITLE], TRACK_STREAM_URL: json_entry.get(TRACK_STREAM_URL, ""), TRACK_ARTWORK_URL: thumbnail_url, TRACK_PERMALINK: json_entry[TRACK_PERMALINK] })

        return tracks

    def get_track(self, permalink):
        ''' Return a track from SoundCloud based on the permalink. '''
        url = self._build_track_query_url(permalink, parameters={QUERY_CONSUMER_KEY: CONSUMER_KEY})
        print 'track query url: ' + url
        json_content = self._https_get_json(url)
        print 'track query response JSON: ' + str(json_content)
        if TRACK_ARTWORK_URL in json_content and json_content[TRACK_ARTWORK_URL]:
                thumbnail_url = json_content[TRACK_ARTWORK_URL]
        else:
                thumbnail_url = json_content[TRACK_USER].get(USER_AVATAR_URL)
        track_stream_url_with_consumer_key = '%s?%s' % (json_content[TRACK_STREAM_URL], str(urllib.urlencode({QUERY_CONSUMER_KEY: CONSUMER_KEY})))
        return { TRACK_STREAM_URL: track_stream_url_with_consumer_key, TRACK_TITLE: json_content[TRACK_TITLE], TRACK_ARTWORK_URL: thumbnail_url, TRACK_GENRE: json_content[TRACK_GENRE] }

    def get_group_tracks(self, offset, limit, mode, plugin_url, group_id):
        ''' Return a list of tracks belonging to the given group, based on the specified parameters. '''
        url = self._build_groups_query_url(resource_type="tracks", group_id=group_id, parameters={ QUERY_CONSUMER_KEY: CONSUMER_KEY, QUERY_FILTER: TRACK_STREAMABLE, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_ORDER: "hotness"})
        return self._get_tracks(url)

    def get_user_tracks(self, offset, limit, mode, plugin_url, user_permalink):
        ''' Return a list of tracks uploaded by the given user, based on the specified parameters. '''
        url = self._build_users_query_url(resource_type="tracks", user_permalink=user_permalink, parameters={ QUERY_CONSUMER_KEY: CONSUMER_KEY, QUERY_FILTER: TRACK_STREAMABLE, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_ORDER: "hotness"})
        return self._get_tracks(url)
    
    def get_favorite_tracks(self, offset, limit, mode, plugin_url):
        ''' Return a list of tracks favorited by the current user, based on the specified parameters. '''
        url = self._build_query_url(base='https://api.soundcloud.com/', resource_type="me/favorites", parameters={ QUERY_OAUTH_TOKEN: OAUTH_TOKEN, QUERY_FILTER: TRACK_STREAMABLE, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_ORDER: "hotness"})
        return self._get_tracks(url)

    def get_groups(self, offset, limit, mode, plugin_url, query=""):
        ''' Return a list of groups, based on the specified parameters. '''
        url = self._build_query_url(resource_type="groups", parameters={ QUERY_CONSUMER_KEY: CONSUMER_KEY, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_Q: query, QUERY_ORDER: "hotness"})
        json_content = self._https_get_json(url)

        groups = []
        for json_entry in json_content:
            if GROUP_ARTWORK_URL in json_entry and json_entry[GROUP_ARTWORK_URL]:
                thumbnail_url = json_entry[GROUP_ARTWORK_URL]
            elif GROUP_CREATOR in json_entry and json_entry[GROUP_CREATOR] and USER_AVATAR_URL in json_entry[GROUP_CREATOR] and json_entry[GROUP_CREATOR][USER_AVATAR_URL]:
                thumbnail_url = json_entry[GROUP_CREATOR][USER_AVATAR_URL]
            else:
                thumbnail_url = ""
            groups.append({ GROUP_NAME: json_entry[GROUP_NAME], GROUP_ARTWORK_URL: thumbnail_url, GROUP_ID: json_entry[GROUP_ID], GROUP_PERMALINK_URL: json_entry[GROUP_PERMALINK_URL], GROUP_PERMALINK: json_entry[GROUP_PERMALINK] })

        return groups

    def get_users(self, offset, limit, mode, plugin_url, query):
        url = self._build_query_url(resource_type="users", parameters={ QUERY_CONSUMER_KEY: CONSUMER_KEY, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_Q: query, QUERY_ORDER: "hotness"})
        return self._get_users(url)

    def get_following_users(self, offset, limit, mode, plugin_url):
        url = self._build_query_url(base="https://api.soundcloud.com/", resource_type="me/followings", parameters={ QUERY_OAUTH_TOKEN : OAUTH_TOKEN, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_ORDER: "hotness"})
        return self._get_users(url)
        
    def get_follower_users(self, offset, limit, mode, plugin_url):
        url = self._build_query_url(base="https://api.soundcloud.com/", resource_type="me/followers", parameters={ QUERY_OAUTH_TOKEN : OAUTH_TOKEN, QUERY_OFFSET: offset, QUERY_LIMIT: limit, QUERY_ORDER: "hotness"})
        return self._get_users(url)

    def _get_users(self, url):
        ''' Return a list of users, based on the specified parameters. '''
        json_content = self._https_get_json(url)

        users = []
        for json_entry in json_content:
            users.append({ USER_NAME: json_entry[USER_NAME], USER_AVATAR_URL: json_entry[USER_AVATAR_URL], USER_ID: json_entry[USER_ID], USER_PERMALINK_URL: json_entry[USER_PERMALINK_URL], USER_PERMALINK: json_entry[USER_PERMALINK] })

        return users

    def _build_query_url(self, resource_type, parameters, base="http://api.soundcloud.com/", format="json"):
        url = '%s%s.%s?%s' % (base, resource_type, format, str(urllib.urlencode(parameters)))
        print url
        return url

    def _build_track_query_url(self, permalink, parameters, base="http://api.soundcloud.com/", format="json"):
        url = '%stracks/%s.%s?%s' % (base, permalink, format, str(urllib.urlencode(parameters)))
        return url

    def _build_groups_query_url(self, group_id, resource_type, parameters, base="http://api.soundcloud.com/", format="json"):
        url = '%sgroups/%d/%s.%s?%s' % (base, group_id, resource_type, format, str(urllib.urlencode(parameters)))
        return url

    def _build_users_query_url(self, user_permalink, resource_type, parameters, base="http://api.soundcloud.com/", format="json"):
        url = '%susers/%s/%s.%s?%s' % (base, user_permalink, resource_type, format, str(urllib.urlencode(parameters)))
        return url
    
    def _http_get_json(self, url):
        h = httplib2.Http()
        resp, content = h.request(url, 'GET')
        if resp.status == 401:
            raise RuntimeError('Authentication error')
        
        return json.loads(content)