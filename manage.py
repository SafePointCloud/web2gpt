#!/usr/bin/env python3

import argparse
import base64
import json
import shutil
import ssl
import sys
import datetime
import platform
import os
from urllib.request import urlopen, HTTPError
import re
import subprocess
import string
import time
import random
import socket


QRCODE = """
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
██ ▄▄▄▄▄ █▀█ █▄█▀▀▄█ ▄▄▄▀▄██ ▄▄▄▄▄ ██
██ █   █ █▀▀▀█ ▀▀▄▄▄▄▄▀▄  ▀█ █   █ ██
██ █▄▄▄█ █▀ █▀▀ █▄▄▄▄▄▄▀▀▄▄█ █▄▄▄█ ██
██▄▄▄▄▄▄▄█▄▀ ▀▄█▄▀▄█ █▄▀ █▄█▄▄▄▄▄▄▄██
██ ▄ ▄▄█▄▄▄▄▀▄▀▀██▀ ▀▀ ▀█ ▄▄▀▄█▄▀ ▀██
██ ▄ ▄██▄█ █▄█▀ ▄▄▀█ ▀▀ █▀█▀▄██▄▀▄███
███▀▄▄▄█▄▀  ▄█▄█▄█▀▄█▀▀▄█ ▄ ▀▄▄▄█▀▀██
██▀▀█▄  ▄▄ █▄ ▄█▀ ▀▄ █▀  ▀▀█▄█▄█▀▄███
██▀ █ ▄▀▄███ ▄▀▀▀▀▀▄▀█▀▀▄▀▄▄▀█▄▀█ ▀██
██▀███ ▄▄▄█ ██▀ ▄██▀▀▄▀▀█▀▄▀▄▄ ▄▀▄███
██ ▄█▀██▄▀█▀▀█▄█▄▀▀▀▀ █ █  ▄▀ ▄▀█ ▀██
██ █ ▀▄█▄▀▄ ▄ ▄█▀▀██ ██  █▀▄ ▀  ▀▄███
██▄█▄██▄▄█▀█ ▄▀▀▀▄▀▄▀▄█ ▀▀ ▄▄▄  ▀█ ██
██ ▄▄▄▄▄ █▄ ██▀ ▄▄▀▄▀█▀▀   █▄█  ▀ ███
██ █   █ █  ▄█▄█▄█▀▄██ ██▀ ▄▄  ▀█ ▄██
██ █▄▄▄█ █ ▀█ ▄█▀▄█▀ ▀ ▄█▀▄▀ ▀▀ ▀████
██▄▄▄▄▄▄▄█▄█▄▄███▄████▄█▄▄▄█▄▄█▄█▄███

微信扫描上方二维码加入雷池项目讨论组
"""



BOLD    = 1
DIM     = 1
BLINK   = 5
REVERSE = 7
RED     = 31
GREEN   = 32
YELLOW  = 33
BLUE    = 34
CYAN    = 36


class log():
    @staticmethod
    def _log(c, l, s):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        print('\r\033[0;%dm[%-5s %s]: %s\033[0m' % (c, l, t, s))

    @staticmethod
    def debug(s):
        if os.getenv('DEBUG'):
            log._log(DIM, 'DEBUG', s)

    @staticmethod
    def info(s):
        log._log(CYAN, 'INFO', s)

    @staticmethod
    def warning(s):
        log._log(YELLOW, 'WARN', s)

    @staticmethod
    def error(s):
        log._log(RED, 'ERROR', s)

    @staticmethod
    def fatal(s):
        log._log(RED, 'ERROR', s)
        sys.exit(1)

def color(t, attrs=[], end=True):
    t = '\x1B[%sm%s' % (';'.join([str(i) for i in attrs]), t)
    if end:
        t = t + '\x1B[m'
    return t

def banner():
    t = r'''
  ______               ___           _____       _                        ____      ____       _        ________
.' ____ \            .' ..]         |_   _|     (_)                      |_  _|    |_  _|     / \      |_   __  |
| (___ \_|  ,--.    _| |_    .---.    | |       __    _ .--.    .---.      \ \  /\  / /      / _ \       | |_ \_|
 _.____`.  `'_\ :  '-| |-'  / /__\\   | |   _  [  |  [ `.-. |  / /__\\      \ \/  \/ /      / ___ \      |  _|
| \____) | // | |,   | |    | \__.,  _| |__/ |  | |   | | | |  | \__.,       \  /\  /     _/ /   \ \_   _| |_
 \______.' \'-;__/  [___]    '.__.' |________| [___] [___||__]  '.__.'        \/  \/     |____| |____| |_____|

'''.strip('\n')
    print(color(t + '\n', [GREEN, BLINK]))

