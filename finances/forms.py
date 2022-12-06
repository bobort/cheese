import csv

from django import forms

# used to map csv headers to location fields
from django.core.exceptions import ValidationError

from finances.models import ApprovedTransaction, BankTransaction

HEADERS = {
    'details': {'field': 'details', 'required': True},
    'posting date': {'field': 'date', 'required': True},
    'description': {'field': 'description', 'required': True},
    'amount': {'field': 'amount', 'required': True},
    'type': {'field': 'type', 'required': True},
}


def get_csv(document):
    # check file valid csv format
    try:
        document.seek(0, 0)
        dialect = csv.Sniffer().sniff(document.readline().decode())
        document.seek(0, 0)
    except csv.Error as e:
        raise ValidationError(f"Not a valid CSV file: {e}")
    return csv.reader(document.read().decode().splitlines(), dialect)


def get_csv_headers(document, reader=None):
    if reader is None:
        reader = get_csv(document)
    # yield reader
    return [header_name.lower() for header_name in next(reader) if header_name]


def get_required_headers():
    return [header_name.lower() for header_name, values in HEADERS.items() if values['required']]


def is_csv(document):
    return bool(get_csv(document))


def check_csv_headers(document):
    reader = get_csv(document)
    required_headers = get_required_headers()
    csv_headers = get_csv_headers(document, reader)

    missing_headers = set(required_headers) - set(csv_headers)
    if missing_headers:
        missing_headers_str = ', '.join(missing_headers)
        raise ValidationError(f"Missing headers: {missing_headers_str}")
    return bool(csv_headers)


def check_required_data(document):
    reader = get_csv(document)
    csv_headers = get_csv_headers(document, reader)
    required_headers = get_required_headers()
    for row_number, row in enumerate(reader):
        # ignore blank rows
        if not ''.join(str(x) for x in row):
            continue
        for col_number, cell_value in enumerate(row):
            # if indexerror, probably an empty cell past the headers col count
            try:
                csv_headers[col_number]
            except IndexError:
                continue
            if csv_headers[col_number] in required_headers:
                if not cell_value:
                    raise ValidationError(f"Missing required value %s for row %s" %
                                          (csv_headers[col_number], row_number + 1))
    return True


class UploadBankTransaction(forms.Form):
    template_name = "upload.html"
    file = forms.FileField(validators=[is_csv, check_csv_headers, check_required_data])


class ApproveTransactionForm(forms.ModelForm):
    class Meta:
        model = ApprovedTransaction
        fields = ('category', 'notes', 'contact', 'document', 'contact_order')


