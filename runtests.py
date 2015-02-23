# -*- encoding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, 'testing')


if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    sys.argv.insert(1, 'test')
    execute_from_command_line(sys.argv)
