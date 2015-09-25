# 基于laravel的cms系统

Github：https://github.com/BootstrapCMS/CMS/

## 安装 

```sh
# 1. git clone 
git clone git@github.com:BootstrapCMS/CMS.git 

# 2. composer install
composer install --no-dev -o

# 3. npm install 
# 很慢很慢，使用cnpm install会快一点
npm install 

# 4. create database
create database laravel_cms

# 5. edit .env
cp .env.example .env 
vim .env 

# 6. gulp 
gulp --production

# 7. app install
php artisan app:install

```


