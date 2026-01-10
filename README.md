# **My caching proxy server**

## project overview:
in this project, i make a simple caching proxy server.<br/>
all i do is make a http server with a generic api route that can accept all types of requests, i take the path (suffix) of the request, put it in the end of the url of the origin (the intended backend server), then do the caching stuff and return the response.

## detailed features:
1-get and post methods get cached.
<br/>
2-cached requests get deleted automatically on server start.
<br/>
3-postgresql is used for storing the cached requests.
