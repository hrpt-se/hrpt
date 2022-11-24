import datetime
from collections import namedtuple
import json
import itertools
import sys

from django.core import serializers
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder

from apps.pollster import models

ModelKey = namedtuple('ModelKey', ['model', 'pk'])

EntityDef = namedtuple('EntityDef', ['json_key', 'fkeys', 'm2ms'])

FKeyDef = namedtuple('FKeyDef', ['field_name', 'model'])

# We could use FKeyDef where we use this, but it becomes clearer this way
M2MDef = namedtuple('M2MDef', ['field_name', 'model'])

# TODO: define only the survey id and the models. The rest can easily be done using
# the inspect module.
IMPORT_ENTITIES_DEFINITIONS = [
    EntityDef(
        "survey_questions",
        ["survey", "data_type", FKeyDef("open_option_data_type", 'questiondatatype')],
        []
    ),
    EntityDef(
        "survey_translations",
        ["survey"],
        []
    ),
    EntityDef(
        "rows",
        ["question"],
        []
    ),
    EntityDef(
        "columns",
        ["question"],
        []
    ),
    EntityDef(
        'options',
        [
            "question",
            FKeyDef("virtual_type", "virtualoptiontype")],  # TODO: possibly row and column, check this
        []
    ),
    EntityDef(
        "rules",
        [
            FKeyDef("rule_type", "ruletype"),
            FKeyDef("subject_question", "question"),
            FKeyDef("object_question", "question"),
        ],
        [
            M2MDef("object_options", "option"),
            M2MDef("subject_options", "option")
        ]
    ),
    EntityDef(
        "translation_questions",
        [
            "question",
            FKeyDef("translation", "translationsurvey")
        ],
        []
    ),
    EntityDef(
        "translation_column",
        [
            FKeyDef("translation", "translationsurvey"),
            FKeyDef("column", "questioncolumn")
        ],
        []
    ),
    EntityDef(
        "translation_row",
        [
            FKeyDef("translation", "translationsurvey"),
            FKeyDef("row", "questionrow")
        ],
        []
    ),
    EntityDef(
        "translation_option",
        [
            "option",
            FKeyDef("translation", "translationsurvey")
        ],
        []
    ),

    # TODO. go throught tables and check if any missing
]


def create_survey_from_json(json_string):
    if isinstance(json_string, bytes):
        json_string = json_string.decode('utf-8')
    data_from_json = json.loads(json_string)

    # we use this to map old keys present in the exported file, to new keys obtained on insert
    keys_save = {}

    # the main survey object needs to be saved separately because it is a special case
    # we need to prevent survey shortname colisions
    keys_save = _save_serialized_survey(data_from_json['survey'][0], keys_save)

    # this is just so we can define relationships both with a string in the simple case,
    # or with a FKeyDef in the case where the target model name does not match the attribute name
    normalized_import_defs = _normalize_fkey_definitions(IMPORT_ENTITIES_DEFINITIONS)

    for definition in normalized_import_defs:
        for serialized_instance in data_from_json[definition.json_key]:
            keys_save = _save_model_from_serialized_data(serialized_instance, definition, keys_save)


def survey_to_json(survey):
    survey.group = None  # SurveyGroups can't be exported/imported
    survey_questions = survey.question_set.all()
    survey_translations = survey.translationsurvey_set.all()

    all_options_nested = [question.option_set.all() for question in survey_questions]
    all_transl_questions_nested = [trasl_survey.translationquestion_set.all() for trasl_survey in survey_translations]
    all_transl_columns_nested = [trasl_survey.translationquestioncolumn_set.all() for trasl_survey in
                                 survey_translations]
    all_transl_rows_nested = [translationsurvey.translationquestionrow_set.all() for translationsurvey in
                              survey_translations]
    all_transl_options_nested = [translationsurvey.translationoption_set.all() for translationsurvey in
                                 survey_translations]
    all_rules_nested = [q.subject_of_rules.all() for q in survey_questions]
    all_rows_nested = [q.rows for q in survey_questions]
    all_columns_nested = [q.columns for q in survey_questions]

    all_options = _flaten(all_options_nested)
    all_transl_questions = _flaten(all_transl_questions_nested)
    all_transl_columns = _flaten(all_transl_columns_nested)
    all_transl_rows = _flaten(all_transl_rows_nested)
    all_transl_options = _flaten(all_transl_options_nested)
    all_rules = _flaten(all_rules_nested)
    all_rows = _flaten(all_rows_nested)
    all_columns = _flaten(all_columns_nested)

    # note that IMPORT_ENTITIES_DEFINITIONS must match this... obviously.
    serialize_this = {
        'survey': serializers.serialize("python", [survey], ),
        'survey_questions': serializers.serialize("python", survey_questions),
        'survey_translations': serializers.serialize("python", survey_translations),
        "rows": serializers.serialize("python", all_rows),
        "columns": serializers.serialize("python", all_columns),
        'options': serializers.serialize("python", all_options),
        "rules": serializers.serialize("python", all_rules),
        "translation_questions": serializers.serialize("python", all_transl_questions),
        "translation_column": serializers.serialize("python", all_transl_columns),
        "translation_row": serializers.serialize("python", all_transl_rows),
        "translation_option": serializers.serialize("python", all_transl_options),
    }

    return json.dumps(serialize_this, indent=2, cls=DjangoJSONEncoder)


