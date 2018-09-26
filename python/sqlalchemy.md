# Flask SQLAlchemy的使用

```python
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class RunStatus(Enum):
    SCHEDULED = 1 # Run is scheduled to run at a later time.
    RUNNING   = 2 # Run has been initiated.
    FINISHED  = 3 # Run has completed.


class RunInfo(db.Model):
    """运行日志表"""
    __table_name__ = 'run_info'
    __table_args__ = (db.Index('user_task', "user_id", "task_id"), )

    run_id = db.Column(db.Integer, autoincrement=True, primary_key=True, comment='运行唯一ID')
    user_id = db.Column(db.CHAR(16), nullable=False, comment='用户ID')
    task_id = db.Column(db.CHAR(16), nullable=False, comment='任务ID')
    algo_name = db.Column(db.String(60), nullable=False, comment='算法名称')
    status = db.Column(db.Enum(RunStatus), comment='运行状态')
    data_conf = db.Column(db.String(1023), comment='数据配置, json格式')
    start_et = db.Column(db.DateTime, comment='训练开始时间')
```


