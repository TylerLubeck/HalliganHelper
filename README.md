# HalliganHelper
[![Gitter chat](https://badges.gitter.im/HalliganHelper/HalliganHelper.png)](https://gitter.im/HalliganHelper/)

Welcome! HalliganHelper is a system for managing Teacher's Assistants and the
students who need them. It offers real-time queuing so that both students and
TAs can know when they'll be helped. 

It's written in [python][python], [django][django], and [backbone][backbone].

| Branch  | Test Status | Coverage |
| ------  | ----------- | -------- |
| Develop | [![Build Status](https://travis-ci.org/HalliganHelper/HalliganHelper.svg?branch=develop)](https://travis-ci.org/HalliganHelper/HalliganHelper) | [![Codecov branch](https://img.shields.io/codecov/c/github/HalliganHelper/HalliganHelper/develop.svg)](https://codecov.io/gh/HalliganHelper/HalliganHelper/branch/develop) |
| Master  | [![Build Status](https://travis-ci.org/HalliganHelper/HalliganHelper.svg?branch=master)](https://travis-ci.org/HalliganHelper/HalliganHelper) | [![Codecov branch](https://img.shields.io/codecov/c/github/HalliganHelper/HalliganHelper/master.svg)](https://codecov.io/gh/HalliganHelper/HalliganHelper/branch/master) |





## Organization Rules

We have exactly 2:

1. Don't be rude. This project is meant to be friendly to beginners and
experienced developers alike. We're all here to learn!

2. If you find a security bug, please email 
support@halliganhelper.com immediately, and _don't_ open a github issue. We'll
do our best to patch it as soon as possible.

## Reporting Bugs

*Most Importantly* if you find a security bug, please email 
support@halliganhelper.com immediately, and _don't_ open a github issue. We'll
do our best to patch it as soon as possible.

Otherwise, file an issue on the [Github Issue Tracker][issues]. Please leave
the labeling to us.


## Contributing

_All PRs require tests before they will be merged_.

Fork the repository and follow the setup instructions below. If they don't work
for you, please quietly offer up your offering of chosen swear words to the
devops deities and file a ticket. We'll prioritize these tickets, because if 
people can't help out than what's the point?

After you've set up your development environment, check the 
[Github Issue Tracker][issues]. If you're interested in working on a ticket,
and nobody else has claimed it, comment there and let everyone know you're 
going to take it on. If you're interested in something but don't see a ticket
for it, search for any tickets that may have been closed as "WontFix" or 
similar. Assuming your ticket isn't found there, file a new one. Then start
coding and open a PR. We'll review your code, chat about other implications,
and offer constructive criticism. If a reviewer offers criticism that you feel
is something other than constructive, feel free to call them out.


### Development Setup

1. Install [docker](https://www.docker.com/products/docker-desktop)
2. Start everything with docker compose:  `docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d`
3. Run all database migrations with docker compose: `docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up db-migrations`
   . This should print a bunch of lines with `OK`, and then exit 0
4. Create a super user: `docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run python migrate.py createsuperuser`
5. Visit the site at `https://localhost` - You may have to allow a self-signed cert


#### Changing Python Packages

If you make any changes to `requirements.txt` then you'll need to rebuild the containers to pull the changes in.
The easiest way to do this is to redeploy with `docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up --build -d`


As you write your python code, uwsgi will detect the changes and automatically reload the server

As you write your javascript code, webpack will detect the changes and automatically re-render the output

Either way, you'll need to refresh the browser after changes.


[python]: https://www.python.org/
[django]: https://www.djangoproject.com/
[backbone]: http://backbonejs.org/
[issues]: https://github.com/HalliganHelper/HalliganHelper/issues
