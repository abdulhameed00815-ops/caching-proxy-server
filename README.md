# **my first caching proxy server**
in this project, i make the simplist caching proxy server.<br/> i use nginx to grab requests from the client, and either forward it to my backend server (if the response is completely new)<br/> or grab the cached responses inside of a directory on my pc.<br/>
the following is some of my nginx config:

    http {
        proxy_cache_path /var/cache keys_zone=mycache:10m loader_threshold=300 loader_files=200;
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';

        access_log  /var/log/nginx/access.log  main;
    
        sendfile            on;
        tcp_nopush          on;
        keepalive_timeout   65;
        types_hash_max_size 4096;
    
        include             /etc/nginx/mime.types;
        default_type        application/octet-stream;
    
        # Load modular configuration files from the /etc/nginx/conf.d directory.
        # See http://nginx.org/en/docs/ngx_core_module.html#include
        # for more information.
        include /etc/nginx/conf.d/*.conf;
    
    
        server {
            location / {
                    proxy_pass http://127.0.0.1:8000;
                    proxy_cache mycache;
                    proxy_cache_valid 200 10m;
                    proxy_cache_use_stale error timeout updating;
            }
        }
    
