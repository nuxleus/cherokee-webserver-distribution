#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
# Cherokee Distribution
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2011 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import os
import sys
import imp
import gzip
import time
import pprint
import config

from util import *

# Globals
packages = []
dest_dir = ''

PACKAGE_PROPS = ('software', 'installation', 'maintainer')


def figure_package_list():
    pkgs = []

    for f in os.listdir('.'):
        if not os.path.isdir (f):
            continue

        dsc_fp = os.path.join (f, 'description.py')
        if os.path.exists (dsc_fp):
            pkgs.append (f)

    return pkgs


def initial_sanity_checks ():
    errors = False

    for pkg in packages:
        dsc_fp = os.path.join (pkg, 'description.py')
        dsc    = imp.load_source (pkg, dsc_fp)
        pkg_id = dsc.software.get('id')

        for prop in ('id', 'name', 'version', 'icon_small', 'icon_big', 'score', 'desc_short', 'desc_long', 'category'):
            if not dsc.software.get(prop):
                print "ERROR: Package %s does not have an '%s' property" %(pkg, prop)
                errors = True
                continue

        if dsc.software['id'] != pkg:
            print "ERROR: Package %s has a %s ID" %(pkg, dsc.software['id'])
            errors = True

    if errors:
        raise SystemExit


def build_packages():
    for pkg in packages:
        # Rebuild the package if neccessary
        cmd = "./build-package.py %s" %(pkg)
        ret = run (cmd, want='retcode')
        if ret != 0:
            raise SystemExit


def build_index_file():
    package_list = {}
    for package in packages:
        build_fp = os.path.join (package, 'build.py')
        dsc_fp   = os.path.join (package, 'description.py')

        # Import package description files
        dsc   = imp.load_source (package, dsc_fp)
        build = imp.load_source (package, build_fp)

        # Read its properties
        package_info = {}
        for k in PACKAGE_PROPS:
            package_info[k] = dsc.__dict__[k]

        # Generate package information
        filename = "%s-%s_%s.%s" %(dsc.software['id'],
                                   dsc.software['version'],
                                   build.REVISION,
                                   config.PACKAGE_EXT)

        pkg_fp = os.path.join (package, filename)
        pkg_stat = os.stat (pkg_fp)
        pkg_date = time.strftime ("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(pkg_stat.st_ctime))

        package_info['package'] = {'filename':   filename,
                                   'revision':   build.REVISION,
                                   'build_date': pkg_date}

        # Add it the the general list
        package_list[package] = package_info

    index = {
        'packages':      package_list,
        'build_date':    time.strftime ("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
        'featured_apps': ('redmine', 'drupal7', 'phpmyadmin', 'trac', 'wordpress'), # TMP
        'top_apps':      ('drupal', 'drupal7', 'joomla', 'trac', 'vanilla', 'phpbb', 'moodle', 'mediawiki', 'silverstripe', 'statusnet', 'sugar_ce'), #TMP
    }

    # Render the package directory
    render = pprint.pformat (index)

    # Write it down
    index_fp = os.path.join (dest_dir, 'index.py.gz')

    print "Writing %s" %(index_fp)
    f = gzip.open (index_fp, 'wb+', 9)
    f.write (render)
    f.close()


def create_dest_dirs():
    for pkg in packages:
        dest_fp = os.path.join (dest_dir, pkg)
        if not os.path.exists (dest_fp):
            print "Creating %s" %(dest_fp)
            os.makedirs (dest_fp)

        for subdir in ('screenshots', 'icons'):
            fp = os.path.join (dest_fp, subdir)
            if not os.path.exists (fp):
                print "Creating %s" %(fp)
                os.makedirs (fp)


def copy_package_resources():
    for pkg in packages:
        icons_fp       = os.path.join (dest_dir, pkg, 'icons')
        screenshots_fp = os.path.join (dest_dir, pkg, 'screenshots')

        dsc_fp  = os.path.join (pkg, 'description.py')
        dsc = imp.load_source (pkg, dsc_fp)

        # Screenshots
        for screenshot in dsc.software['screenshots']:
            origin = os.path.join (pkg, 'screenshots', screenshot)
            target = os.path.join (screenshots_fp, screenshot)

            ret = cp (origin, target)
            if ret != 0:
                raise SystemExit

        # Icons
        for icon_type in ('icon_small', 'icon_big'):
            origin = os.path.join (pkg, 'icons', dsc.software[icon_type])
            target = os.path.join (icons_fp, dsc.software[icon_type])

            ret = cp (origin, target)
            if ret != 0:
                raise SystemExit


def copy_packages():
    for pkg in packages:
        dsc_fp = os.path.join (pkg, 'description.py')
        dsc    = imp.load_source (pkg, dsc_fp)

        build_fp = os.path.join (pkg, 'build.py')
        build    = imp.load_source (pkg, build_fp)

        package_filename = '%s-%s_%s.pkg' %(dsc.software['id'], dsc.software['version'], build.REVISION)
        package_origin_fp = os.path.join (pkg, package_filename)
        package_target_fp = os.path.join (dest_dir, pkg, package_filename)

        # Copy it to the package repository
        ret = cp (package_origin_fp, package_target_fp)
        if ret != 0:
            raise SystemExit


def main():
    global packages

    # Figure the package list
    packages = figure_package_list()

    # Sanity checks
    initial_sanity_checks()

    # Build all packages
    build_packages()

    # Build index
    build_index_file()

    # Destination dirs
    create_dest_dirs()

    # Copy images
    copy_package_resources()

    # Copy packages
    copy_packages()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "%s /destination/path" %(sys.argv[0])
        raise SystemExit

    # Destination dir
    dest_dir = sys.argv[1]

    if not os.path.exists (dest_dir):
        os.makedirs (dest_dir)

    # Build the repository
    main()
