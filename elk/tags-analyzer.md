# Tags数据在ElasticSearch中的保存与分析

标签数据是一种常见的数据，例如每个人，每部电影等都可以有不同的标签，怎么能正确的保存并分词很重要。

## 构造标签分词器

构造一个`analyzer`，使用分号进行分隔。这样只要导入es时，保存相应的格式即可。

`settings.json`如下：

```json
{
    "settings": {
        "analysis": {
            "analyzer": {
                "tags_analyzer": {
                    "type": "pattern",
                    "pattern": ";"
                }
            }
        }
    }
}
```

对应的`mappings.json`如下：

```json
{
    "properties": {
        "tags": {
            "type": "string",
            "index": "analyzed",
            "analyzer": "tags_analyzer"
        },
        ...
    }
}
```

## 使用Python生成相应的索引结构

```python
es = ElasticSearch(host)

with open(settings_file_name, 'r') as f:
    settings_json = json.loads(f.read())
es.create_index(index_name, settings=settings_json)

with open(mapping_file_name) as f:
    mapping = json.loads(f.read())
es.put_mapping(index_name, doc_type, mapping)
```

然后就可以正常的往es写入数据了。。。