def _normalize_fkey_definitions(import_entities_definition):
    normalized_entity_definitions = []
    for ed in import_entities_definition:
        normalized_fkeys = []
        for fk in ed.fkeys:
            if isinstance(fk, str):
                normalized_fkeys.append(FKeyDef(fk, fk))
            else:
                normalized_fkeys.append(fk)
        # not suported for many to many relations, could be easily added if needed
        normalized_ed = EntityDef(ed.json_key, normalized_fkeys, ed.m2ms)
        normalized_entity_definitions.append(normalized_ed)
    # TODO: convert all model names to lowercase.
    return normalized_entity_definitions


def _save_serialized_survey(input_survey_object, keys_save):
    input_survey_object['fields']['shortname'] = _change_shortname_if_invalid(input_survey_object['fields']['shortname'])
    new_survey = models.Survey(**input_survey_object['fields'])
    new_survey.save()
    key = ModelKey(model="pollster.survey", pk=input_survey_object['pk'])
    keys_save[key] = new_survey.pk
    return keys_save


def _change_shortname_if_invalid(shortname):
    # Change a given shortname if it is too long by truncating anything above max_length
    max_len = models.Survey._meta.get_field("shortname").max_length
    shortname = shortname[:max_len]

    if not models.Survey.objects.filter(shortname=shortname).exists():
        return shortname

    # Retuan a 20 character shortname ending with the current timestamp,
    # the shortname will be truncated to fit the timestamp.
    ts_string = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    return "{}_{}".format(shortname[:20-len(ts_string) - 1], ts_string)


def _prepare_fkey_fields(serialized_instance, fkey_defs, keys_save):
    for key_def in fkey_defs:
        lookup_key = ModelKey("pollster." + key_def.model, serialized_instance["fields"][key_def.field_name])
        if lookup_key in keys_save:
            value = keys_save[lookup_key]
        else:
            value = serialized_instance["fields"][key_def.field_name]
        new_key = key_def.field_name + "_id"
        serialized_instance["fields"][new_key] = value
        del serialized_instance["fields"][key_def.field_name]
    return serialized_instance


def _prepare_m2m_fields(serialized_instance, m2m_defs, keys_save):
    """
    we move the important data from the 'fields', up to the serialized instance root
    This way, all the fields in fields can be passed to the model constructor as kwargs
    and the many to many relationships are inserted after the instance is saved,
    which is actually a requirement imposed by django.
    """
    serialized_instance['m2m_fields'] = {}
    for m2m_def in m2m_defs:
        translated_relative_modelkeys = []
        for other_entity_id in serialized_instance['fields'][m2m_def.field_name]:
            lookup_key = ModelKey("pollster." + m2m_def.model, other_entity_id)
            if lookup_key in keys_save:
                # in this case we have created this object during the import, use the id of the created instance
                # (i.e. relative to this import)
                model_key_to_insert = ModelKey("pollster." + m2m_def.model, keys_save[lookup_key])
                translated_relative_modelkeys.append(model_key_to_insert)
            else:
                # nothing we have created durint this import, reference something that exists on the database
                # (i.e. absolute reference to id on the database)
                translated_relative_modelkeys.append(lookup_key)

        serialized_instance['m2m_fields'][m2m_def.field_name] = translated_relative_modelkeys
        del serialized_instance['fields'][m2m_def.field_name]
    return serialized_instance


def _save_m2m_relationships(instance, serialized_instance, entity_definition):
    for m2mdef in entity_definition.m2ms:
        attr = getattr(instance, m2mdef.field_name)
        full_model_name = "pollster." + m2mdef.model
        TargetModelClass = apps.get_model(*full_model_name.split('.', 1))
        models_instances_to_add = []
        for model_key_to_insert in serialized_instance["m2m_fields"][m2mdef.field_name]:
            models_instances_to_add.append(TargetModelClass.objects.get(pk=model_key_to_insert.pk))
        attr.add(*models_instances_to_add)


def _save_model_from_serialized_data(serialized_instance, entity_definition, keys_save):
    ModelClass = apps.get_model(*serialized_instance["model"].split('.', 1))
    serialized_instance = _prepare_m2m_fields(serialized_instance, entity_definition.m2ms, keys_save)
    serialized_instance = _prepare_fkey_fields(serialized_instance, entity_definition.fkeys, keys_save)
    new_instance = ModelClass(**serialized_instance["fields"])
    new_instance.save()
    _save_m2m_relationships(new_instance, serialized_instance, entity_definition)
    new_instance.save()
    key = ModelKey(serialized_instance['model'], serialized_instance['pk'])
    keys_save[key] = new_instance.id
    return keys_save


def _flaten(list2d):
    return list(itertools.chain.from_iterable(list2d))


def specialPrint(msg):
    print(msg, file=sys.stderr)
