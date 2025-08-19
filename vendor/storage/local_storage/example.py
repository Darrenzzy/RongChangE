#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------

@file: example.py

@author: 'ovan'

@mtime: '2023/5/24'

@desc:

    
    `````````````````````````````````
    

---------------------------------------------------
"""

# from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings

if __name__ == '__main__':
    location = settings.BASE_DIR / "media/import/upload"
    if not location.exists():
        location.mkdir(parents=True)

    fs = FileSystemStorage(location=location)
    name = "None.txt"
    filename = fs.save(
        name, ContentFile(b'we have a beat one ~')
    )

    print(fs.path(filename))
