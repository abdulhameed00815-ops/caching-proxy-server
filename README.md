# **my first caching proxy server**
in this project, i make a simple caching proxy server.<br/>
all i do is make a http server with a generic api route that can accept all types of requests, i take the path (suffix) of the request, put it in the end of the url of the origin (the intended backend server), then do the caching stuff and return the response.