def get_url(url):
    try:
        request_ctx = ssl.create_default_context()
        request_ctx.check_hostname = False
        request_ctx.verify_mode = ssl.CERT_NONE
        response = urlopen(url, timeout=10, context=request_ctx)
        content = response.read()
        return content.decode('utf-8')
    except Exception as e:
        log.error('get url %s failed: %s' % (url, str(e)))

def ui_read(question, default):
    while True:
        if default is None:
            sys.stdout.write('%s: ' % (
                color(question, [GREEN]),
            ))
        else:
            sys.stdout.write('%s  %s: ' % (
                color(question, [GREEN]),
                color('留空则为默认值 %s' % default, [YELLOW]),
                ))
        r = input().strip()
        if len(r) == 0:
            if default is None or len(default) == 0:
                continue
            r = default
        return r

def ui_choice(question, options):
    while True:
        s_options = '[ %s ]' % '  '.join(['%s.%s' % option for option in options])
        s_choices = '(%s)' % '/'.join([option[0] for option in options])
        sys.stdout.write('%s  %s  %s: ' % (color(question, [GREEN]), color(s_options, [YELLOW]), color(s_choices, [YELLOW])))
        r = input().strip()
        if r in [i[0] for i in options]:
            return r

def humen_size(x):
    if x >= 1024 * 1024 * 1024 * 1024:
        return '%.02f TB' % (x / 1024 / 1024 / 1024 / 1024)
    elif x >= 1024 * 1024 * 1024:
        return '%.02f GB' % (x / 1024 / 1024 / 1024)
    elif x >= 1024 * 1024:
        return '%.02f MB' % (x / 1024 / 1024)
    elif x >= 1024:
        return '%.02f KB' % (x / 1024)
    else:
        return '%d Bytes'

def free_space(path):
    while not os.path.exists(path) and path != '/':
        path = os.path.dirname(path)
    try:
        st = os.statvfs(path)
        free_bytes = st.f_bavail * st.f_frsize
        return free_bytes
    except Exception as e:
        log.error('获取空间失败: ' + str(e))
        return None

def free_memory():
    t = filter(lambda x: 'MemAvailable' in x, open('/proc/meminfo', 'r').readlines())
    return int(next(t).split()[1]) * 1024

def exec_command(*args,shell=False):
    try:
        proc = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,shell=shell)
        subprocess_output(proc.stdout.strip())
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return -1, '', str(e)

def exec_command_with_loading(*args, cwd=None, env=None):
    try:
        with subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env, cwd=cwd) as proc:
            loading = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
            iloading = 0
            while proc.poll() is None:
                sys.stderr.write('\r' + loading[iloading])
                sys.stderr.flush()
                iloading = (iloading + 1) % len(loading)
                time.sleep(0.1)
            sys.stderr.write('\r')
            sys.stderr.flush()
            return proc.returncode, proc.stdout.read(), proc.stderr.read()
    except Exception as e:
        return -1, '', str(e)

def get_docker_compose():
    code, _, _ = exec_command('docker', 'compose', 'version')
    if code == 0:
        return ['docker', 'compose']
    code, _, _ = exec_command('docker-compose', 'version')
    if code == 0:
        return ['docker-compose']
    return None
    

def install():
    log.info('准备安装 Web2GPT')

    docker_compose = get_docker_compose()
    if docker_compose is None:
        log.error('未找到 docker-compose 命令')
        return

    default_path = '/data/web2gpt'

    while True:
        path = ui_read('请输入 Web2GPT 的安装目录', default_path)
        if os.path.exists(path):
            log.warning('安装目录已存在')
            continue
        if free_space(path) < 10 * 1024 * 1024 * 1024:
            log.warning('磁盘空间不足')
            continue
        break

    try:
        os.makedirs(path)
    except Exception as e:
        log.error('创建目录失败')
        return

    log.info('剩余磁盘容量: %s' % humen_size(free_space(path)))

    log.info('下载 compose 文件')
    if not save_file_from_url('https://release.web2gpt.ai/latest/docker-compose.yml', os.path.join(path, 'docker-compose.yml')):
        log.error('下载 compose 文件失败')
        return
    rename_file(os.path.join(path, 'docker-compose.yml'), os.path.join(path, 'docker-compose.yml.bak'))

    

    log.info('安装完成')

