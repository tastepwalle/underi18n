# underi18n.js

`underi18n` is a minimalistic approach to internationalization for javascript-based templates.
It can work in conjuction with other libraries providing the templates, such as [underscore](http://underscorejs.org/#template) or [moustache](https://github.com/janl/mustache.js). It supports variable substitution and AMD loading.

[__Edit:__ To supplement this library, I have bolted on some support for Django and its internationalization framework. In terms of modifications to the original repository, I have only modified the default end delimiter to be `_%>` (originally `%>`, which can clobber some regexes when used with underscore variable tags). The remainder of my additions can be seen in the appended section 'Django Integration' below ~PWALLE 10/8/15]

## Catalogs

`underi18n` uses a simple JSON format for catalogs, following the standard `gettext` format. In the following example,

```javascript
{
    'Developer': 'Προγραμματιστής',
    'Role ${role} does not exist in ${context}': 'Ο ρόλος ${role} δεν υπάρχει στο ${context}'
}
```

we have two translation strings, the second one with two variables, `role` and `context`.
A simple python script is provided to help you convert standard `.mo` files to this JSON format.

## Usage

Create a *MessageFactory* from a json i18n catalog:

```javascript
var t = underi18n.MessageFactory(catalog);
```

You can now translate inline:

```javascript

t('Developer') // returns "Προγραμματιστής"

t('Role ${role} does not exist in ${context}', {role: 'διαχειριστής', context: 'πρόγραμμα'})
// Returns "Ο ρόλος διαχειριστής δεν υπάρχει στο πρόγραμμα"
```

## Templates

Typically variables in templates are indicated with some delimiter. In mustache for instance `{{ var }}` is used whereas `<%= var %>` is default for underscore. We use the same approach to indicate translatable strings. You can specify the delimiters for translatable strings as a RegExp, as well as the left/right delimiters used by your template language of choice in `underi18n.templateSettings`. By default this is following underscore conventions:

```javascript
templateSettings: {
    translate: /<%_([\s\S]+?)_%>/g,
    i18nVarLeftDel: '<%=',
    i18nVarRightDel: '%>'
}
```

[__EDIT:__ Note the above modification to the original library ~PWALLE]

so, `<%_ i18n %>` are set to denote translatable strings and `<%= var %>` is used to denote variables inside a template.

You can translate a template by calling `underi18n.template`, for example using underscore, you can do

```javascript
var templ = _.template(underi18n.template(myTemplate, t));
```

### Example

Given the following catalogs, factories and template for english and greek and assuming an underscore template,
```javascript
var test_en = {
        'files_label': 'Files',
        'num_files': 'There are ${num} files in this folder'
    },

    templ = '<h1><%= title %></h1>' +
            '<label><%_ files_label %></label>' +
            '<span><%_ num_files %></span>',

    t_en = underi18n.MessageFactory(test_en);
    t_el = underi18n.MessageFactory(test_el);

```
the template can by constructed by,
```javascript
var toRender = _.template(underi18n.template(templ, t_en));
toRender({title: 'Summary', num: 3});
```
would yield

```html
<h1>Summary</h1>
<label>Files</label>
<span>There are 3 files in this folder</span>
```

## AMD loading

underi18n will register as an anonymous module if you use [requireJS](http://requirejs.org/).

## Django Integration [PWALLE]

The Django web framework provides some nice tools of its own for i18n internationalization, but I've brewed up quite a few headaches working with the Javascript components of these tools. I've built a process for integrating the original underi18n library with Django internationalization using two additional custom commands `make_messages` and `compile_template_messages`. These commands 1) parse underscorejs template files and add text marked for translation to the standard `django.po` file(s), and 2) build the underi18n translation catalog(s).

### Usage

Generate the .mo file(s) needed for Django internationalization *and* the underi18n catalog(s):

```
python manage.py make_messages -d <comma-sep template dirs> -x <comma-sep template exts> [other args]
python manage.py compilemessages
python manage.py compile_template_mesages [-d <translations directory default=static/translations>]
```

Usage within Javascript source is the same as original library, though _please note the change to the default end delimiter._
