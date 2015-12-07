#!/bin/bash

export PYTHONPATH=".:$PYTHONPATH"
export DJANGO_SETTINGS_MODULE="test_settings"

usage() {
    echo "USAGE: $0 [command]"
    echo "  test - run the waffle tests"
    echo "  shell - open the Django shell"
    echo "  schema - create a schema migration for any model changes"
    exit 1
}

CMD="$1"
shift

case "$CMD" in
    "test" )
        django-admin.py test waff $@ ;;
    "lint" )
        flake8 waff $@ ;;
    "shell" )
        django-admin.py shell $@ ;;
    "schema" )
        django-admin.py schemamigration waff --auto $@ ;;
    "makemigrations" )
        django-admin.py makemigrations waff $@ ;;
    * )
        usage ;;
esac
