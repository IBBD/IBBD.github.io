# 基于laravel和Bootstrap的cms系统

Github：https://github.com/BootstrapCMS/CMS/

## 基于Docker镜像测试

- `docker pull ibbd/nginx`
- `docker pull ibbd/php-fpm`
- `docker pull ibbd/mariadb`
- `docker pull ibbd/node-dev`

## 安装 

除非特别说明，否则步骤是基于ibbd/php-fpm的命令行进行：

```sh
# 1. git clone 
# 宿主机器
# 可以顺便把composer.json中的laravel/framework的版本改为：5.1.*
cd /var/www
git clone git@github.com:BootstrapCMS/CMS.git laravel_cms
chown -R www-data:www-data storage

# 后台初始的管理员的账号密码在这个文件：app/Seeds/UsersTableSeeder.php
# 修改成自己的

# 2. composer install
composer install --no-dev -o

# 3. npm install 
# 在ibbd/node-dev镜像内
# 很慢很慢，使用cnpm install会快一点
npm install 

# 4. create database
create database laravel_cms

# 5. edit .env
cp .env.example .env 
vim .env 

# 6. gulp 
# 在ibbd/node-dev镜像内
gulp --production

# 7. app install
php artisan app:install

```

注意要按照顺序执行，否则可能会出现异常。



