# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand

from flaskcities.app import create_app

app = create_app()
manager = Manager(app)


def _make_context():
    return {'app': app}

manager.add_command("server", Server(host="0.0.0.0", port=5000))
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()