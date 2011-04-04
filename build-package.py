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

# USAGE:
#  buildall.py
#  buildall.py all build
#  buildall.py hello-world bump upload repo

import os
import re
import imp
import sys
import time
import subprocess

import config

BASEDIR = os.path.dirname (os.path.realpath (__file__))
EXCLUDES = [r'common', r'download-cache', r'\.git', r'build.py.*', r'.*\.pkg']

EXIT_ERROR = 1
EXIT_OK    = 0

def get_package_list():
    packages = []

    for f in os.listdir (BASEDIR):
        fp = os.path.join (BASEDIR, f)

        if True in [bool(re.match (exclude, f)) for exclude in EXCLUDES]:
            continue

        if not os.path.isdir (fp):
            continue

        packages.append (f)

    return packages

def parse_argv():
    if len(sys.argv) < 2:
        packages = ["all"]
        ops      = ["build"]
    elif len(sys.argv) < 3:
        packages = [sys.argv[1]]
        ops      = ["build"]
    else:
        packages = [sys.argv[1]]
        ops      = sys.argv[2:]

    if len(packages) == 1 and packages[0] == "all":
        packages = get_package_list()

    return ops, packages

def run (package, command, want='output', print_stdout=False):
    fp = os.path.join (BASEDIR, package)

    print command
    p = subprocess.Popen (command, cwd=fp, shell=True, stdout=subprocess.PIPE, close_fds=True)
    output = p.stdout.read()
    p.stdout.close()
    retcode = p.wait()

    if print_stdout:
        print output

    if want == 'output':
        return output
    return retcode

def compile_py (package, file, debug=False):
    if debug:
        return file

    # Compile
    run (package, "python -O -c \"import py_compile; py_compile.compile('%s')\"" %(file))
    return file.replace ('.py', '.pyo')

def op_clean (pkg_build, package, pkg_name, debug):
    # Basic cleaning
    run (package, 'rm -f *~ *.pyc *.pyo %s'%(pkg_name))
    if pkg_build.__dict__.has_key('build'):
        pkg_build.build (op, *args)

    # Clean unpacked dirs as well
    if pkg_build.__dict__.has_key('DOWNLOADS'):
        for down_entry in pkg_build.DOWNLOADS:
            rm_target = down_entry.get('dir')

            # If no dir specified, try to remove lingering copied files
            if not rm_target:
                rm_target = down_entry.get('copy')
                if rm_target == '.':
                    rm_target = down_entry.get('url','').split('/')[-1]

            run (package, "rm -rf '%s'" %(rm_target))

def op_mrproper (pkg_build, package, pkg_name, debug):
    # Remove cached file
    if pkg_build.__dict__.has_key('DOWNLOADS'):
        for down_entry in pkg_build.DOWNLOADS:
            rm_target = down_entry.get('url','').split('/')[-1]
            if rm_target:
                run ("download-cache", "rm -rf '%s'" %(rm_target))

def op_bump (pkg_dsc, package, pkg_name, debug):
    # Bump 'revision'
    build_fp = os.path.join (BASEDIR, package, 'build.py')
    build = open(build_fp, 'r').read()

    package_version = re.findall (r"REVISION\s*=\s*(\d+)", build, re.MULTILINE)[0]
    package_version_new = str(int(package_version)+1)

    build_new = re.sub (r"(\s*)REVISION(\s*)=(\s*)\d+", r"\1REVISION\2=\3{new}", build)
    build_new = build_new.replace ('{new}', package_version_new)

    print "Bumped to %s" %(package_version_new)

    # Write it
    f = open (build_fp, 'w+')
    f.write (build_new)
    f.close()

def op_upload (pkg_build, package, pkg_name, debug):
    # Package ID
    build_fp = os.path.join (BASEDIR, package, 'description.py')
    build = open(build_fp, 'r').read()
    app_name = re.findall (r"'id'\s*:\s*['\"](.+)['\"]", build, re.MULTILINE)[0]

    # Copy it
    run (package, "ssh %s mkdir -p %s/%s" %(config.PKGS_HOST, config.PKGS_DIR, app_name))
    run (package, "scp '%s' %s:%s/%s/" %(pkg_name, config.PKGS_HOST, config.PKGS_DIR, app_name))
    run (package, "ssh %s chmod g+w %s/%s/%s" %(config.PKGS_HOST, config.PKGS_DIR, app_name, pkg_name))

