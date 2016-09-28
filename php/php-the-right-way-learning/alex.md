# php-the-right-way-learning-阅读笔记 By Alex

## 代码风格检查 

```sh
# 安装 
sudo pear install PHP_CodeSniffer

# 使用
phpcs filename.php
# 这条命令也可以用在 git hook 中，如果你的分支代码不符合选择的代码标准则无法提交
```

## 日期和时间 

PHP 中 DateTime 类的作用是在你读、写、比较或者计算日期和时间时提供帮助。除了 DateTime 类之外，PHP 还有很多与日期和时间相关的函数，但 DateTime 类为大多数常规使用提供了优秀的面向对象接口。它还可以处理时区。

文档：http://php.net/manual/en/class.datetime.php

## 浏览器层面的 UTF-8

使用 *mb_http_output()* 函数来确保 PHP 向浏览器输出 UTF-8 格式的字符串。

## 依赖注入

### 依赖反转

依赖反转准则是面向对象设计准则 S.O.L.I.D 中的 “D” ,倡导 “依赖于抽象而不是具体”。简单来说就是依赖应该是接口/约定或者抽象类，而不是具体的实现。

```php
<?php
namespace Database;

class Database
{
    protected $adapter;

    public function __construct(AdapterInterface $adapter)
    {
        $this->adapter = $adapter;
    }
}

interface AdapterInterface {}

class MysqlAdapter implements AdapterInterface {}
```

### 容器



## 数据库 

- 使用*utf8mb4*，而不是utf8. 
- 使用PDO扩展或者Mysqli扩展，而不使用mysql扩展
- 防注入

```php
<?php
$pdo = new PDO('sqlite:/path/db/users.db');
$stmt = $pdo->prepare('SELECT name FROM users WHERE id = :id');
$id = filter_input(INPUT_GET, 'id', FILTER_SANITIZE_NUMBER_INT); // <-- filter your data first (see [Data Filtering](#data_filtering)), especially important for INSERT, UPDATE, etc.
$stmt->bindParam(':id', $id, PDO::PARAM_INT); // <-- Automatically sanitized for SQL by PDO
$stmt->execute();
```

对于写入操作，例如 INSERT 或者 UPDATE，进行数据过滤并对其他内容进行清理（去除 HTML 标签，Javascript 等等）是尤其重要的。PDO 只会为 SQL 进行清理，并不会为你的应用做任何处理。

## 安全

### 使用 password_hash 来哈希密码

```php
<?php
require 'password.php';

$passwordHash = password_hash('secret-password', PASSWORD_DEFAULT);

if (password_verify('bad-password', $passwordHash)) {
    // Correct Password
} else {
    // Wrong password
}
```

### 数据过滤

- 永远不要信任外部输入。请在使用外部输入前进行过滤和验证。filter\_var() 和 filter\_input() 函数可以过滤文本并对格式进行校验（例如 email 地址）。
- 记住，外部输入的定义并不局限于用户通过表单提交的数据。上传和下载的文档，session 值，cookie 数据，还有来自第三方 web 服务的数据，这些都是外服输入。

### 配置文件

- 推荐你将你的配置信息存储在无法被直接读取和上传的位置上。
- 如果你一定要存储配置文件在根目录下，那么请使用 .php 的扩展名来进行命名。这将可以确保即使脚本被直接访问到，它也不会被以明文的形式输出出来。
- 配置文件中的信息需要被针对性的保护起来，对其进行加密或者设置访问权限。

## 测试

为你的 PHP 程序编写自动化测试被认为是最佳实践，可以帮助你建立良好的应用程序。 自动化测试是非常棒的工具，它能确保你的应用程序在改变或增加新的功能时不会影响现有的功能，不应该忽视。

### 测试驱动开发

- 单元测试：PHPUnit 是业界PHP应用开发单元测试框架的标准
- 集成测试：
- 功能性测试：

功能测试的工具

- Selenium
- Mink
- Codeception 是一个全栈的测试框架包括验收性测试工具。
- Storyplayer 是一个全栈的测试框架并且支持随时创建和销毁测试环境。

### 行为驱动开发

有两种不同的行为驱动开发 (BDD): SpecBDD 和 StoryBDD。 SpecBDD 专注于代码的技术行为，而 StoryBDD 专注于业务逻辑或功能的行为和互动。这两种 BDD 都有对应的 PHP 框架。

