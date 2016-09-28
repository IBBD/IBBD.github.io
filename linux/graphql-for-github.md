# Github的GraphQL API规范摘要

see: https://developer.github.com/early-access/graphql/

## OAuth Token

For example:

```sh
curl -H "Authorization: bearer token" https://api.github.com/graphql
```

GraphQL查询时使用JSON数据，例如：

```sh
curl -H "Authorization: bearer token" -X POST -d '
{
 "query": "query { viewer { login }}"
}
' https://api.github.com/graphql
```

## Queries

query如下：

```
{
  viewer {
    login
    bio
    organizations(first: 3) {
      edges {
        org:node {
          name
        }
      }
    }
  }
}
```

返回结果样例：

```json
{
  "data": {
    "viewer": {
      "login": "gjtorikian",
      "bio": "I inhale and exhale.",
      "organizations": {
        "edges": [
          {
            "org": {
              "name": "GitHub"
            }
          },
          {
            "org": {
              "name": "Atom"
            }
          },
          {
            "org": {
              "name": "octokit"
            }
          }
        ]
      }
    }
  }
}
```

### Connections

#### Search

参数   | 类型       | 说明
---    | ----       | -----
first  | Int        | 返回最前面的n个元素
last   | Int        | 返回最后的n个元素
after  | String     | 返回指定ID后面的元素
before | String     | 返回指定ID前面的元素
query  | String     | 查询字符串
type   | SearchType | 搜索类型

### Fields

#### Node

参数 | 类型 | 说明
---  | ---- | -----
id   | ID   |

#### Nodes

参数 | 类型 | 说明
---  | ---- | -----
ids  | List | ID列表

#### repositoryOwner

查找一个项目的Owner（一个用户或者组织）

参数  | 类型   | 说明
---   | ----   | -----
login | String |

#### viewer

当前登陆的用户

## Mutations

对应着增删改操作，这里只使用project为例：

### createProject

Creates a new project.

Input fields

- clientMutationId (String):  A unique identifier for the client performing the mutation.
- subjectId (ID): The Node ID of the subject to modify.
- body (String): The contents of the comment.

Return fields

- clientMutationId (String): A unique identifier for the client performing the mutation.
- project (Project): The new project.

### updateProject

Updates an existing project.

Input fields

- clientMutationId (String): A unique identifier for the client performing the mutation.
- subjectId (ID): The Node ID of the subject to modify.
- body (String): The contents of the comment.

Return fields

- clientMutationId (String): A unique identifier for the client performing the mutation.
- project (Project): The updated project.

### deleteProject

Deletes a project.

Input fields

- clientMutationId (String): A unique identifier for the client performing the mutation.
- subjectId (ID): The Node ID of the subject to modify.
- body (String): The contents of the comment.

Return fields

- clientMutationId (String): A unique identifier for the client performing the mutation.
- owner (ProjectOwner): The repository the project was removed from.


---------

Date: 2016-09-28  Author: alex cai <cyy0523xc@gmail.com>
