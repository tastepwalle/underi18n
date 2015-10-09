"""
This command extends Django's builtin command compilemessages with a monkey patch that handles
underi18n template files. In addition to the standard compilation of .po files to .mo, this command
also processes the resultant .mo files using underi18n's convert.py and generates translation catalogs
for each locale.

Takes a parameter -o <output directory for translation catalogs>, which defaults to the corresponding
directory in settings.LOCALE_PATHS

Code inspired by and borrowed from Mjumbe Poe's django-mustachejs GitHub project
(https://github.com/mjumbewu/django-mustachejs)

@author: Paul Elliott (PE)
@date: 10/8/2015
"""

from django.core.management.base import CommandError
from django.core.management.commands.compilemessages import Command as BaseI18nCommand

from django.conf import settings

from optparse import make_option

import os

# underi18n convert.py requirements
import gettext
import json


class Command (BaseI18nCommand):
    help = BaseI18nCommand.help + ' [EDIT] and converts .mo files to underi18n translation catalogs'

    option_list = BaseI18nCommand.option_list + (
        make_option('--output-dir', '-o', default=None, dest='output_dir', action='store',
                    help='Specify a directory/directories containing underscorejs template files'),)

    def handle(self, **options):
        output_dir = options.get('output_dir')
        self.output_dir = output_dir if output_dir else settings.LOCALE_PATHS[0]

        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except:
                raise CommandError("Could not create output directory: %s\r\nCheck that you have write permission"
                                   % self.output_dir)

        super(Command, self).handle(**options)

    def compile_messages(self, locations):
        """
        [From Django compilemessages.py]

        Locations is a list of tuples: [(directory, file), ...]
        """
        super(Command, self).compile_messages(locations)
        for i, (dirpath, f) in enumerate(locations):
            fname = os.path.splitext(f)[0]

            mo_path = os.path.join(dirpath, fname + '.mo')
            if not os.path.exists(mo_path):
                raise CommandError("Could not find .mo file %s in %s" % (f, dirpath))

            split_locale_path = dirpath.split('/')
            catalog_base_path = os.path.join(self.output_dir, split_locale_path[-2], split_locale_path[-1])
            if not os.path.exists(catalog_base_path):
                try:
                    os.makedirs(catalog_base_path)
                except:
                    raise CommandError("Could not create output directory: %s\r\nCheck that you have write permission"
                                       % self.output_dir)

            catalog_path = os.path.join(catalog_base_path, fname + '.json')

            if self.verbosity > 0:
                self.stdout.write('[underi18n] converting %s > %s' % (mo_path, catalog_path))

            convert(mo_path, catalog_path)


"""
underi18n convert.py (modified slightly)
"""


def convert(inputfile, outputfile):
    with open(inputfile) as ifile:
        catalog = gettext.GNUTranslations(ifile)._catalog

    del catalog['']
    output = json.dumps(catalog)
    with open(outputfile, 'w') as ofile:
        ofile.write(output)