采用 StoryBDD 时, 你编写可读的故事来描述应用程序的行为。接着这些故事可以作为应用程序的实际测试案例执行。Behat 是使用在 PHP 应用程序中的 StoryBDD框架，它受到 Ruby 的 Cucumber 项目的启发并且实现了 Gherkin DSL 來描述功能的行为。

采用 SpecBDD 时, 你编写规格来描述实际的代码应该有什么行为。你应该描述函数或者方法应该有什么行为，而不是测试函数或者方法。PHP 提供了 PHPSpec 框架来达到这个目的，这个框架受到了 Ruby 的 RSpec project 项目的启发。

另：Codeception 是一个使用 BDD 准则的全栈测试框架。


## 构建及部署应用 

如果你在手动的进行数据库结构的修改或者在更新文件前手动运行测试，请三思而后行！因为随着每一个额外的手动任务的添加都需要去部署一个新的版本到应用程序，这些更改会增加程序潜在的致命错误。即使你是在处理一个简单的更新，全面的构建处理或者持续集成策略，构建自动化绝对是你的朋友。

### 构建自动化工具

构建工具可以认为是一系列的脚本来完成应用部署的通用任务。构建工具并不属于应用的一部分，它独立于应用层 ‘之外’。

Phing 是一种在 PHP 领域中最简单的开始自动化部署的方式。通过 Phing 你可以控制打包，部署或者测试，只需要一个简单的 XML 构建文件。Phing (基于Apache Ant) 提供了在安装或者升级 web 应用时的一套丰富的任务脚本，并且可以通过 PHP 编写额外的任务脚本来扩展。

Capistrano 是一个为 中高级程序员 准备的系统，以一种结构化、可复用的方式在一台或多台远程机器上执行命令。对于部署 Ruby on Rails 的应用，它提供了预定义的配置，不过也可以用它来 部署 PHP 应用 。如果要成功的使用 Capistrano ，需要一定的 Ruby 和 Rake 的知识。

对 Capistrano 感兴趣的 PHP 开发者可以阅读 Dave Gardner 的博文 PHP Deployment with Capistrano ，来作为一个很好的开始。

Chef 不仅仅只是一个部署框架， 它是一个基于 Ruby 的强大的系统集成框架，除了部署你的应用之外，还可以构建整个服务环境或者虚拟机。

Deployer 是一个用 PHP 编写的部署工具，它很简单且实用。并行执行任务，原子化部署，在多台服务器之间保持一致性。为 Symfony、Laravel、Zend Framework 和 Yii 提供了通用的任务脚本。

### 持续集成

持续集成是一种软件开发实践，团队的成员经常用来集成他们的工作， 通常每一个成员至少每天都会进行集成 — 因此每天都会有许多的集成。许多团队发现这种方式会显著地降低集成问题， 并允许一个团队更快的开发软件。

对于 PHP 来说，有许多的方式来实现持续集成。近来 Travis CI 在持续集成上做的很棒，对于小项目来说也可以很好的使用。Travis CI 是一个托管的持续集成服务用于开源社区。它可以和 Github 很好的集成，并且提供了很多语言的支持包括 PHP 。

## Docker

下面的命令, 会下载一个功能齐全的 Apache 和 最新版本的 PHP, 并会设置 WEB 目录 /path/to/your/php/files 运行在 http://localhost:8080:

```sh
docker run -d --name my-php-webserver -p 8080:80 -v /path/to/your/php/files:/var/www/html/ php:apache
```

在使用 docker run 命令以后, 如果你想停止, 或者再次开启容器的话, 只需要执行以下命令:

```sh
docker stop my-php-webserver
docker start my-php-webserver
```

## 缓存 

### Opcache：opcode缓存

php5.5自带了opcode缓存工具Opcache。

API: http://php.net/manual/zh/ref.opcache.php 

### 对象缓存


- APCu 和 Memcached 。APCu 对于对象缓存来说是个很好的选择，它提供了简单的 API 让你能将数据缓存到内存，并且很容易设置和使用。APCu 的局限性表现在它依赖于所在的服务器。
- 值得注意的是当你以 CGI(FastCGI) 的形式使用 PHP 时，每个进程将会有各自的缓存，比如说，APCu 缓存数据无法在多个工作进程中共享。

## 文档撰写

PHPDoc 是注释 PHP 代码的非正式标准。它有许多不同的标记可以使用。完整的标记列表和范例可以查看 PHPDoc 指南。






---------

Date: 2015-10-09  Author: alex cai <cyy0523xc@gmail.com>
