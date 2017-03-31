# React与GraphQl的Demo（基于Apollo React和Apollo Client）
GraphQL的客户端有很多，FB官方就有Relay，不过Relay实现得比较复杂，直接使用有难度。而Apollo Client则是一个比较好的选择。

Apollo Client的介绍：

    Apollo Client is a fully-featured caching GraphQL client with integrations for React, Angular, etc. It allows you to easily build UI components that fetch data via GraphQL. To get the most value out of apollo-client you should use it with one of its view layer integrations.

Apollo Client是全功能的缓存GraphQL Client，可以集成到React，Angular等框架中。

## Demo

- 服务器端接口：https://github.com/cyy0523xc/go-graphql-weekly
- 客户端：https://github.com/cyy0523xc/react-graphql-apollo-demo

下面只介绍几个比较有特色的点：

## 更新操作之后刷新列表的数据

```javascript
const ADD_TASK_MUTATION = gql`mutation addTask($taskContent: String!) {
  createTask(content: $taskContent) {
    id
    content
    status
  }
}
`

const GET_TASKS_QUERY = gql`query getTasks($status: TaskStatus!) {
  taskList(status: $status) {
    id
    content
    status
  }
}`;

graphql(ADD_TASK_MUTATION, {
    options: () => ({
        // 刷新会产生网络请求
        /*refetchQueries: [ 
            {
                query: GET_TASKS_QUERY,
                variables: {
                    status: 'todo'
                }
            }
        ],*/

        // 减少一次网络请求
        update: (proxy, { data: { createTask } }) => {
            // readQuery从本地读取
            const queryData = proxy.readQuery(getTasksQuery('todo'));
            queryData.taskList.push(createTask);
            proxy.writeQuery(getTasksQuery('todo', queryData));
        },
    })
})(AddTask);
```

这里实现的功能是：添加一个任务操作之后主动刷新列表的数据。这里有两种方式：

- 第一种：主动请求新的数据`refetchQueries`
- 第二种：通过`readQuery`和`writeQuery`直接更新本地的缓存数据

第二种方式可以减少一次网络请求，但是本地的实现有点复杂，例如增加的话应该增加到列表的哪个位置，如果删除的话分页数据怎么处理等。

## 前置和后置中间件
使用中间件非常简单，只需要简单设置即可：

```javascript
import ApolloClient, { createNetworkInterface } from 'apollo-client';

import auth from "./middleware/auth";
import error from "./afterware/error";

export default (uri) => {
    const networkInterface = createNetworkInterface({uri: uri});

    // 设置中间件
    networkInterface.use([auth])
        .useAfter([error]);

    const client = new ApolloClient({
        networkInterface,
        dataIdFromObject: r => r.id,
    });
    return client
};
```

前置中间件：

```javascript
// middleware/auth.js
export default {
    applyMiddleware(req, next) {
        // 中间件，可以实现全局权限校验
        console.log("in auth middleware")
        console.log(req)
        if (!req.options.headers) {
            req.options.headers = {};  // Create the header object if needed.
        }

        // Send the login token in the Authorization header
        //req.options.headers.authorization = `Bearer ${TOKEN}`;
        next();
    }
}
```

后置中间件：

```javascript
// afterware/error.js
export default {
    applyAfterware({ response }, next) {
        console.log("in afterware")
        if (response.status !== 200) {
            console.log("error")
        }
        next();
    }
}
```



