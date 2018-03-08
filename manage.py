from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from FlaskDemo import app
from exts import db
from models import User
from models import Question
from models import Answer

# 使用migrate绑定db和app
migrate = Migrate(app=app,db=db)

# 添加迁移脚本命令到manager
manager = Manager(app=app)
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()

