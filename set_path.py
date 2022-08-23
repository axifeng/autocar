#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os


# 添加同一目录级下的所有文件夹作为目录
for file in os.listdir("./"):
    if re.match(r'[a-zA-Z]{2,20}$', file):
        sys.path.append(file)
