edX Experience API Bridge
=========================

Parse the edX event log, convert the events to xAPI format, and publish them to an LRS.


## Installation

```sh
$ git clone https://github.com/adlnet/edx-xapi-bridge.git
$ cd edx-xapi-bridge
$ virtualenv env
$ source env/bin/activate
(env)$ pip install -r requirements.txt
(env)$ deactivate
$ 
```

## Configuration

Rename the file *xapi-bridge/settings-dist.py* to *settings.py* and change the properties to match your environment. There are several properties you will want to customize, and they are documented below.

* *PUBLISH_MAX_PAYLOAD* and *PUBLISH_MAX_WAIT_TIME*

	To save bandwidth and server time, the xAPI Bridge will publish edX events in batches of variable size, depending on the configuration. It will wait to publish a batch until either *PUBLISH_MAX_PAYLOAD* number of events have accumulated, or *PUBLISH_MAX_WAIT_TIME* seconds have elapsed since the oldest event was queued for publishing. You should tune these values based on the expected usage of the edX LMS and the performance of the LRS.
	
	Reasonable default values are *10* and *60*, respectively.

* *LRS_ENDPOINT*, *LRS_USERNAME*, and *LRS_PASSWORD*

	The URL and login credentials of the LRS to which you want to publish edX events. The endpoint URL should end in a slash, e.g. *http://mydoma.in/xAPI/*.


## Running

There is no process management yet, so just run the module directly:

```sh
$ source env/bin/activate
(env)$ python xapi-bridge [watchfile]
(env)$ deactivate
$
```

The program can optionally take one argument, which is the file path to the log to be watched. If omitted, it is assumed to be the default location in the edX Development Stack, */edx/var/log/tracking.log*.

**NOTE**: The tracking log typically has very strict permissions on it, so make sure the user account running the xAPI-Bridge has permissions to read the log file.


## License

Copyright 2014 United States Government, as represented by the Secretary of Defense.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

