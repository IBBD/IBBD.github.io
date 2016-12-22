# Laravel数据迁移是的一个坑（float类型）

数据迁移时，当需要创建`float`类型的字段，运行之后，发现数据库里是`double`类型，查看源码如下：

```php
// vim Database/Schema/Grammars/MySqlGrammar.php

    /**
     * Create the column definition for a float type.
     *
     * @param  \Illuminate\Support\Fluent  $column
     * @return string
     */
    protected function typeFloat(Fluent $column)
    {
        return $this->typeDouble($column);
    }

    /**
     * Create the column definition for a double type.
     *
     * @param  \Illuminate\Support\Fluent  $column
     * @return string
     */
    protected function typeDouble(Fluent $column)
    {
        if ($column->total && $column->places) {
            return "double({$column->total}, {$column->places})";
        }

        return 'double';
    }
```

对于5.1和5.3版本都是这样子，其他版本应该也类似，但是官方文档貌似没有这个说明。

