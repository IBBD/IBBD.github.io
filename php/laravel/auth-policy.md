# Laravel中的授权策略
自laravel5.1.11开始支持`Gate`和`Policy`，详见文档：http://laravelacademy.org/post/577.html

文档中提到多种的实现方式，这里只摘取我们可用的部分。

## 策略类（Policies）

### 创建策略类
为了避免授权逻辑越来越臃肿笨重，尤其是在大型应用中，所以Laravel允许你将授权逻辑分割到多个“策略”类中，策略类是原生的PHP类，基于授权资源对授权逻辑进行分组。

首先，让我们生成一个策略类来管理对Post模型的授权，你可以使用Artisan命令`make:policy`来生成该策略类。生成的策略类位于`app/Policies`目录：

```sh
php artisan make:policy PostPolicy
```

### 编写策略
策略类生成之后，我们可以为授权的每个权限添加方法。例如，我们在PostPolicy中定义一个update方法，该方法判断给定User是否可以更新某个Post：

```php
<?php

namespace App\Policies;

use App\User;
use App\Post;

class PostPolicy{
    /**
     * 判断给定文章是否可以被给定用户更新
     *
     * @param  \App\User  $user
     * @param  \App\Post  $post
     * @return bool
     */
    public function update(User $user, Post $post)
    {
        return $user->id === $post->user_id;
    }
}
```

你可以继续在策略类中为授权的权限定义更多需要的方法，例如，你可以定义show, destroy, 或者 addComment方法来认证多个Post动作。

注：所有策略类都通过服务容器进行解析，这意味着你可以在策略类的构造函数中类型提示任何依赖，它们将会自动被注入。

## 注册策略类
PostPolicy类创建好之后，我们就需要考虑将其应用到我们的Post模型中。

而AuthServiceProvider包含了一个policies属性来映射实体及管理该实体的策略类。因此，我们指定Post模型的策略类是PostPolicy：

```php
<?php

namespace App\Providers;

use App\Post;
use App\Policies\PostPolicy;
use Illuminate\Contracts\Auth\Access\Gate as GateContract;
use Illuminate\Foundation\Support\Providers\AuthServiceProvider as ServiceProvider;

class AuthServiceProvider extends ServiceProvider{
    /**
     * 应用的策略映射
     *
     * @var array
     */
    protected $policies = [
        Post::class => PostPolicy::class,
    ];
}
```

## 应用策略到控制器
在上面注册策略类是时候，已经将策略类和模型做了绑定（`Post::class => PostPolicy::class`，其中`Post`就是我们的模型），下面我们来看看怎么在控制器中应用授权策略：

```php
<?php

namespace App\Http\Controllers;

use App\Post;
use App\Http\Controllers\Controller;

class PostController extends Controller{
    /**
     * 更新给定文章
     *
     * @param  int  $id
     * @return Response
     */
    public function update($id)
    {
        $post = Post::findOrFail($id);

        // $post是Post的一个实例对象，而PostPolicy又已经注册到了Post上面
        // 这里会直接授权策略类PostPolicy类的update方法（同名方法）
        $this->authorize($post);

        // 更新文章...
    }
}
```

如果授权成功，控制器继续正常执行；然而，如果authorize方法判断该动作授权失败，将会抛出HttpException 异常并生成带403 Not Authorized状态码的HTTP响应。正如你所看到的，authorize方法是一个授权动作、抛出异常的便捷方法。

如果控制器类的方法名和授权策略类的方法名不一致，则可以这样使用：

```php
<?php

    // 这里故意制造了一个不同名的updatePost方法
    // 实际使用的时候，PostPolicy中的update策略是有可能应用到其他的控制器方法上的
    public function updatePost($id)
    {
        $post = Post::findOrFail($id);

        // 这里指定应用PostPolicy中的update方法
        $this->authorize('update', $post);

        // 更新文章...
    }
```

AuthorizesRequeststrait还提供了authorizeForUser方法用于授权非当前用户：

```php
<?php
$this->authorizeForUser($user, 'update', $post);
```

