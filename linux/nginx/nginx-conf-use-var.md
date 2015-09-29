# 使用变量来简化nginx配置文件

原文：http://mo2g.com/view/61/ 

## 普通的配置文件

没有使用变量的nginx虚拟主机配置文件如下：

```
server {
    listen          80;
    server_name     blog.mo2g.com;
    root  /www;
    access_log      /www/logs/blog.mo2g.com.access.log main;
    location / {
        index index.php index.html;

    }
    location ~ \.php$ {
        root           html;
        fastcgi_pass   127.0.0.1:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  /www$fastcgi_script_name;
        include        fastcgi_params;
    }
}
```

仔细的观察上边的配置，不难发现，/www这个路径出现了3次，如果要配置10个，100个虚拟主机，那就得写30遍，300遍路径，如果中途需要做相关修改，那工作量就更大了，而且很容易出错。然而换成变量，那就方便了。

上边的配置使用变量后，可以拆分为两个部分：

1）公用部分，新建一个php.conf配置文件，内容如下

```
location ~ \.php$ {
    root           html;
    fastcgi_pass   127.0.0.1:9000;
    fastcgi_index  index.php;
    fastcgi_param  SCRIPT_FILENAME  $root$fastcgi_script_name;
    include        fastcgi_params;
}
```

2）定制部分，再新建一个虚拟主机的配置文件blog.mo2g.com.conf，内容如下： 

``` 
server {
    listen          80;
    server_name     blog.mo2g.com;
    set $root /www;#声明$root变量
    root  $root;
    access_log      $root/logs/blog.mo2g.com.access.log main;
    location / {
        index index.php index.html;
    }
    include php.conf;#加载配置文件
}
```

## 使用变量简化后的配置文件

上边的代码，有以下几点改变:

1. 把网站根目录的路径通过set操作赋值给了$root变量
2. 分离公用的配置，在需要时include加载进来

基于上边的思想，我们可以再添加一个static.conf配置文件，用来配置静态文件的缓存时间，与一些反盗链的规则

``` 
#防止mo2g.com以外的域名盗用本站资源
location ~ .*\.(gif|jpg|png|swf|flv|rar|zip)$ { 
    valid_referers none blocked *.mo2g.com mo2g.com; 
    if ($invalid_referer) { 
        return 403;
        #rewrite   ^/   http://blog.mo2g.com/images/default/logo.gif; 
    }   
}
#静态资源缓存时间
location ~ .*\.(gif|jpg|jpeg|png|bmp|ico|swf)$ {
    expires 30d;
}
location ~ .*\.(js|css)$ {
    expires 1d; 
}
```

nginx配置通过使用变量，配置文件可以很简洁，很容易进行管理。 

