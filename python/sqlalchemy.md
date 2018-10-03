# Flask SQLAlchemy的使用

```python
from json import loads as json_loads
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model_flow.settings import DBConfig, JobStatus, DoStatus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DBConfig.URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
tb_prefix = DBConfig.TB_PREFIX


class JobInfo(db.Model):
    """作业基本信息表"""
    __tablename__ = tb_prefix + 'job_info'

    job_id = db.Column(db.CHAR(16), primary_key=True, comment='唯一ID')
    user_id = db.Column(db.CHAR(16), nullable=False, index=True, comment='用户ID')
    task_id = db.Column(db.CHAR(16), nullable=False, index=True, comment='任务ID')
    node_id = db.Column(db.CHAR(16), nullable=False, index=True, comment='节点ID')
    algo_type = db.Column(db.String(20), index=True, comment='算法名称')
    algo_name = db.Column(db.String(20), index=True, comment='算法名称')
    features = db.Column(db.String(1023), nullable=False, comment='特征字段名列表，英文逗号分隔')
    target = db.Column(db.String(50), index=True, comment='目标字段名列表，英文逗号分隔')
    status = db.Column(db.Enum(JobStatus), default=JobStatus.INIT, comment='作业状态')
    train_status = db.Column(db.Enum(DoStatus), default=DoStatus.INIT, comment='训练进度状态')
    test_status = db.Column(db.Enum(DoStatus), default=DoStatus.INIT, comment='测试进度状态')
    dataset_conf = db.Column(db.String(1023), comment='数据配置, json格式')
    train_begin = db.Column(db.DateTime, comment='训练开始时间')
    train_end = db.Column(db.DateTime, comment='训练结束时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    def to_dict(self):
        row = {
            'job_id': self.job_id,
            'algo_name': self.algo_name,
            'features': self.features,
            'target': self.target,
            'status': self.status.name,
            'train_status': self.train_status.name,
            'test_status': self.test_status.name,
            'dataset_conf': json_loads(self.dataset_conf),
            'created_at': self.created_at.strftime(DBConfig.DATETIME_FORMAT),
            'updated_at': self.updated_at.strftime(DBConfig.DATETIME_FORMAT),
        }
        if self.train_begin is not None:
            row['train_begin'] = self.train_begin.strftime(DBConfig.DATETIME_FORMAT)
        if self.train_end is not None:
            row['train_end'] = self.train_end.strftime(DBConfig.DATETIME_FORMAT)

        return row


class Metric(db.Model):
    """模型评估指标记录表"""
    __tablename__ = tb_prefix + 'metric'
    __table_args__ = (db.PrimaryKeyConstraint('job_id', 'key'), )

    job_id = db.Column(db.CHAR(16), db.ForeignKey(JobInfo.job_id), comment='job唯一ID')
    key = db.Column(db.String(20), nullable=False, comment='指标key')
    user_id = db.Column(db.CHAR(16), nullable=False, index=True, comment='用户ID')
    task_id = db.Column(db.CHAR(16), nullable=False, comment='任务ID')
    node_id = db.Column(db.CHAR(16), nullable=False, comment='节点ID')
    value = db.Column(db.Float, nullable=False, comment='指标value')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

# 增加索引
db.Index('ix_metric_task_key_val', Metric.task_id, Metric.key, Metric.value)
db.Index('ix_metric_node_key_val', Metric.node_id, Metric.key, Metric.value)
```