def get_installed_dir():
    path = ''
    path_proc = exec_command('docker','inspect','--format','\'{{index .Config.Labels "com.docker.compose.project.working_dir"}}\'', 'turing-api')
    if path_proc[0] == 0:
        path = path_proc[1].strip().replace("'",'')
    else:
        log.debug("get installed dir error: " + path_proc[2])
    log.debug('find Web2GPT installed in "%s"' % path)
    if path == '' or not os.path.exists(path):
        log.warning('未能找到安装目录')
        return ui_read('请输入 Web2GPT 的安装目录',None)

    return path

def save_file_from_url(url, path):
    log.debug('saving '+url+' to '+path)
    data = get_url(url)
    if data is None:
        return False
    with open(path, 'w') as f:
        f.write(data)
    return True

def rename_file(src, dst):
    if os.path.exists(src):
        os.rename(src, dst)

def remove_file(src):
    if os.path.exists(src):
        os.remove(src)

def upgrade():
    path = get_installed_dir()

    if not precheck_docker_compose():
        log.error('当前环境不符合 Web2GPT 的安装条件')
        return

    log.info('下载 compose 文件')
    rename_file(os.path.join(path, 'docker-compose.yml'), os.path.join(path, 'docker-compose.yml.bak'))
    if not save_file_from_url('https://release.web2gpt.ai/latest/docker-compose.yml', os.path.join(path, 'docker-compose.yml')):
        log.error('下载 compose 文件失败')
        return

    log.info('升级完成')


def docker_restart_all(cwd):
    if not docker_down(cwd):
        log.error('停止 docker 容器失败')
        return False

    if not docker_up(cwd):
        log.error('启动 docker 容器失败'))
        return False

    return True


def restart():
    path = get_installed_dir()

    if not precheck_docker_compose():
        log.error('当前环境不符合 Web2GPT 的安装条件')
        return

    if not docker_restart_all(path):
        return

    log.info('重启完成')

def uninstall():
    path = get_installed_dir()

    action = ui_choice('是否确认卸载 Web2GPT, 该操作会删除目录下所有数据: %s' % path,[
        ('y', '是'),
        ('n', '否'),
    ])

    if action == 'n':
        return

    if not precheck_docker_compose():
        log.error('当前环境不符合 Web2GPT 的安装条件')
        return

    if not docker_down(path):
        log.error('无法停止 Web2GPT')
        return

    try:
        shutil.rmtree(path)
    except Exception as e:
        log.debug("remove dir failed: " + str(e))
        log.error('无法删除 Web2GPT 目录')

    log.info('卸载完成')


def main():
    banner()
    log.info(text('hello1'))
    log.info(text('hello2'))
    print()

    if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor <= 5):
        log.error('Python 版本过低, 脚本无法运行, 需要 Python 3.5 以上')
        return

    if not sys.stdin.isatty():
        log.error('运行脚本的方式不对, STDIN 不是标准的 TTY')
        return

    if os.geteuid() != 0:
        log.error('Web2GPT 需要 root 权限才能运行')
        return

    if platform.system() != 'Linux':
        log.error('Web2GPT 暂时不支持 %s 操作系统' % platform.system())
        return

    if platform.machine() not in ('x86_64', 'AMD64'):
        log.error('Web2GPT 暂时不支持 %s 处理器' % platform.machine())
        return


    action = ui_choice('选择你要执行的动作', [
        ('1', '安装'),
        ('2', '升级'),
        ('3', '卸载'),
        ('4', '重启'),
    ])

    if action == '1':
        install()
    elif action == '2':
        upgrade()
    elif action == '3':
        uninstall()
    elif action == '4':
        restart()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.warning('取消安装')
    except Exception as e:
        log.error(e)
    finally:
        print(color(QRCODE + '\n', [GREEN]))