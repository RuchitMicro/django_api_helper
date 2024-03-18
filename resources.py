from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

def create_dynamic_resource(model_class, include=None, exclude=None, lookup_fields=None, import_id_fields=None):
    meta_attrs = {
        'model': model_class,
        'fields': include if include is not None else '__all__',
        'exclude': exclude if exclude is not None else (),
        'import_id_fields': import_id_fields if import_id_fields is not None else ('id',),
        'skip_unchanged': True,
        'report_skipped': False
    }
    
    # Create Meta class dynamically
    Meta = type('Meta', (), meta_attrs)

    # Dynamically create field instances based on lookup_fields
    dynamic_fields = {}
    if lookup_fields:
        for field_name, related_lookup in lookup_fields.items():
            # Assuming all lookup_fields are ForeignKey relations for simplicity
            related_model = model_class._meta.get_field(field_name).remote_field.model
            dynamic_fields[field_name] = fields.Field(
                column_name=field_name,
                attribute=field_name,
                widget=ForeignKeyWidget(related_model, related_lookup)
            )
    
    # Dynamic ModelResource class creation with Meta and dynamically created fields
    resource_attrs = {'Meta': Meta, **dynamic_fields}
    resource_class = type(f'{model_class.__name__}Resource', (resources.ModelResource,), resource_attrs)

    return resource_class



from tenant.models import Metric, MetricValue
class MetricValueResource(resources.ModelResource):
    metric = fields.Field(
        column_name='metric',
        attribute='metric',
        widget=ForeignKeyWidget(Metric, 'name')
    )

    class Meta:
        model = MetricValue
        # Assuming your CSV or Excel file has columns that exactly match the model field names except for 'metric', which matches 'name' of Metric
        fields              = ('metric', 'month', 'year', 'expected_value', 'actual_value')
        import_id_fields    = ('metric', 'month', 'year')  # Use fields that can uniquely identify a record if necessary
        skip_unchanged      = True
        report_skipped      = False