def op_repo (pkg_build, package, pkg_name, debug):
    # Source
    package_fp = os.path.join (BASEDIR, package, pkg_name)

    # Target
    target_fp = os.path.join (config.LOCAL_REPO_PATH, package)
    target_file_fp = os.path.join (config.LOCAL_REPO_PATH, package, pkg_name)

    # Copy
    if not os.path.exists (target_fp):
        os.makedirs (target_fp)

    # Is it actually neccesary to copy the file?
    do_copy = True
    if os.path.exists (target_file_fp):
        package_info     = os.stat (package_fp)
        target_file_info = os.stat (target_file_fp)

        # Skip if the local package is not newer
        if target_file_info.st_mtime >= package_info.st_mtime:
            do_copy = False

        # It can't be in the future though
        if target_file_info.st_mtime > time.time():
            do_copy = True

    if do_copy:
        run (package, "cp '%s' '%s'" %(package_fp, target_file_fp))
    else:
        print "%s skipping copy to repository" %(pkg_name)


def op_build (pkg_build, package, pkg_name, debug):
    # Has something changed?
    package_fp = os.path.join (BASEDIR, package, pkg_name)
    if os.path.exists (package_fp):
        all_files = ['build.py']
        for p in ['PY_DEPS', 'PY_FILES', 'INCLUDE']:
            if pkg_build.__dict__.has_key(p):
                all_files += pkg_build.__dict__[p]

        for p in pkg_build.__dict__.get('DOWNLOADS',[]):
            if p.has_key('skip_if'):
                all_files.append (p['skip_if'])
            if p.has_key('patches'):
                all_files += [p[0] for p in p['patches']]

        package_stat = os.stat (package_fp)
        something_to_do = False
        for f in all_files:
            fp = os.path.join (BASEDIR, package, f)
            if not os.path.exists (fp):
                something_to_do = True
            else:
                if os.stat(fp).st_mtime > package_stat.st_mtime:
                    something_to_do = True

        if not something_to_do:
            print "%s is up to date." %(pkg_name)
            return

    # Detect a new/modified patches
    new_patch=False

    for d in pkg_build.__dict__.get('DOWNLOADS',[]):
        for patch_entry in d.get('patches',[]):
            patch_file, patch_params = patch_entry

            patch_fp   = os.path.join (BASEDIR, package, patch_file)
            patch_stat = os.stat (patch_fp)

            for d in pkg_build.__dict__.get('INCLUDE',[]):
                fp = os.path.join (BASEDIR, package, d)
                if not os.path.exists (fp):
                    continue

                fp_stat = os.stat (fp)

                if ((patch_stat.st_mtime > fp_stat.st_mtime) or
                    (patch_stat.st_mtime > fp_stat.st_ctime)):
                    print "WARNING: Path is newer than include: %s > %s." %(patch_file, d)
                    new_patch = True

    if new_patch:
        # Force a 'mrproper' to remove src dirs and rebuild everything
        print "* Invoking: mrproper"
        op_clean (pkg_build, package, pkg_name, debug)

    # Copy dependencies
    py_files = pkg_build.PY_FILES[:]

    if pkg_build.__dict__.has_key('PY_DEPS'):
        for dep in pkg_build.PY_DEPS:
            run (package, 'cp %s .' %(dep))
            py_files.append (os.path.basename(dep))

    # Download
    if pkg_build.__dict__.has_key('download'):
        pkg_build.download()
    else:
        if pkg_build.__dict__.has_key('DOWNLOADS'):
            for down_entry in pkg_build.DOWNLOADS:
                download_dir     = down_entry.get('dir','')
                download_url     = down_entry.get('url')
                download_copy    = down_entry.get('copy')
                download_patches = down_entry.get('patches')

                # Pre-requisite
                cache_dir = os.path.join (BASEDIR, 'download-cache')
                if not os.path.exists (cache_dir):
                    os.makedirs (cache_dir)

                # Download
                file_download = download_url.split('/')[-1]
                file_in_cache = os.path.join (BASEDIR, 'download-cache', file_download)
                if not os.path.exists (file_in_cache):
                    run ("download-cache", "wget -O '%s' '%s'" %(file_in_cache, download_url))
                else:
                    print "Skipping download of", download_url

                # Unpack
                is_fenced       = down_entry.get('fence')
                skip_if_present = down_entry.get('skip_if')
                moves           = down_entry.get('mv', ())

                download_dir_fp = os.path.join (BASEDIR, package, download_dir)
                if download_dir and (not os.path.exists (download_dir_fp)) or skip_if_present:
                    # Target unpack dir
                    if is_fenced:
                        target_dir  = os.path.join (package, download_dir)
                        package_dir = target_dir
                        run (package, "mkdir -p '%s'" %(download_dir))
                    else:
                        target_dir  = package
                        package_dir = os.path.join (target_dir, download_dir)

                    # Skip if present
                    if skip_if_present:
                        skip_fp = os.path.join (package, skip_if_present)
                        if os.path.exists (skip_fp):
                            continue

                    if '.tar.gz' in download_url or '.tgz' in download_url:
                        cmd = "tar xfvz '%s'" %(os.path.join (BASEDIR, "download-cache", file_download))
                        run (target_dir, cmd)
                    elif '.tar.bz2' in download_url:
                        cmd = "tar xfvj '%s'" %(os.path.join (BASEDIR, "download-cache", file_download))
                        run (target_dir, cmd)
                    elif '.zip' in download_url:
                        cmd = "unzip -o '%s'" %(os.path.join (BASEDIR, "download-cache", file_download))
                        run (target_dir, cmd)
                    else:
                        cmd = "cp '%s' ." %(os.path.join (BASEDIR, "download-cache", file_download))
                        run (target_dir, cmd)

                    # Renames
                    for mv in moves:
                        dir_orig   = os.path.join (BASEDIR, package, mv[0])
                        dir_target = os.path.join (BASEDIR, package, mv[1])

                        print "dir_orig, dir_target", dir_orig, dir_target
                        os.rename (dir_orig, dir_target)

                    # Apply patches
                    for path_entry in download_patches or []:
                        patch_file, patch_params = path_entry
                        patch_fp = os.path.join (BASEDIR, package, patch_file)

                        if download_dir:
                            apply_cwd = os.path.join (package, download_dir)
                        else:
                            apply_cwd = package

                        ret = run (apply_cwd, "patch --verbose %s < '%s'" %(patch_params, patch_fp), print_stdout=True, want='retcode')
                        if ret != 0:
                            print "ERROR: Could not apply '%s'" %(patch_fp)
                            print
                            op_clean (pkg_build, package, pkg_name, debug)
                            print "Try again."
                            print
                            sys.exit (EXIT_ERROR)

                elif download_copy:
                    run ("download-cache", "cp '%s' '%s'" %(file_download, os.path.join (BASEDIR, package, download_copy)))

    # All
    if pkg_build.__dict__.has_key('all'):
        pkg_build.all (op, *args)
    else:
        files = ['description.py']

        # Build the package
        for py_file in py_files:
            files.append (compile_py (package, py_file, debug=debug))

        # Generic includes
        if pkg_build.__dict__.has_key('INCLUDE'):
            files += pkg_build.INCLUDE

        # Check local files and emit warning
        for f in os.listdir (os.path.join (BASEDIR, package)):
            fp = os.path.join (BASEDIR, f)

            if True in [bool(re.match (exclude, f)) for exclude in EXCLUDES]:
                continue

            if f in py_files:
                continue

            if not f in files and not f.endswith('~'):
                print "WARNING: %s not being included in the package" %(f)

        # Pack
        run (package, "tar cfz %s %s %s" %(pkg_name, config.TAR_PARMS, ' '.join (files)))

        # Clean up
        if pkg_build.__dict__.has_key('PY_DEPS'):
            for dep in pkg_build.PY_DEPS:
                local_py = os.path.basename (dep)
                run (package, "rm -f '%s'" %(local_py))


