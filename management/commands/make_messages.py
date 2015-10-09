"""
This command extends Django's builtin command makemessages with a monkey patch that handles
underi18n template files.

Given parameters -d <template dir(s)> and -e <template ext(s)>, it processes underi18n template files
matching those parameters and adds text marked for translation to the Django standard .po files.
Files outside of template dir(s) and ext(s) are passed to the original command for standard processing.

Code inspired by and borrowed from Mjumbe Poe's django-mustachejs GitHub project
(https://github.com/mjumbewu/django-mustachejs)

@author: Paul Elliott (PE)
@date: 10/8/2015
"""

from django.core.management.commands.makemessages import Command as BaseI18nCommand
from django.core.management.utils import handle_extensions
from django.utils.translation import templatize as base_templatize

from optparse import make_option

import fnmatch
import os
import re

template_dirs = [] # TODO: find a more elegant solution
template_exts = []

class Command (BaseI18nCommand):
    help = BaseI18nCommand.help + \
           (' [EDIT] and adds the translatable strings from underscorejs templates to the messages')

    option_list = BaseI18nCommand.option_list + (
        make_option('--template_dirs', '-t', default=[], dest='template_dirs', action='append',
                    help='Specify a directory/directories containing underscorejs template files'),
        make_option('--template_exts', '-x', default=[], dest='template_exts', action='append',
                    help='Specify which extensions contain underscorejs templates'))

    def handle_noargs(self, *args, **options):
        global template_dirs # TODO: find a more elegant solution for this
        global template_exts
        template_dirs = options.get('template_dirs')
        template_exts = handle_extensions(options.get('template_exts'))

        return super(Command, self).handle_noargs(*args, **options)

def get_underi18n_pattern():
    # Should match strings like: <%_ blah blah <%= var %> blah %>
    start_tag = r'<%_'
    end_tag = r'_%>'

    return start_tag + '(.*?)' + end_tag

def update_matches(matches, directory, extension):
    if directory not in matches:
        matches[directory] = []

    for root, dirnames, filenames in os.walk(directory):
        if root not in matches:
            matches[root] = []
        for filename in fnmatch.filter(filenames, '*' + extension):
            if filename not in matches[root]:
                matches[root].append(os.path.join(root, filename))

def find_paths():
    global template_dirs
    global template_exts

    all_paths = []
    all_matches = {}

    for directory in template_dirs:
        for extension in template_exts:
            update_matches(all_matches, directory, extension)

    for dir, paths in all_matches.items():
        all_paths.extend(paths)

    return all_paths

def templatize(src, origin=None):
    pattern = get_underi18n_pattern()
    # Get all the paths that we know about
    paths = [os.path.abspath(path) for path in find_paths()]

    # Hijack the process if the file we're talking about is in one of the
    # finder paths.
    if origin and os.path.abspath(origin) in paths:
        with open(origin) as template_file:

            # Load the template content.
            content = template_file.read()

            # Find all the translatable strings.
            pattern = re.compile(pattern, flags=re.DOTALL)
            strings = set(re.findall(pattern, content))

            def escape(s):
                s = s.replace('\\', '\\\\')
                s = s.replace('"', r'\"')
                return s

            # Build a string that looks like a Python file that's ready to be
            # translated.
            translatable = '\n'.join(['_("""{0}""")'.format(escape(string))
                                      for string in strings])

            return translatable

    # If the file isn't in one of our paths, then delegate to the original
    # method.
    else:
        return base_templatize(src, origin)


# ============================================================================
#
# Monkey-patch django.utils.translation.templatize to use this version.
# Patch it globally so that any other commands that also patch the function
# will inherit this functionality.

import django.utils.translation
django.utils.translation.templatize = templatize