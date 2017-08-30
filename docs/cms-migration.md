# HRPT CMS Content Migration

This document outlines how to copy content from one instance of the HRPT system
to another. Note that this process only works between instances which are 
running similar, recent versions of Django CMS. It will not work for legacy 
versions of HRPT.

## Extracting Existing Content

Existing content can be migrated using Django's `dumpdata` command. Begin by 
logging in to the instance that hosts the content ready for extraction and 
issue the command below. This will generate a file with all CMS data on the 
instance named `cms_content.json`.

```bash
python manage.py dumpdata --natural-primary \
                          --natural-foreign \
                          cms \
                          djangocms_file \
                          djangocms_link \
                          djangocms_text_ckeditor \
                          djangocms_picture \
                          easy_thumbnails \
                          filer > cms_content.json
```

## Inserting Extracted Content

Transfer the generated file with the CMS content (`cms_content.json`) that was
extracted in the previous step to the instance that the content should be 
copied to. Then use the `loaddata` command to insert the data into the new 
system.

```bash
python manage.py loaddata cms_content.json
```