def dispatch (package, op):
    # Load the definition file
    fp = os.path.join (BASEDIR, package, "build.py")
    pkg_build = imp.load_source ("package-%s"%(package), fp)

    # Load the package description file
    fp = os.path.join (BASEDIR, package, "description.py")
    pkg_dsc = imp.load_source ("package-%s"%(package), fp)

    # Package nameS=
    pkg_file = "%s-%s_%s.%s" %(pkg_dsc.software['id'],
                               pkg_dsc.software['version'],
                               pkg_build.REVISION,
                               config.PACKAGE_EXT)

    # Debug
    debug = config.DEBUG
    if pkg_build.__dict__.has_key('DEBUG'):
        debug = debug and pkg_build.DEBUG

    # Execute
    if op == 'clean':
        op_clean  (pkg_build, package, pkg_file, debug)
    elif op == 'mrproper':
        op_clean    (pkg_build, package, pkg_file, debug)
        op_mrproper (pkg_build, package, pkg_file, debug)
    elif op == 'bump':
        op_bump   (pkg_dsc, package, pkg_file, debug)
    elif op == 'build':
        op_build  (pkg_build, package, pkg_file, debug)
    elif op == 'repo':
        op_build  (pkg_build, package, pkg_file, debug)
        op_repo   (pkg_build, package, pkg_file, debug)
    elif op == 'upload':
        op_build  (pkg_build, package, pkg_file, debug)
        op_upload (pkg_build, package, pkg_file, debug)
    elif op == 'all':
        op_clean  (pkg_build, package, pkg_file, debug)
        op_bump   (pkg_dsc,   package, pkg_file, debug)
        op_build  (pkg_build, package, pkg_file, debug)
        op_repo   (pkg_build, package, pkg_file, debug)
        op_upload (pkg_build, package, pkg_file, debug)


def main():
    packages = get_package_list()
    ops, packages = parse_argv()

    for pkg in packages:
        if not os.path.exists (pkg):
            print "ERROR: Package does not exist: %s" %(pkg)
            sys.exit (EXIT_ERROR)

        for op in ops:
            print "- %s: %s" %(pkg, op)
            dispatch (pkg, op)


if __name__ == "__main__":
    main()
