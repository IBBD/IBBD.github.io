# 基于React，React-router, Flux等的前端工程的目录结构 

我们用于生产环境的目录结构，先看：

```
/js js主目录
    /common   公共模块目录
        /components    公共组件
            layout.react.js     
            header.react.js     
            footer.react.js     
        /config        公共配置文件目录
            constants.js    常量配置
        /stores 
            user-stores.js  用户stores
        dispatcher.js    全站公用的dispatcher 
    /article  功能模块目录，其他功能模块类似
        /components    组件目录
            index.react.js     
        /actions       actions文件目录
        /stores        存储目录(Reflux store)
        /config        功能模块的配置文件
            constants.js    常量配置
        router.js      功能模块的路由文件
    app.js    主入口js
/public    网站根目录
    /build        编译后的文件目录
    /css          css文件 
    /js           外部引用的js文件，如jQuery等，如果需要的话
    index.html    网站入口文件
/nginx     nginx配置文件
/node-modules 
package.json 
webpack.config.js 
```

## 几点说明 

- 网站的根目录独立在一个public目录下
- 项目的每一个模块都是一个独立的目录，并且有自己的路由等，基本是完全独立的部分
- React-router的官方demo中，组件根据路由的层级嵌套，太深，对于开发并不好
- Flux的官方demo，常量定义在constants目录中，我们是定义在config目录中，可以有其他的配置也放到该目录下

demo程序可以看这里：https://github.com/IBBD/react-router-flux-demo/tree/master 
（可以切换到react-router-flux这个tag）



---------

Date: 2015-11-10  Author: alex cai <cyy0523xc@gmail.com>
